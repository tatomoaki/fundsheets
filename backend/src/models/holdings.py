from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class Holding(BaseModel):
    fund_id: str
    as_of_date: date
    instrument_name: str
    weight: Decimal