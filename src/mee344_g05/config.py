"""Project configuration and paths."""

from pathlib import Path

RANDOM_STATE = 42
N_CV_SPLITS = 5
TEST_HOURS = 336  # ~14 days hold-out

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_INTERIM = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
SLIDES_DIR = PROJECT_ROOT / "slides"

URETIM_CSV = DATA_RAW / "Gercek_Zamanli_Uretim-31072025-29102025.csv"
TUKETIM_CSV = DATA_RAW / "Gercek_Zamanli_Tuketim-31072025-29102025.csv"
MERGED_PARQUET = DATA_INTERIM / "merged.parquet"
TRAIN_PARQUET = DATA_PROCESSED / "train.parquet"
TEST_PARQUET = DATA_PROCESSED / "test.parquet"

TARGET_COL = "consumption_mwh"

# Turkish holidays in dataset window (2025)
TR_HOLIDAYS = [
    "2025-08-30",  # Zafer Bayramı
    "2025-10-29",  # Cumhuriyet Bayramı
]

PRODUCTION_SOURCE_COLS = [
    "dogal_gaz",
    "barajli",
    "linyit",
    "akarsu",
    "ithal_komur",
    "ruzgar",
    "gunes",
    "fuel_oil",
    "jeotermal",
    "asfaltit_komur",
    "tas_komur",
    "biyokutle",
    "nafta",
    "lng",
    "uluslararasi",
    "atik_isi",
]
