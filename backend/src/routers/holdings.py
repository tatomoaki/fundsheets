from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.dependencies import get_db_session
from src.models.holdings import Holding
from src.services.holdings_service import HoldingsService
from src.storage.repositories import FundRepository, HoldingsRepository

router = APIRouter(prefix="/funds/{fund_id}/holdings", tags=["holdings"])


class HoldingCreate(BaseModel):
    instrument_name: str
    weight: Decimal
    as_of_date: date


class HoldingResponse(BaseModel):
    id: UUID
    fund_id: UUID
    instrument_name: str
    weight_pct: Decimal | None
    as_of_date: date

    model_config = ConfigDict(from_attributes=True)


def _holdings_service(session: Session = Depends(get_db_session)) -> HoldingsService:
    return HoldingsService(HoldingsRepository(session), FundRepository(session))


@router.get("/", response_model=list[HoldingResponse])
def list_holdings(
    fund_id: UUID,
    as_of_date: date | None = Query(None, description="Filter by date. Omit for latest."),
    service: HoldingsService = Depends(_holdings_service),
):
    if as_of_date:
        return service.get_holdings(fund_id, as_of_date)
    return service.get_latest_holdings(fund_id)
 

@router.post("/", response_model=list[HoldingResponse], status_code=201)
def create_holdings(
    fund_id: UUID,
    body: list[HoldingCreate],
    service: HoldingsService = Depends(_holdings_service),
):
    holdings = [
        Holding(
            fund_id=str(fund_id),
            instrument_name=h.instrument_name,
            weight=h.weight,
            as_of_date=h.as_of_date,
        )
        for h in body
    ]
    try:
        rows = service.record_holdings(fund_name=None, fund_id=fund_id, holdings=holdings)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return rows
