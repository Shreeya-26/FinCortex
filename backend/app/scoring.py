"""Loads the trained model and turns one user's numbers into a 0-100 score."""
from pathlib import Path

import joblib
import pandas as pd

from .features import engineer_features

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "model.pkl"
_model = None


def _retrain() -> None:
    """Rebuild data and model from the seeded scripts (takes a few seconds)."""
    from ml import generate_data, train_model
    print("Training the model (first run or incompatible model.pkl)...")
    generate_data.main()
    train_model.main()


def load_model() -> bool:
    global _model
    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(MODEL_PATH)
        _model = joblib.load(MODEL_PATH)
    except Exception as exc:  # missing file or different scikit-learn version
        print(f"Could not load model ({exc.__class__.__name__}). Retraining...")
        _retrain()
        _model = joblib.load(MODEL_PATH)
    return _model is not None


def model_loaded() -> bool:
    return _model is not None


def predict_features(X: pd.DataFrame) -> pd.Series:
    """Raw model output (0-100, not rounded) for rows that are already feature ratios."""
    if _model is None:
        raise RuntimeError("Model not trained yet. Run: python -m ml.generate_data && python -m ml.train_model")
    return pd.Series(_model.predict(X), index=X.index).clip(0, 100)


def predict_score(values: dict) -> int:
    X = engineer_features(pd.DataFrame([values]))
    return int(round(float(predict_features(X).iloc[0])))


def verdict_for(score: int) -> str:
    return "Healthy" if score >= 75 else "Fair" if score >= 50 else "Needs attention"
