#!/usr/bin/env python3
"""Extra diagram figures for slides."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mee344_g05.config import FIGURES_DIR
from mee344_g05.ppt_theme import NAVY, SKY, TEAL, AMBER, OFF_WHITE

OUT = FIGURES_DIR / "presentation"


def save(name):
    p = OUT / name
    plt.savefig(p, dpi=200, bbox_inches="tight", facecolor=OFF_WHITE)
    plt.close()
    return p


def cyclic_demo():
    h = np.arange(24)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(h, np.sin(2 * np.pi * h / 24), color=TEAL, lw=2.5, label="hour_sin")
    ax.plot(h, np.cos(2 * np.pi * h / 24), color=SKY, lw=2.5, label="hour_cos")
    ax.set_title("Cyclic Hour Encoding", fontweight="bold", color=NAVY)
    ax.set_xlabel("Hour of day")
    ax.legend()
    ax.grid(alpha=0.3)
    save("cyclic_demo.png")


def pipeline_horizontal():
    fig, ax = plt.subplots(figsize=(12, 2.8))
    ax.axis("off")
    steps = [
        "EPİAŞ CSV",
        "Parse & Merge",
        "Preprocess",
        "Features",
        "GridSearch CV",
        "DT + AdaBoost",
    ]
    xs = np.linspace(0.06, 0.94, len(steps))
    for i, (x, s) in enumerate(zip(xs, steps)):
        c = TEAL if i == len(steps) - 1 else NAVY
        ax.add_patch(plt.Rectangle((x - 0.065, 0.35), 0.13, 0.35, fc=c, ec="white", lw=1.5))
        ax.text(x, 0.52, s, ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        if i < len(steps) - 1:
            ax.annotate("", xy=(xs[i + 1] - 0.07, 0.52), xytext=(x + 0.07, 0.52),
                        arrowprops=dict(arrowstyle="->", color=AMBER, lw=2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save("pipeline_horizontal.png")


def weak_to_strong():
    fig, axes = plt.subplots(1, 4, figsize=(10, 2.5))
    for ax in axes:
        ax.axis("off")
    for i, ax in enumerate(axes[:3]):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.plot([0.5, 0.2, 0.8], [0.9, 0.1, 0.1], color=SKY, lw=2)
        ax.text(0.5, 0.05, f"Stump {i+1}", ha="center", fontsize=9)
    axes[3].text(0.5, 0.55, "AdaBoost\nEnsemble", ha="center", fontsize=12, fontweight="bold", color=TEAL)
    axes[3].text(0.5, 0.25, "Strong predictor", ha="center", fontsize=9, color=NAVY)
    fig.suptitle("Weak Learners → AdaBoost", fontweight="bold", color=NAVY)
    save("weak_to_strong.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cyclic_demo()
    pipeline_horizontal()
    weak_to_strong()
    print(f"Diagrams saved to {OUT}")


if __name__ == "__main__":
    main()
