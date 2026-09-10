from typing import Sequence

from src.models.funds import Fund
from src.storage.repositories import FundRepository
from src.storage.tables import FundTable


class FundService:
    def __init__(self, fund_repo: FundRepository):
        self._fund_repo = fund_repo

    def list_funds(self) -> Sequence[Fund]:
        return self._fund_repo.list_funds()
    
    def create_fund(
            self,
            *,
            name: str,
            manager: str | None,
            risk_profile: str | None,
            asisa_classification: str | None = None,
            benchmark: str | None = None,
            portfolio_launch_date=None,
            portfolio_size: str | None = None,
            as_of_date=None,
            fund_hash: str | None = None,
            **_ignored,
    ) -> FundTable:
        from datetime import date

        existing = self._fund_repo.get_by_fund_name(name)
        if existing:
            return existing

        def _to_date(val) -> date | None:
            if val is None:
                return None
            if isinstance(val, date):
                return val
            s = str(val).strip()
            if not s:
                return None
            # Accept YYYY-MM-DD or YYYY-MM
            parts = s.split("-")
            if len(parts) == 2:
                return date(int(parts[0]), int(parts[1]), 1)
            return date.fromisoformat(s)

        fund = self._fund_repo.create(
            name=name,
            manager=manager,
            risk_profile=risk_profile,
            asisa_classification=asisa_classification,
            benchmark=benchmark,
            portfolio_launch_date=_to_date(portfolio_launch_date),
            portfolio_size=portfolio_size,
            as_of_date=_to_date(as_of_date),
            fund_hash=fund_hash,
        )
        self._fund_repo.session.commit()
        return fund