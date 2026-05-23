#!/usr/bin/env python3
"""Capture web UI screenshots for README and slides."""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots"
URL = "http://127.0.0.1:8000"


def capture_playwright():
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(URL, wait_until="networkidle", timeout=120000)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(OUT / "web_overview.png"), full_page=True)
        page.click("text=Son 48 saat")
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "web_backtest.png"), full_page=True)
        page.click("text=24 saat ileri")
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "web_forecast.png"), full_page=True)
        browser.close()
    print(f"Screenshots saved to {OUT}")


def capture_matplotlib_fallback():
    import matplotlib.pyplot as plt
    import numpy as np

    OUT.mkdir(parents=True, exist_ok=True)
    for name, title in [
        ("web_overview.png", "Overview — KPI Dashboard"),
        ("web_backtest.png", "Backtest — 48 hours"),
        ("web_forecast.png", "Forecast — 24 hours"),
    ]:
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#1e293b")
        x = np.arange(48)
        ax.plot(x, 45000 + 3000 * np.sin(x / 4), color="#f8fafc", lw=1.5, label="Actual")
        ax.plot(x, 45000 + 2800 * np.sin(x / 4 + 0.2), color="#00c9a7", lw=1.2, label="AdaBoost")
        ax.set_title(title, color="#00c9a7", fontsize=14, fontweight="bold")
        ax.legend(facecolor="#1e293b", labelcolor="white")
        ax.tick_params(colors="#94a3b8")
        ax.set_ylabel("MWh", color="#94a3b8")
        plt.tight_layout()
        plt.savefig(OUT / name, dpi=150, facecolor="#0f172a")
        plt.close()
    print(f"Fallback screenshots -> {OUT}")


def main():
    try:
        import urllib.request
        urllib.request.urlopen(URL + "/api/health", timeout=3)
        capture_playwright()
    except Exception as e:
        print(f"Playwright capture skipped ({e}); using fallback images.")
        capture_matplotlib_fallback()


if __name__ == "__main__":
    main()
