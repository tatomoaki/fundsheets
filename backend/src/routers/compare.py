from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.dependencies import get_db_session
from src.services.holdings_service import HoldingsService
from src.storage.repositories import FundRepository, HoldingsRepository

router = APIRouter(prefix="/funds/compare", tags=["compare"])


class CommonHolding(BaseModel):
    instrument_name: str
    fund_a_weight: Decimal | None
    fund_b_weight: Decimal | None


class OverlapResponse(BaseModel):
    fund_a_id: UUID
    fund_b_id: UUID
    overlap_pct: Decimal
    common_holdings: list[CommonHolding]
    fund_a_only: list[str]
    fund_b_only: list[str]


def _holdings_service(session: Session = Depends(get_db_session)) -> HoldingsService:
    return HoldingsService(HoldingsRepository(session), FundRepository(session))


@router.get("/", response_model=OverlapResponse)
def compare_funds(
    fund_a: UUID = Query(..., description="First fund ID"),
    fund_b: UUID = Query(..., description="Second fund ID"),
    service: HoldingsService = Depends(_holdings_service),
):
    return service.compare_funds(fund_a, fund_b)
