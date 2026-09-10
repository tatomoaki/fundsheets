from datetime import date
from uuid import UUID

from src.models.asset_allocation import AssetAllocation
from src.storage.repositories import AssetAllocationRepository, FundRepository
from src.storage.tables import AssetAllocationTable


class AssetAllocationService:
    def __init__(self, allocation_repo: AssetAllocationRepository, fund_repo: FundRepository):
        self._allocation_repo = allocation_repo
        self._fund_repo = fund_repo

    def record_allocations(
        self,
        *,
        fund_name: str,
        allocations: list[AssetAllocation],
    ) -> list[AssetAllocationTable]:
        fund = self._fund_repo.get_by_fund_name(fund_name)
        if fund is None:
            raise ValueError(f"Fund '{fund_name}' not found")

        rows = self._allocation_repo.bulk_create(fund_id=fund.id, allocations=allocations)
        self._allocation_repo.session.commit()
        return rows

    def get_allocations(self, fund_id: UUID, as_of_date: date) -> list[AssetAllocationTable]:
        return self._allocation_repo.list_by_fund_and_date(fund_id, as_of_date)

    def get_latest_allocations(self, fund_id: UUID) -> list[AssetAllocationTable]:
        latest_date = self._allocation_repo.get_latest_date_by_fund(fund_id)
        if latest_date is None:
            return []
        return self._allocation_repo.list_by_fund_and_date(fund_id, latest_date)
