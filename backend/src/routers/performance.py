from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.dependencies import get_db_session
from src.services.performance_service import PerformanceService
from src.storage.repositories import AnnualReturnsRepository, FundRepository, PerformanceRepository

router = APIRouter(prefix="/funds/{fund_id}/performance", tags=["performance"])


class PerformanceRecordResponse(BaseModel):
    id: UUID
    fund_id: UUID
    period: str
    fund_return_pct: Decimal | None
    benchmark_return_pct: Decimal | None
    tracking_difference_pct: Decimal | None
    as_of_date: date | None

    model_config = ConfigDict(from_attributes=True)


class AnnualReturnsResponse(BaseModel):
    id: UUID
    fund_id: UUID
    highest_pct: Decimal | None
    lowest_pct: Decimal | None
    as_of_date: date

    model_config = ConfigDict(from_attributes=True)


def _service(session: Session = Depends(get_db_session)) -> PerformanceService:
    return PerformanceService(
        PerformanceRepository(session),
        AnnualReturnsRepository(session),
        FundRepository(session),
    )


@router.get("/", response_model=list[PerformanceRecordResponse])
def get_performance(fund_id: UUID, service: PerformanceService = Depends(_service)):
    return service.get_latest_performance(fund_id)


@router.get("/annual-returns", response_model=AnnualReturnsResponse | None)
def get_annual_returns(fund_id: UUID, service: PerformanceService = Depends(_service)):
    return service.get_latest_annual_returns(fund_id)
