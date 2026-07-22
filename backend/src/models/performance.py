from pydantic import BaseModel
from decimal import Decimal
from datetime import date


class PerformanceRecord(BaseModel):
    fund_id: str
    period: str
    fund_return_pct: Decimal | None = None
    benchmark_return_pct: Decimal | None = None
    tracking_difference_pct: Decimal | None = None
    as_of_date: date | None = None


class AnnualReturns(BaseModel):
    fund_id: str
    highest_pct: Decimal | None = None
    lowest_pct: Decimal | None = None
    as_of_date: date
