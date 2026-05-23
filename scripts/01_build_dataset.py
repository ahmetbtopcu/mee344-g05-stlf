#!/usr/bin/env python3
"""Build merged and feature-engineered datasets."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mee344_g05.config import DATA_PROCESSED, DATA_INTERIM, TRAIN_PARQUET, TEST_PARQUET
from mee344_g05.data_loader import save_merged
from mee344_g05.features import build_features, get_feature_columns, train_test_split_time
from mee344_g05.preprocessing import preprocess_merged


def main():
    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    merged = save_merged()
    clean = preprocess_merged(merged)
    featured = build_features(clean)
    train, test = train_test_split_time(featured)

    train.to_parquet(TRAIN_PARQUET)
    test.to_parquet(TEST_PARQUET)

    feat_cols = get_feature_columns(featured)
    print(f"Merged rows: {len(merged)}")
    print(f"Featured rows: {len(featured)} | features: {len(feat_cols)}")
    print(f"Train: {len(train)} | Test: {len(test)}")
    print(f"Saved: {TRAIN_PARQUET}, {TEST_PARQUET}")


if __name__ == "__main__":
    main()
