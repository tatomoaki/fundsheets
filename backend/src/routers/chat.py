import itertools
from uuid import UUID

import anthropic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.dependencies import get_db_session
from src.ingestion.pipeline import ChunkEmbedder
from src.services.asset_allocation_service import AssetAllocationService
from src.services.chunk_service import ChunkService
from src.services.fee_service import FeeService
from src.services.holdings_service import HoldingsService
from src.services.performance_service import PerformanceService
from src.storage.repositories import (
    AnnualReturnsRepository,
    AssetAllocationRepository,
    FeeRepository,
    FundChunkRepository,
    FundRepository,
    HoldingsRepository,
    PerformanceRepository,
)

router = APIRouter(prefix="/chat", tags=["chat"])

_embedder = ChunkEmbedder()
_llm = anthropic.Anthropic()

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOOL_ROUNDS = 5

_SYSTEM_PROMPT = """\
You are a helpful assistant answering questions about a single South African \
collective investment scheme fund factsheet, named "{fund_name}". Use the \
provided tools to look up exact figures — holdings, fees, performance, asset \
allocation — rather than guessing at numbers. Use search_factsheet_text for \
narrative questions about strategy, objectives, risk, or disclaimers. Cite \
figures precisely as returned by the tools. If a tool reports no data, say the \
information isn't available rather than guessing.
"""

_TOOLS = [
    {
        "name": "search_factsheet_text",
        "description": "Semantic search over this fund's factsheet text, for narrative content such as strategy, objectives, risk, or disclaimers.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_holdings",
        "description": "Get this fund's holdings, ordered by weight descending (largest first).",
        "input_schema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "Max number of holdings to return, largest first."}},
        },
    },
    {
        "name": "get_fees",
        "description": "Get this fund's latest fee breakdown (TER, transaction costs, advice/manager fees).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_performance",
        "description": "Get this fund's latest performance records (1yr, 3yrs, 5yrs, 7yrs, since_launch) vs benchmark.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_asset_allocation",
        "description": "Get this fund's latest asset allocation breakdown by asset class.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    fund_id: UUID
    message: str
    history: list[ChatMessage] = []


class Source(BaseModel):
    fund_name: str
    page_no: int | None = None


class ChatResponse(BaseModel):
    reply: str
    sources: list[Source] = []


def _format_holdings(rows, limit: int | None) -> str:
    if not rows:
        return "No holdings data available."
    if limit:
        rows = rows[:limit]
    return "\n".join(f"{i}. {r.instrument_name} — {r.weight_pct}%" for i, r in enumerate(rows, start=1))


def _format_fees(fee) -> str:
    if fee is None:
        return "No fee data available."
    return "\n".join([
        f"TER: {fee.ter}%",
        f"Transaction cost: {fee.transaction_cost_pct}%",
        f"Total investment charge: {fee.total_investment_charge_pct}%",
        f"Manager annual fee: {fee.manager_annual_fee_pct}%",
        f"Advice annual fee (max): {fee.advice_annual_fee_max_pct}%",
        f"Manager initial fee: {fee.manager_initial_fee_pct}%",
        f"Advice initial fee (max): {fee.advice_initial_fee_max_pct}%",
        f"Effective date: {fee.effective_date}",
    ])


def _format_performance(rows) -> str:
    if not rows:
        return "No performance data available."
    return "\n".join(
        f"{r.period}: fund {r.fund_return_pct}% vs benchmark {r.benchmark_return_pct}% "
        f"(tracking difference {r.tracking_difference_pct}%)"
        for r in rows
    )


def _format_allocations(rows) -> str:
    if not rows:
        return "No asset allocation data available."
    return "\n".join(f"{r.asset_class}: {r.weight_pct}%" for r in rows)


class _Toolbox:
    """Fund-scoped tool implementations backing the chat tool-use loop."""

    def __init__(self, fund, session: Session):
        self._fund = fund
        self._chunks = ChunkService(FundChunkRepository(session))
        fund_repo = FundRepository(session)
        self._holdings = HoldingsService(HoldingsRepository(session), fund_repo)
        self._fees = FeeService(FeeRepository(session), fund_repo)
        self._performance = PerformanceService(
            PerformanceRepository(session), AnnualReturnsRepository(session), fund_repo
        )
        self._allocations = AssetAllocationService(AssetAllocationRepository(session), fund_repo)

    def run(self, name: str, tool_input: dict) -> tuple[str, list[Source]]:
        if name == "search_factsheet_text":
            return self._search_factsheet_text(tool_input["query"])
        if name == "get_holdings":
            rows = self._holdings.get_latest_holdings(self._fund.id)
            return _format_holdings(rows, tool_input.get("limit")), []
        if name == "get_fees":
            return _format_fees(self._fees.get_latest_fees(self._fund.id)), []
        if name == "get_performance":
            return _format_performance(self._performance.get_latest_performance(self._fund.id)), []
        if name == "get_asset_allocation":
            return _format_allocations(self._allocations.get_latest_allocations(self._fund.id)), []
        return f"Unknown tool: {name}", []

    def _search_factsheet_text(self, query: str) -> tuple[str, list[Source]]:
        embedding = _embedder.embed_query(query)
        chunks = self._chunks.find_similar(embedding, limit=5, fund_id=self._fund.id)
        if not chunks:
            return "No matching text found in this fund's factsheet.", []
        text = "\n\n---\n\n".join(f"[page {c.page_no}]\n{c.text}" for c in chunks)
        sources = [Source(fund_name=self._fund.name, page_no=c.page_no) for c in chunks]
        return text, sources


def _fund_repo(session: Session = Depends(get_db_session)) -> FundRepository:
    return FundRepository(session)


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    session: Session = Depends(get_db_session),
    fund_repo: FundRepository = Depends(_fund_repo),
):
    fund = fund_repo.get_by_id(payload.fund_id)
    if fund is None:
        raise HTTPException(status_code=404, detail="Fund not found")

    toolbox = _Toolbox(fund, session)
    

    # Claude requires messages to start with role "user"; ChatPanel's history
    # can begin with its seeded assistant greeting, so drop any leading turns
    # before the first user message.
    prior_turns = itertools.dropwhile(lambda m: m.role != "user", payload.history)
    messages = [{"role": m.role, "content": m.content} for m in prior_turns]
    messages.append({"role": "user", "content": payload.message})

    system_prompt = _SYSTEM_PROMPT.format(fund_name=fund.name)
    sources: list[Source] = []

    for _ in range(_MAX_TOOL_ROUNDS):
        response = _llm.messages.create(
            model=_MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=_TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            reply = next(b.text for b in response.content if b.type == "text")
            return ChatResponse(reply=reply, sources=sources)

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result_text, block_sources = toolbox.run(block.name, block.input)
            sources.extend(block_sources)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_text,
            })
        messages.append({"role": "user", "content": tool_results})

    return ChatResponse(reply="Sorry, I wasn't able to complete that request.", sources=sources)
