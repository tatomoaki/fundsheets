from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class AssetAllocation(BaseModel):
    fund_id: str
    as_of_date: date
    asset_class: str
    weight: Decimal
