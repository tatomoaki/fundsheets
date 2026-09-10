import hashlib
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

import anthropic
import voyageai
from docling.chunking import HybridChunker
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from pydantic import BaseModel

load_dotenv()


class ExtractedFund(BaseModel):
    fund_name: Optional[str] = None
    fund_manager: Optional[str] = None
    risk_profile: Optional[str] = None
    asisa_classification: Optional[str] = None
    benchmark: Optional[str] = None
    portfolio_launch_date: Optional[str] = None  # ISO 8601
    portfolio_size: Optional[str] = None          # e.g. "R 10.58 billion"
    as_of_date: Optional[str] = None              # ISO 8601


class ExtractedHolding(BaseModel):
    instrument_name: str
    weight: float  # percentage points, e.g. 5.08


class ExtractedFees(BaseModel):
    ter: Optional[float] = None
    transaction_cost_pct: Optional[float] = None
    total_investment_charge_pct: Optional[float] = None
    manager_annual_fee_pct: Optional[float] = None
    advice_annual_fee_max_pct: Optional[float] = None
    manager_initial_fee_pct: Optional[float] = None
    advice_initial_fee_max_pct: Optional[float] = None
    effective_date: Optional[str] = None  # ISO 8601


class ExtractedPerformanceRecord(BaseModel):
    period: str  # "1yr" | "3yrs" | "5yrs" | "7yrs" | "since_launch"
    fund_return_pct: Optional[float] = None
    benchmark_return_pct: Optional[float] = None


class ExtractedAssetAllocation(BaseModel):
    asset_class: str
    weight: float  # percentage points


class DocumentChunk(BaseModel):
    text: str
    headings: List[str] = []
    page_no: Optional[int] = None
    embedding: Optional[List[float]] = None


class _LLMPayload(BaseModel):
    """Tool input schema passed to Claude. Populated entirely by the LLM."""
    fund: ExtractedFund
    holdings: List[ExtractedHolding] = []
    fees: Optional[ExtractedFees] = None
    performance: List[ExtractedPerformanceRecord] = []
    asset_allocations: List[ExtractedAssetAllocation] = []


class FundData(BaseModel):
    """Pipeline output."""
    fund_hash: Optional[str] = None
    fund: Optional[ExtractedFund] = None
    holdings: List[ExtractedHolding] = []
    fees: Optional[ExtractedFees] = None
    performance: List[ExtractedPerformanceRecord] = []
    asset_allocations: List[ExtractedAssetAllocation] = []
    chunks: List[DocumentChunk] = []


# --- Stage 1: PDF → DoclingDocument ------------------------------------------

@dataclass
class ConversionResult:
    markdown: str
    doc: object  # DoclingDocument
    fund_hash: str


class DisclosureConverter:

    def __init__(self, do_ocr: bool = False, verbose: bool = True):
        self._do_ocr = do_ocr
        self._verbose = verbose
        self._converter: Optional[DocumentConverter] = None

    def _get_converter(self) -> DocumentConverter:
        if self._converter is None:
            if self._verbose:
                print("Loading docling models...")
            options = PdfPipelineOptions()
            options.do_ocr = self._do_ocr
            options.do_table_structure = True
            self._converter = DocumentConverter(
                format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
            )
        return self._converter

    def run(self, pdf_path: str) -> ConversionResult:
        pdf_path = str(pdf_path)
        fund_hash = self._hash_file(pdf_path)
        doc = self._get_converter().convert(pdf_path).document
        markdown = doc.export_to_markdown()
        if not markdown.strip() and not self._do_ocr and self._verbose:
            print(
                f"Warning: no text extracted from {pdf_path}. "
                "The PDF may be image-based — rerun with do_ocr=True."
            )
        return ConversionResult(markdown=markdown, doc=doc, fund_hash=fund_hash)

    @staticmethod
    def _hash_file(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65_536), b""):
                h.update(chunk)
        return h.hexdigest()


# --- Stage 2a: Chunk document for RAG ----------------------------------------

class DisclosureChunker:

    def __init__(self):
        self._chunker = HybridChunker()

    def chunk(self, doc) -> List[DocumentChunk]:
        results = []
        for chunk in self._chunker.chunk(doc):
            page_no = None
            if chunk.meta.doc_items:
                prov = chunk.meta.doc_items[0].prov
                if prov:
                    page_no = prov[0].page_no

            results.append(DocumentChunk(
                text=chunk.text,
                headings=chunk.meta.headings or [],
                page_no=page_no,
            ))
        return results


# --- Stage 2b: Chunk embedding ------------------------------------------------

class ChunkEmbedder:
    def __init__(self, model: str = "voyage-finance-2"):
        self._client = voyageai.Client()
        self._model = model

    def embed(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        if not chunks:
            return chunks

        vectors: List[List[float]] = []
        batch_size = voyageai.VOYAGE_EMBED_BATCH_SIZE
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            result = self._client.embed(
                texts=[c.text for c in batch],
                model=self._model,
                input_type="document",
            )
            vectors.extend(result.embeddings)

        return [
            chunk.model_copy(update={"embedding": vector})
            for chunk, vector in zip(chunks, vectors)
        ]

    def embed_query(self, text: str) -> List[float]:
        result = self._client.embed(texts=[text], model=self._model, input_type="query")
        return result.embeddings[0]


# --- Stage 2c: LLM structured extraction -------------------------------------

_SYSTEM_PROMPT = """\
You are an expert financial document analyst specialising in South African collective \
investment scheme (CIS) fund factsheets compliant with ASISA standards.

Extract all available structured data from the provided factsheet and call extract_fund_data.

Rules:
- All dates must be ISO 8601 strings (YYYY-MM-DD).
- All weights, fees, and return values must be percentage points as plain floats \
  (e.g. 5.08, not 0.0508). Strip any % signs.
- If the factsheet contains multiple share classes (e.g. Class A, Class B1), \
  extract fees and performance for Class A only.
- For performance, extract 1yr, 3yrs, 5yrs, 7yrs, and since_launch periods where present.
- portfolio_size should be the NAV as a human-readable string (e.g. "R 10.58 billion").
- asisa_classification is the ASISA category (e.g. "Global - Equity - General").
- Use null for any field not present in the document. Never fabricate values.
"""


class DisclosureLLM:
    _TOOL_NAME = "extract_fund_data"

    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        self._client = anthropic.Anthropic()
        self._model = model
        self._tool = {
            "name": self._TOOL_NAME,
            "description": "Structured extraction of all fields from a fund factsheet.",
            "input_schema": _LLMPayload.model_json_schema(),
        }

    def extract(self, markdown: str) -> _LLMPayload:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            cache_control={"type": "ephemeral"},
            tools=[self._tool],
            tool_choice={"type": "tool", "name": self._TOOL_NAME},
            messages=[{
                "role": "user",
                "content": f"Extract all fund data from this factsheet:\n\n{markdown}",
            }],
        )
        tool_block = next(b for b in response.content if b.type == "tool_use")
        return _LLMPayload.model_validate(tool_block.input)


# --- Stage 3: Orchestrator ---------------------------------------------------

class DisclosurePipeline:

    def __init__(
        self,
        do_ocr: bool = False,
        verbose: bool = True,
        model: str = "claude-haiku-4-5-20251001",
        embedding_model: str = "voyage-finance-2",
    ):
        self._converter = DisclosureConverter(do_ocr=do_ocr, verbose=verbose)
        self._chunker = DisclosureChunker()
        self._embedder = ChunkEmbedder(model=embedding_model)
        self._llm = DisclosureLLM(model=model)

    def run(self, pdf_path: str) -> FundData:
        result = self._converter.run(pdf_path)
        payload = self._llm.extract(result.markdown)
        chunks = self._embedder.embed(self._chunker.chunk(result.doc))
        return FundData(
            fund_hash=result.fund_hash,
            chunks=chunks,
            **payload.model_dump(),
        )

