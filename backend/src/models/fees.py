from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date

class FeeBreakdown(BaseModel):
    fund_id: str
    advice_initial_fee_max_pct: Decimal | None = None
    manager_initial_fee_pct: Decimal | None = None
    advice_annual_fee_max_pct: Decimal | None = None
    manager_annual_fee_pct: Decimal | None = None
    ter: Decimal | None = Field(None, description="Total Expense Ratio, annualised")
    transaction_cost_pct: Decimal | None = None
    total_investment_charge_pct: Decimal | None = None
    currency: str = "ZAR"
    effective_date: date