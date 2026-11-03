from typing import Literal

from pydantic import BaseModel, Field, model_validator

MAX_SALARY = 10_000_000          # per month, in rupees
MAX_EXPENSE = 10_000_000
MAX_SAVINGS = 1_000_000_000

Risk = Literal["Low", "Medium", "High"]


class FinancialInput(BaseModel):
    salary: float = Field(..., gt=0, le=MAX_SALARY, description="Monthly take-home salary in rupees")
    rent: float = Field(0, ge=0, le=MAX_EXPENSE)
    food: float = Field(0, ge=0, le=MAX_EXPENSE)
    transport: float = Field(0, ge=0, le=MAX_EXPENSE)
    emi: float = Field(0, ge=0, le=MAX_EXPENSE)
    other_expenses: float = Field(0, ge=0, le=MAX_EXPENSE)
    existing_savings: float = Field(0, ge=0, le=MAX_SAVINGS)
    risk_appetite: Risk = "Medium"

    @model_validator(mode="after")
    def expenses_must_be_believable(self):
        total = self.rent + self.food + self.transport + self.emi + self.other_expenses
        if total > 3 * self.salary:     # almost always a typo, like an extra zero
            raise ValueError("Your expenses are more than 3 times your salary. Please re-check the numbers.")
        return self


class CategoryLine(BaseModel):
    category: str
    amount: float
    pct_of_salary: float


class Rule503020(BaseModel):
    needs_pct: float
    wants_pct: float
    savings_pct: float


class PlanStep(BaseModel):
    step: int
    title: str
    detail: str


class Platform(BaseModel):
    name: str
    url: str
    best_for: str


class Reason(BaseModel):
    factor: str
    points: float            # estimated points this habit is costing
    message: str


class BiggestWin(BaseModel):
    factor: str
    projected_score: int     # score if only the biggest problem were fixed


class AnalyzeResponse(BaseModel):
    id: int
    created_at: str
    score: int
    verdict: str
    savings_rate_pct: float
    leftover: float
    emergency_fund_needed: float
    emergency_months: float
    breakdown: list[CategoryLine]
    rule_50_30_20: Rule503020
    warnings: list[str]
    reasons: list[Reason]
    biggest_win: BiggestWin | None = None
    allocation: dict[str, int]
    plan: list[PlanStep]
    platforms: list[Platform]


class HistoryItem(BaseModel):
    id: int
    created_at: str
    score: int
    salary: float
    savings_rate_pct: float
    risk_appetite: str
