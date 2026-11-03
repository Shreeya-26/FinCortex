"""Step 2: compare two models on unseen data and save the better one."""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from app.features import FEATURE_COLUMNS, engineer_features

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "data" / "synthetic_data.csv"
MODEL_FILE = HERE / "model.pkl"


def main():
    df = pd.read_csv(DATA_FILE)
    X, y = engineer_features(df), df["health_score"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    candidates = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_leaf=5, random_state=42),
    }
    results = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        results[name] = (mean_absolute_error(y_test, pred), r2_score(y_test, pred))
        print(f"{name:<17} MAE {results[name][0]:.2f}   R2 {results[name][1]:.3f}")

    best = min(results, key=lambda k: results[k][0])
    print(f"\nSaving the best model: {best}")
    joblib.dump(candidates[best], MODEL_FILE, compress=3)

    if hasattr(candidates[best], "feature_importances_"):
        print("\nWhat the model pays attention to:")
        for col, imp in sorted(zip(FEATURE_COLUMNS, candidates[best].feature_importances_), key=lambda t: -t[1]):
            print(f"  {col:<20} {imp:.2f}")


if __name__ == "__main__":
    main()
