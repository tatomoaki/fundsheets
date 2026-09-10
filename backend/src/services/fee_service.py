from datetime import date
from decimal import Decimal
from uuid import UUID

from src.storage.repositories import FeeRepository, FundRepository
from src.storage.tables import FeeTable


class FeeService:
    def __init__(self, fee_repo: FeeRepository, fund_repo: FundRepository):
        self._fee_repo = fee_repo
        self._fund_repo = fund_repo

    def record_fees(
        self,
        *,
        fund_name: str | None = None,
        fund_id: UUID | None = None,
        advice_initial_fee_max_pct: Decimal | None = None,
        manager_initial_fee_pct: Decimal | None = None,
        advice_annual_fee_max_pct: Decimal | None = None,
        manager_annual_fee_pct: Decimal | None = None,
        ter: Decimal | None,
        transaction_cost_pct: Decimal | None = None,
        total_investment_charge_pct: Decimal | None = None,
        currency: str = "ZAR",
        effective_date: date,
        as_of_date: date,
    ) -> FeeTable:
        resolved_id = self._resolve_fund_id(fund_name=fund_name, fund_id=fund_id)

        row = self._fee_repo.create(
            fund_id=resolved_id,
            advice_initial_fee_max_pct=advice_initial_fee_max_pct,
            manager_initial_fee_pct=manager_initial_fee_pct,
            advice_annual_fee_max_pct=advice_annual_fee_max_pct,
            manager_annual_fee_pct=manager_annual_fee_pct,
            ter=ter,
            transaction_cost_pct=transaction_cost_pct,
            total_investment_charge_pct=total_investment_charge_pct,
            currency=currency,
            effective_date=effective_date,
            as_of_date=as_of_date,
        )
        self._fee_repo.session.commit()
        return row

    def _resolve_fund_id(self, *, fund_name: str | None, fund_id: UUID | None) -> UUID:
        if fund_id is not None:
            return fund_id
        if fund_name is not None:
            fund = self._fund_repo.get_by_fund_name(fund_name)
            if fund is None:
                raise ValueError(f"Fund '{fund_name}' not found")
            return fund.id
        raise ValueError("Either fund_name or fund_id must be provided")

    def get_latest_fees(self, fund_id: UUID) -> FeeTable | None:
        return self._fee_repo.get_latest_by_fund(fund_id)

    def list_fees(self, fund_id: UUID) -> list[FeeTable]:
        return self._fee_repo.list_by_fund(fund_id)
