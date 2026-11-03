from fastapi import APIRouter, HTTPException

from . import database, explain, recommendations as rec, scoring
from .features import EMERGENCY_MONTHS, HIGH_EMI_RATIO
from .schemas import AnalyzeResponse, FinancialInput, HistoryItem

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "model_loaded": scoring.model_loaded()}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(data: FinancialInput):
    if not scoring.model_loaded() and not scoring.load_model():
        raise HTTPException(503, "Model not trained yet. Run the two training commands in the README.")

    score = scoring.predict_score(data.model_dump())
    total = rec.total_expenses(data)
    leftover = data.salary - total
    needed = round(total * EMERGENCY_MONTHS, -2)
    emergency_short = data.existing_savings < needed
    high_emi = data.emi / data.salary > HIGH_EMI_RATIO
    savings_rate = rec.pct(max(leftover, 0), data.salary)

    reasons, biggest_win = explain.explain(data.model_dump())
    check_id, created_at = database.save_check(score, data.salary, savings_rate, data.risk_appetite)
    return AnalyzeResponse(
        id=check_id, created_at=created_at, score=score, verdict=scoring.verdict_for(score),
        savings_rate_pct=savings_rate, leftover=round(leftover, 2), emergency_fund_needed=needed,
        emergency_months=round(data.existing_savings / total, 1) if total else 0.0,
        breakdown=rec.breakdown(data), rule_50_30_20=rec.rule_50_30_20(data),
        reasons=reasons, biggest_win=biggest_win,
        warnings=rec.warnings_for(data, emergency_short, high_emi),
        allocation=rec.allocation_for(data.risk_appetite, emergency_short, high_emi),
        plan=rec.plan_for(data, emergency_short, high_emi),
        platforms=rec.platforms_for(data.risk_appetite),
    )


@router.get("/history", response_model=list[HistoryItem])
def history(limit: int = 50):
    return database.list_checks(min(max(limit, 1), 200))


@router.delete("/history/{check_id}", status_code=204)
def delete_history(check_id: int):
    if not database.delete_check(check_id):
        raise HTTPException(404, "That check doesn't exist.")
