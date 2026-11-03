"""Turns raw rupee amounts into ratios. Used by BOTH training and the API, so they never disagree."""
import pandas as pd

# Limits used by the API warnings. (The training rule in ml/generate_data.py scores EMI down to zero points at 50%.)
HIGH_EMI_RATIO = 0.40        # above this share of salary, warn about EMIs
EMERGENCY_MONTHS = 3         # months of expenses an emergency fund should cover

FEATURE_COLUMNS = ["savings_rate", "emi_ratio", "rent_ratio", "expense_ratio", "emergency_coverage"]


def total_expenses(df: pd.DataFrame) -> pd.Series:
    return df["rent"] + df["food"] + df["transport"] + df["emi"] + df["other_expenses"]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    total = total_expenses(df)
    out = pd.DataFrame(index=df.index)
    out["savings_rate"] = (df["salary"] - total).clip(lower=0) / df["salary"]   # share of salary left over
    out["emi_ratio"] = df["emi"] / df["salary"]                                  # share going to loans
    out["rent_ratio"] = df["rent"] / df["salary"]                                # share going to rent
    out["expense_ratio"] = total / df["salary"]                                  # share spent in total
    out["emergency_coverage"] = (df["existing_savings"] / (total * 3).clip(lower=1)).clip(0, 3)  # 1.0 = 3 months covered
    return out[FEATURE_COLUMNS]
