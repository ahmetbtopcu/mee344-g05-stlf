#!/usr/bin/env python3
"""Copy final report; optional PDF via pandoc if installed."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "reports" / "final_report.md"
REPORT_PDF = ROOT / "reports" / "final_report.pdf"


def main():
    if not REPORT_MD.exists():
        print("Missing final_report.md")
        sys.exit(1)
    try:
        subprocess.run(
            [
                "pandoc",
                str(REPORT_MD),
                "-o",
                str(REPORT_PDF),
                "--pdf-engine=xelatex",
                "-V",
                "geometry:margin=1in",
            ],
            check=True,
        )
        print(f"PDF: {REPORT_PDF}")
    except (FileNotFoundError, subprocess.CalledProcessError):
        html = ROOT / "reports" / "final_report.html"
        shutil.copy(REPORT_MD, ROOT / "reports" / "final_report_copy.md")
        print("pandoc not found — report available as Markdown:")
        print(f"  {REPORT_MD}")
        print("Export PDF manually: Word, VS Code Markdown PDF, or install pandoc.")


if __name__ == "__main__":
    main()
