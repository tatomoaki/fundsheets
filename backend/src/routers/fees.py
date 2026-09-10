from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.dependencies import get_db_session
from src.services.fee_service import FeeService
from src.storage.repositories import FeeRepository, FundRepository

router = APIRouter(prefix="/funds/{fund_id}/fees", tags=["fees"])


class FeeCreate(BaseModel):
    advice_initial_fee_max_pct: Decimal | None = None
    manager_initial_fee_pct: Decimal | None = None
    advice_annual_fee_max_pct: Decimal | None = None
    manager_annual_fee_pct: Decimal | None = None
    ter: Decimal | None = Field(None, description="Total Expense Ratio, annualised")
    transaction_cost_pct: Decimal | None = None
    total_investment_charge_pct: Decimal | None = None
    currency: str = "ZAR"
    effective_date: date
    as_of_date: date


class FeeResponse(BaseModel):
    id: UUID
    fund_id: UUID
    advice_initial_fee_max_pct: Decimal | None = None
    manager_initial_fee_pct: Decimal | None = None
    advice_annual_fee_max_pct: Decimal | None = None
    manager_annual_fee_pct: Decimal | None = None
    ter: Decimal | None = None
    transaction_cost_pct: Decimal | None = None
    total_investment_charge_pct: Decimal | None = None
    currency: str
    effective_date: date
    as_of_date: date

    model_config = {"from_attributes": True}


def _fee_service(session: Session = Depends(get_db_session)) -> FeeService:
    return FeeService(FeeRepository(session), FundRepository(session))


@router.get("/", response_model=list[FeeResponse])
def list_fees(fund_id: UUID, service: FeeService = Depends(_fee_service)):
    return service.list_fees(fund_id)


@router.get("/latest", response_model=FeeResponse | None)
def get_latest_fee(fund_id: UUID, service: FeeService = Depends(_fee_service)):
    return service.get_latest_fees(fund_id)


@router.post("/", response_model=FeeResponse, status_code=201)
def create_fee(
    fund_id: UUID,
    body: FeeCreate,
    service: FeeService = Depends(_fee_service),
):
    try:
        row = service.record_fees(
            fund_name=None,
            fund_id=fund_id,
            advice_initial_fee_max_pct=body.advice_initial_fee_max_pct,
            manager_initial_fee_pct=body.manager_initial_fee_pct,
            advice_annual_fee_max_pct=body.advice_annual_fee_max_pct,
            manager_annual_fee_pct=body.manager_annual_fee_pct,
            ter=body.ter,
            transaction_cost_pct=body.transaction_cost_pct,
            total_investment_charge_pct=body.total_investment_charge_pct,
            currency=body.currency,
            effective_date=body.effective_date,
            as_of_date=body.as_of_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return row
