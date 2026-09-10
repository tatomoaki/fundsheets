from datetime import date
from decimal import Decimal
from uuid import UUID

from src.storage.repositories import AnnualReturnsRepository, FundRepository, PerformanceRepository
from src.storage.tables import AnnualReturnsTable, PerformanceRecordTable


class PerformanceService:
    def __init__(
        self,
        performance_repo: PerformanceRepository,
        annual_returns_repo: AnnualReturnsRepository,
        fund_repo: FundRepository,
    ):
        self._performance_repo = performance_repo
        self._annual_returns_repo = annual_returns_repo
        self._fund_repo = fund_repo

    def record_performance(
        self,
        *,
        fund_name: str,
        records: list[dict],
        as_of_date: date,
    ) -> list[PerformanceRecordTable]:
        fund = self._fund_repo.get_by_fund_name(fund_name)
        if fund is None:
            raise ValueError(f"Fund '{fund_name}' not found")

        for r in records:
            r["as_of_date"] = as_of_date
            fund_pct = r.get("fund_return_pct")
            benchmark_pct = r.get("benchmark_return_pct")
            if fund_pct is not None and benchmark_pct is not None:
                r["tracking_difference_pct"] = Decimal(str(fund_pct)) - Decimal(str(benchmark_pct))

        rows = self._performance_repo.bulk_create(fund_id=fund.id, records=records)
        self._performance_repo.session.commit()
        return rows

    def get_latest_performance(self, fund_id: UUID) -> list[PerformanceRecordTable]:
        latest_date = self._performance_repo.get_latest_date_by_fund(fund_id)
        if latest_date is None:
            return []
        return self._performance_repo.list_by_fund_and_date(fund_id, latest_date)

    def record_annual_returns(
        self,
        *,
        fund_name: str,
        highest_pct: Decimal | None,
        lowest_pct: Decimal | None,
        as_of_date: date,
    ) -> AnnualReturnsTable:
        fund = self._fund_repo.get_by_fund_name(fund_name)
        if fund is None:
            raise ValueError(f"Fund '{fund_name}' not found")

        row = self._annual_returns_repo.create(
            fund_id=fund.id,
            highest_pct=highest_pct,
            lowest_pct=lowest_pct,
            as_of_date=as_of_date,
        )
        self._annual_returns_repo.session.commit()
        return row

    def get_latest_annual_returns(self, fund_id: UUID) -> AnnualReturnsTable | None:
        return self._annual_returns_repo.get_latest_by_fund(fund_id)
