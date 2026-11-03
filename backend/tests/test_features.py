import pandas as pd

from app.features import engineer_features


def test_ratios_are_computed_correctly():
    df = pd.DataFrame([{"salary": 100000, "rent": 20000, "food": 10000, "transport": 5000,
                        "emi": 15000, "other_expenses": 10000, "existing_savings": 180000}])
    f = engineer_features(df).iloc[0]
    assert f.savings_rate == 0.40          # (100k - 60k) / 100k
    assert f.emi_ratio == 0.15
    assert f.expense_ratio == 0.60
    assert f.emergency_coverage == 1.0     # 180k savings = exactly 3 months of 60k


def test_overspending_never_gives_negative_savings_rate():
    df = pd.DataFrame([{"salary": 30000, "rent": 20000, "food": 10000, "transport": 5000,
                        "emi": 10000, "other_expenses": 5000, "existing_savings": 0}])
    assert engineer_features(df).iloc[0].savings_rate == 0
