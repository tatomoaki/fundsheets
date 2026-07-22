from pydantic import BaseModel
from datetime import date


class Fund(BaseModel):
    id: str
    name: str
    manager: str | None
    risk_profile: str | None = None
    asisa_classification: str | None = None
    benchmark: str | None = None
    portfolio_launch_date: date | None = None
    portfolio_size: str | None = None
    as_of_date: date | None = None