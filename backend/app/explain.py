"""'Why this score?'  For each habit we set it to a healthy level, ask the model for the new score,
and report the difference as the points that habit is costing. Everything else stays the same."""
import pandas as pd

from .features import EMERGENCY_MONTHS, engineer_features
from .schemas import BiggestWin, Reason
from . import scoring

# Healthy levels. They follow the same ideas the training rule rewards.
GOOD_SAVINGS_RATE = 0.30     # keep 30% of salary
GOOD_EMI_RATIO = 0.15        # EMIs under 15% of salary
MIN_POINTS = 2.0             # ignore habits costing less than this


def _consistent(row: pd.Series) -> pd.Series:
    """Savings rate is whatever is left after spending, so keep the two in step."""
    row["emi_ratio"] = min(row["emi_ratio"], row["expense_ratio"])
    row["savings_rate"] = max(1 - row["expense_ratio"], 0)
    return row


def _scenarios(f: pd.Series) -> dict[str, pd.Series]:
    out = {}
    s = f.copy()                                   # spending and saving are two sides of one habit
    s["expense_ratio"] = min(f["expense_ratio"], 1 - GOOD_SAVINGS_RATE)
    out["Spending and savings"] = _consistent(s)
    s = f.copy()
    s["expense_ratio"] = f["expense_ratio"] - max(f["emi_ratio"] - GOOD_EMI_RATIO, 0)
    s["emi_ratio"] = min(f["emi_ratio"], GOOD_EMI_RATIO)
    out["Loan EMIs"] = _consistent(s)
    s = f.copy()
    s["emergency_coverage"] = 1.0                  # 1.0 means a full 3 months saved
    out["Emergency fund"] = s
    return out


def _message(name: str, f: pd.Series) -> str:
    if name == "Emergency fund":
        return f"You have about {f['emergency_coverage'] * EMERGENCY_MONTHS:.1f} months of expenses saved. The goal is {EMERGENCY_MONTHS}."
    if name == "Loan EMIs":
        return f"Loan EMIs take {f['emi_ratio'] * 100:.0f}% of your salary. Aim for under {GOOD_EMI_RATIO * 100:.0f}%."
    return (f"You spend {f['expense_ratio'] * 100:.0f}% of your salary and keep {f['savings_rate'] * 100:.0f}%. "
            f"Aim to keep {GOOD_SAVINGS_RATE * 100:.0f}% or more.")


def explain(values: dict) -> tuple[list[Reason], BiggestWin | None]:
    f = engineer_features(pd.DataFrame([values])).iloc[0]
    scenarios = _scenarios(f)
    X = pd.DataFrame([f] + list(scenarios.values()))
    scores = scoring.predict_features(X).tolist()
    base = scores[0]
    reasons = []
    for (name, row), new in zip(scenarios.items(), scores[1:]):
        gain = new - base
        if gain >= MIN_POINTS:
            reasons.append(Reason(factor=name, points=round(gain, 1), message=_message(name, f)))
    reasons.sort(key=lambda r: -r.points)
    win = None
    if reasons:
        top = reasons[0]
        win = BiggestWin(factor=top.factor, projected_score=int(round(min(base + top.points, 100))))
    return reasons, win
