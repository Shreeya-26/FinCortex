"""Step 1: create synthetic Indian salary profiles and score them with a hand-written rule."""
from pathlib import Path

import numpy as np
import pandas as pd

from app.features import engineer_features, total_expenses

DATA_DIR = Path(__file__).resolve().parent / "data"
N = 6000


def generate_profiles(n: int = N, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    salary = rng.integers(15000, 200000, n)
    return pd.DataFrame({
        "salary": salary,
        "rent": (salary * rng.uniform(0.10, 0.35, n)).astype(int),
        "food": (salary * rng.uniform(0.08, 0.20, n)).astype(int),
        "transport": (salary * rng.uniform(0.03, 0.12, n)).astype(int),
        "emi": (salary * rng.uniform(0.0, 0.45, n)).astype(int),
        "other_expenses": (salary * rng.uniform(0.02, 0.15, n)).astype(int),
        "existing_savings": (salary * rng.uniform(0, 6, n)).astype(int),
    })


def health_score(df: pd.DataFrame, seed: int = 42) -> pd.Series:
    """The 'teacher' rule: max 100 points across four habits, plus a little noise."""
    rng = np.random.default_rng(seed)
    f = engineer_features(df)
    savings = (f.savings_rate / 0.30).clip(0, 1) * 30                    # save 30%+ of salary
    emi = (1 - (f.emi_ratio / 0.50).clip(0, 1)) * 25                     # keep EMI well under 50%
    emergency = (f.emergency_coverage).clip(0, 1) * 25                   # 3 months of expenses saved
    spending = (1 - ((f.expense_ratio - 0.5) / 0.5).clip(0, 1)) * 20     # spend under ~50% of salary
    return (savings + emi + emergency + spending + rng.normal(0, 2, len(df))).clip(0, 100).round(1)


def main():
    DATA_DIR.mkdir(exist_ok=True)
    df = generate_profiles()
    df["health_score"] = health_score(df)
    df.to_csv(DATA_DIR / "synthetic_data.csv", index=False)
    print(f"Saved {len(df)} synthetic profiles to {DATA_DIR / 'synthetic_data.csv'}")
    return df


if __name__ == "__main__":
    main()
