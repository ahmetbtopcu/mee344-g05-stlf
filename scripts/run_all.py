#!/usr/bin/env python3
"""Run full pipeline end-to-end."""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "01_build_dataset.py",
    "run_eda.py",
    "02_train_decision_tree.py",
    "03_train_adaboost.py",
    "04_evaluate_all.py",
    "run_interpretation.py",
    "regenerate_slide_figures.py",
    "build_pptx.py",
]

def main():
    root = Path(__file__).resolve().parents[1]
    for s in SCRIPTS:
        print(f"\n=== {s} ===")
        subprocess.run([sys.executable, str(root / "scripts" / s)], check=True)
    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
