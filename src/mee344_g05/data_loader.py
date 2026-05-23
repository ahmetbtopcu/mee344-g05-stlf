"""EPİAŞ locale-aware data loading and merge."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .config import MERGED_PARQUET, PRODUCTION_SOURCE_COLS, TARGET_COL, TUKETIM_CSV, URETIM_CSV


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """ASCII-safe column names."""
    mapping = {}
    for col in df.columns:
        key = (
            col.strip()
            .lower()
            .replace("ı", "i")
            .replace("ğ", "g")
            .replace("ü", "u")
            .replace("ş", "s")
            .replace("ö", "o")
            .replace("ç", "c")
            .replace("?", "")
        )
        key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
        mapping[col] = key
    return df.rename(columns=mapping)


def _parse_turkish_number(series: pd.Series) -> pd.Series:
    """Convert '48.719,05' or '48666,45' style strings to float."""
    if series.dtype in ("float64", "int64", "float32", "int32"):
        return series
    s = series.astype(str).str.strip()
    s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def read_epias_csv(path: Path) -> pd.DataFrame:
    """Read semicolon-separated Turkish-locale CSV."""
    last_err = None
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            df = pd.read_csv(path, sep=";", encoding=enc, dtype=str)
            df = _normalize_columns(df)
            for col in df.columns:
                if col in ("tarih", "saat"):
                    continue
                df[col] = _parse_turkish_number(df[col])
            return df
        except UnicodeDecodeError as e:
            last_err = e
    raise last_err  # type: ignore[misc]


def _parse_datetime(df: pd.DataFrame) -> pd.Series:
    combined = df["tarih"].astype(str).str.strip() + " " + df["saat"].astype(str).str.strip()
    parsed = pd.to_datetime(combined, format="%d.%m.%Y %H:%M", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(combined, dayfirst=True, errors="coerce")
    return parsed


def load_production(path: Path = URETIM_CSV) -> pd.DataFrame:
    df = read_epias_csv(path)
    df["datetime"] = _parse_datetime(df)
    df = df.dropna(subset=["datetime"]).sort_values("datetime")
    df = df.set_index("datetime")

    rename = {"toplam": "production_total"}
    for src in PRODUCTION_SOURCE_COLS:
        if src in df.columns:
            rename[src] = src
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    drop_cols = [c for c in df.columns if c in ("tarih", "saat")]
    return df.drop(columns=drop_cols, errors="ignore")


def load_consumption(path: Path = TUKETIM_CSV) -> pd.DataFrame:
    df = read_epias_csv(path)
    df["datetime"] = _parse_datetime(df)
    df = df.dropna(subset=["datetime"]).sort_values("datetime")
    df = df.set_index("datetime")

    cons_col = None
    for c in df.columns:
        if "tuketim" in c or "mwh" in c:
            cons_col = c
            break
    if cons_col is None:
        raise ValueError(f"Consumption column not found in {path}")

    out = df[[cons_col]].rename(columns={cons_col: TARGET_COL})
    return out


def merge_datasets(
    production: pd.DataFrame | None = None,
    consumption: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if production is None:
        production = load_production()
    if consumption is None:
        consumption = load_consumption()

    merged = production.join(consumption, how="inner")
    merged = merged[~merged.index.duplicated(keep="first")]
    merged = merged.sort_index()
    return merged


def save_merged(path: Path = MERGED_PARQUET) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    merged = merge_datasets()
    merged.to_parquet(path)
    return merged


def load_merged(path: Path = MERGED_PARQUET) -> pd.DataFrame:
    if path.exists():
        return pd.read_parquet(path)
    return save_merged(path)
