from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.dependencies import get_db_session
from src.services.asset_allocation_service import AssetAllocationService
from src.storage.repositories import AssetAllocationRepository, FundRepository

router = APIRouter(prefix="/funds/{fund_id}/asset-allocations", tags=["asset-allocations"])


class AssetAllocationResponse(BaseModel):
    id: UUID
    fund_id: UUID
    asset_class: str
    weight_pct: Decimal | None
    as_of_date: date

    model_config = ConfigDict(from_attributes=True)


def _service(session: Session = Depends(get_db_session)) -> AssetAllocationService:
    return AssetAllocationService(AssetAllocationRepository(session), FundRepository(session))


@router.get("/", response_model=list[AssetAllocationResponse])
def list_asset_allocations(
    fund_id: UUID,
    as_of_date: date | None = Query(None, description="Filter by date. Omit for latest."),
    service: AssetAllocationService = Depends(_service),
):
    if as_of_date:
        return service.get_allocations(fund_id, as_of_date)
    return service.get_latest_allocations(fund_id)
