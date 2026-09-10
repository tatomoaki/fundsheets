import hashlib
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from src.ingestion.pipeline import FundData
from src.models.asset_allocation import AssetAllocation
from src.models.holdings import Holding
from src.services.asset_allocation_service import AssetAllocationService
from src.services.fee_service import FeeService
from src.services.fund_service import FundService
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
from src.storage.tables import FundTable


def _dec(value: Optional[float]) -> Optional[Decimal]:
    return None if value is None else Decimal(str(value))


def _parse_date(value: Optional[str]) -> Optional[date]:
    return date.fromisoformat(value) if value else None


def persist_fund_data(session: Session, data: FundData) -> FundTable:
    """Persist one pipeline run's output. Caller owns the session/transaction."""
    if data.fund is None or not data.fund.fund_name:
        raise ValueError("FundData.fund.fund_name is required to persist")

    fund_repo = FundRepository(session)
    fund_service = FundService(fund_repo)
    fee_service = FeeService(FeeRepository(session), fund_repo)
    holdings_service = HoldingsService(HoldingsRepository(session), fund_repo)
    allocation_service = AssetAllocationService(AssetAllocationRepository(session), fund_repo)
    performance_service = PerformanceService(
        PerformanceRepository(session), AnnualReturnsRepository(session), fund_repo
    )
    chunk_repo = FundChunkRepository(session)

    fund_name = data.fund.fund_name
    fund = fund_service.create_fund(
        name=fund_name,
        manager=data.fund.fund_manager,
        risk_profile=data.fund.risk_profile,
        asisa_classification=data.fund.asisa_classification,
        benchmark=data.fund.benchmark,
        portfolio_launch_date=data.fund.portfolio_launch_date,
        portfolio_size=data.fund.portfolio_size,
        as_of_date=data.fund.as_of_date,
        fund_hash=data.fund_hash,
    )
    as_of_date = fund.as_of_date or date.today()

    if data.holdings:
        holdings = [
            Holding(
                fund_id=str(fund.id),
                instrument_name=h.instrument_name,
                weight=_dec(h.weight),
                as_of_date=as_of_date,
            )
            for h in data.holdings
        ]
        holdings_service.record_holdings(fund_name=fund_name, holdings=holdings)

    if data.fees is not None and data.fees.effective_date:
        fee_service.record_fees(
            fund_name=fund_name,
            advice_initial_fee_max_pct=_dec(data.fees.advice_initial_fee_max_pct),
            manager_initial_fee_pct=_dec(data.fees.manager_initial_fee_pct),
            advice_annual_fee_max_pct=_dec(data.fees.advice_annual_fee_max_pct),
            manager_annual_fee_pct=_dec(data.fees.manager_annual_fee_pct),
            ter=_dec(data.fees.ter),
            transaction_cost_pct=_dec(data.fees.transaction_cost_pct),
            total_investment_charge_pct=_dec(data.fees.total_investment_charge_pct),
            effective_date=_parse_date(data.fees.effective_date),
            as_of_date=as_of_date,
        )

    if data.asset_allocations:
        allocations = [
            AssetAllocation(
                fund_id=str(fund.id),
                asset_class=a.asset_class,
                weight=_dec(a.weight),
                as_of_date=as_of_date,
            )
            for a in data.asset_allocations
        ]
        allocation_service.record_allocations(fund_name=fund_name, allocations=allocations)

    if data.performance:
        records = [
            {
                "period": p.period,
                "fund_return_pct": _dec(p.fund_return_pct),
                "benchmark_return_pct": _dec(p.benchmark_return_pct),
            }
            for p in data.performance
        ]
        performance_service.record_performance(fund_name=fund_name, records=records, as_of_date=as_of_date)

    if data.chunks:
        chunk_repo.delete_by_fund(fund.id)
        chunk_repo.bulk_create(
            fund_id=fund.id,
            rows=[
                {
                    "text": c.text,
                    "headings": c.headings or None,
                    "page_no": c.page_no,
                    "content_hash": hashlib.sha256(c.text.encode()).hexdigest(),
                    "embedding": c.embedding,
                }
                for c in data.chunks
            ],
        )

    return fund
