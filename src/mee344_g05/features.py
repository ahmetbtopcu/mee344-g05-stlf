"""Feature engineering for STLF."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import PRODUCTION_SOURCE_COLS, TARGET_COL, TEST_HOURS, TR_HOLIDAYS


def _cyclic(series: pd.Series, period: float) -> tuple[pd.Series, pd.Series]:
    return (
        np.sin(2 * np.pi * series / period),
        np.cos(2 * np.pi * series / period),
    )


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    idx = out.index
    hour = idx.hour
    dow = idx.dayofweek
    doy = idx.dayofyear

    out["hour_sin"], out["hour_cos"] = _cyclic(hour, 24)
    out["dow_sin"], out["dow_cos"] = _cyclic(dow, 7)
    out["doy_sin"], out["doy_cos"] = _cyclic(doy, 365.25)
    out["is_weekend"] = (dow >= 5).astype(int)
    out["is_business_hour"] = ((hour >= 9) & (hour <= 18)).astype(int)
    out["is_holiday"] = idx.normalize().astype(str).isin(TR_HOLIDAYS).astype(int)
    return out


def add_lag_features(df: pd.DataFrame, target: str = TARGET_COL) -> pd.DataFrame:
    out = df.copy()
    for lag in [1, 2, 3, 24, 168]:
        out[f"lag_{lag}h"] = out[target].shift(lag)
    return out


def add_rolling_features(df: pd.DataFrame, target: str = TARGET_COL) -> pd.DataFrame:
    out = df.copy()
    shifted = out[target].shift(1)
    out["roll_mean_24h"] = shifted.rolling(24, min_periods=12).mean()
    out["roll_mean_168h"] = shifted.rolling(168, min_periods=84).mean()
    out["roll_std_24h"] = shifted.rolling(24, min_periods=12).std()
    out["roll_max_24h"] = shifted.rolling(24, min_periods=12).max()
    out["roll_min_24h"] = shifted.rolling(24, min_periods=12).min()
    return out


def add_exogenous_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "ruzgar" in out.columns:
        out["prod_wind"] = out["ruzgar"]
    if "gunes" in out.columns:
        out["prod_solar"] = out["gunes"]
    if "barajli" in out.columns and "akarsu" in out.columns:
        out["prod_hydro"] = out["barajli"] + out["akarsu"]
    thermal_cols = [
        c
        for c in [
            "dogal_gaz",
            "linyit",
            "ithal_komur",
            "tas_komur",
            "asfaltit_komur",
            "fuel_oil",
        ]
        if c in out.columns
    ]
    if thermal_cols:
        out["prod_thermal"] = out[thermal_cols].sum(axis=1)
    renew_cols = [
        c
        for c in ["ruzgar", "gunes", "jeotermal", "biyokutle"]
        if c in out.columns
    ]
    if "production_total" in out.columns and renew_cols:
        renew = out[renew_cols].sum(axis=1)
        if "prod_hydro" in out.columns:
            renew = renew + out["prod_hydro"]
        out["prod_renewable_share"] = renew / out["production_total"].replace(0, np.nan)
    if "production_total" in out.columns:
        out["net_balance"] = out["production_total"] - out[TARGET_COL]
    return out


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    exclude = {
        TARGET_COL,
        "tarih",
        "saat",
        "gap_hours",
    }
    exclude.update(PRODUCTION_SOURCE_COLS)
    exclude.update(["production_total", "nafta", "lng"])
    return [c for c in df.columns if c not in exclude and df[c].dtype in ["float64", "int64", "float32", "int32"]]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = add_time_features(df)
    out = add_exogenous_features(out)
    out = add_lag_features(out)
    out = add_rolling_features(out)
    return out.dropna()


def train_test_split_time(
    df: pd.DataFrame,
    test_hours: int = TEST_HOURS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_idx = len(df) - test_hours
    train = df.iloc[:split_idx].copy()
    test = df.iloc[split_idx:].copy()
    return train, test
