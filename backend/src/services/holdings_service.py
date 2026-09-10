from datetime import date
from decimal import Decimal
from uuid import UUID

from src.models.holdings import Holding
from src.storage.repositories import FundRepository, HoldingsRepository
from src.storage.tables import HoldingTable


class HoldingsService:
    def __init__(self, holdings_repo: HoldingsRepository, fund_repo: FundRepository):
        self._holdings_repo = holdings_repo
        self._fund_repo = fund_repo

    def record_holdings(
        self,
        *,
        fund_name: str,
        holdings: list[Holding],
    ) -> list[HoldingTable]:
        fund = self._fund_repo.get_by_fund_name(fund_name)
        if fund is None:
            raise ValueError(f"Fund '{fund_name}' not found")

        rows = self._holdings_repo.bulk_create(fund_id=fund.id, holdings=holdings)
        self._holdings_repo.session.commit()
        return rows

    def get_holdings(self, fund_id: UUID, as_of_date: date) -> list[HoldingTable]:
        return self._holdings_repo.list_by_fund_and_date(fund_id, as_of_date)

    def get_latest_holdings(self, fund_id: UUID) -> list[HoldingTable]:
        latest_date = self._holdings_repo.get_latest_date_by_fund(fund_id)
        if latest_date is None:
            return []
        return self._holdings_repo.list_by_fund_and_date(fund_id, latest_date)

    def compare_funds(self, fund_a_id: UUID, fund_b_id: UUID) -> dict:
        holdings_a = self.get_latest_holdings(fund_a_id)
        holdings_b = self.get_latest_holdings(fund_b_id)

        weights_a = {h.instrument_name: Decimal(str(h.weight_pct)) if h.weight_pct is not None else Decimal(0) for h in holdings_a}
        weights_b = {h.instrument_name: Decimal(str(h.weight_pct)) if h.weight_pct is not None else Decimal(0) for h in holdings_b}

        shared = set(weights_a) & set(weights_b)
        overlap_pct = sum(min(weights_a[name], weights_b[name]) for name in shared)

        common_holdings = [
            {
                "instrument_name": name,
                "fund_a_weight": weights_a[name],
                "fund_b_weight": weights_b[name],
            }
            for name in sorted(shared)
        ]

        fund_a_only = sorted(set(weights_a) - shared)
        fund_b_only = sorted(set(weights_b) - shared)

        return {
            "fund_a_id": fund_a_id,
            "fund_b_id": fund_b_id,
            "overlap_pct": overlap_pct,
            "common_holdings": common_holdings,
            "fund_a_only": fund_a_only,
            "fund_b_only": fund_b_only,
        }
