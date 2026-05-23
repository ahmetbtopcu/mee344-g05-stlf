"""Live inference — load models and forecast consumption."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .config import MERGED_PARQUET, MODELS_DIR, TARGET_COL, TRAIN_PARQUET, TEST_PARQUET
from .data_loader import load_merged
from .features import build_features, get_feature_columns
from .preprocessing import preprocess_merged


@dataclass
class PredictionResult:
    timestamp: str
    consumption_actual_mwh: float | None
    decision_tree_mwh: float
    adaboost_mwh: float
    is_forecast: bool


class STLFPredictor:
    """Hourly consumption forecasting with DT + AdaBoost."""

    def __init__(self) -> None:
        self._load_models()
        self._load_history()

    def _load_models(self) -> None:
        dt_bundle = joblib.load(MODELS_DIR / "decision_tree.joblib")
        ada_bundle = joblib.load(MODELS_DIR / "adaboost.joblib")
        self.dt_model = dt_bundle["model"]
        self.ada_model = ada_bundle["model"]
        self.feature_columns = dt_bundle["feature_columns"]

    def _load_history(self) -> None:
        if MERGED_PARQUET.exists():
            raw = pd.read_parquet(MERGED_PARQUET)
        else:
            raw = preprocess_merged(load_merged())
        self.raw_history = preprocess_merged(raw) if TARGET_COL in raw.columns else raw

        parts = []
        for path in (TRAIN_PARQUET, TEST_PARQUET):
            if path.exists():
                parts.append(pd.read_parquet(path))
        self.featured_history = pd.concat(parts).sort_index() if parts else build_features(self.raw_history)

    def _predict_row(self, X: pd.DataFrame) -> tuple[float, float]:
        x = X[self.feature_columns]
        return float(self.dt_model.predict(x)[0]), float(self.ada_model.predict(x)[0])

    def predict_at(self, timestamp: str | datetime) -> PredictionResult:
        """Predict for one timestamp that exists in featured history."""
        ts = pd.Timestamp(timestamp)
        if ts not in self.featured_history.index:
            raise ValueError(f"Timestamp {ts} not in history. Use forecast() for future hours.")
        row = self.featured_history.loc[[ts]]
        dt_p, ada_p = self._predict_row(row)
        actual = self.raw_history.loc[ts, TARGET_COL] if ts in self.raw_history.index else None
        return PredictionResult(
            timestamp=ts.isoformat(),
            consumption_actual_mwh=float(actual) if actual is not None else None,
            decision_tree_mwh=dt_p,
            adaboost_mwh=ada_p,
            is_forecast=False,
        )

    def forecast(self, hours: int = 24) -> list[PredictionResult]:
        """
        Recursive multi-step forecast: her adımda bir sonraki saatin tüketimini tahmin eder.
        Gelecek saatlerin üretim değerleri son bilinen saatten taşınır (proxy).
        """
        df = self.raw_history.copy()
        results: list[PredictionResult] = []

        for _ in range(hours):
            featured = build_features(df)
            if featured.empty:
                break
            last_ts = featured.index[-1]
            row = featured.iloc[[-1]]
            dt_p, ada_p = self._predict_row(row)
            next_ts = last_ts + pd.Timedelta(hours=1)
            results.append(
                PredictionResult(
                    timestamp=next_ts.isoformat(),
                    consumption_actual_mwh=None,
                    decision_tree_mwh=dt_p,
                    adaboost_mwh=ada_p,
                    is_forecast=True,
                )
            )
            new_row = df.loc[last_ts].copy()
            new_row[TARGET_COL] = ada_p
            new_row.name = next_ts
            df = pd.concat([df, new_row.to_frame().T])
            if df.index.name is None:
                df.index.name = "datetime"

        return results

    def recent_actuals(self, hours: int = 72) -> list[dict[str, Any]]:
        tail = self.raw_history.tail(hours)
        return [
            {"timestamp": ts.isoformat(), "consumption_mwh": float(tail.loc[ts, TARGET_COL])}
            for ts in tail.index
        ]

    def backtest_sample(self, hours: int = 48) -> list[dict[str, Any]]:
        """Last N hours from test set: actual vs both models."""
        tail = self.featured_history.tail(hours)
        out = []
        for ts in tail.index:
            row = tail.loc[[ts]]
            dt_p, ada_p = self._predict_row(row)
            actual = float(self.raw_history.loc[ts, TARGET_COL]) if ts in self.raw_history.index else None
            out.append(
                {
                    "timestamp": ts.isoformat(),
                    "actual": actual,
                    "decision_tree": dt_p,
                    "adaboost": ada_p,
                }
            )
        return out

    def info(self) -> dict[str, Any]:
        return {
            "target": TARGET_COL,
            "features": len(self.feature_columns),
            "history_from": str(self.raw_history.index.min()),
            "history_to": str(self.raw_history.index.max()),
            "history_hours": len(self.raw_history),
            "models": ["decision_tree", "adaboost"],
        }
