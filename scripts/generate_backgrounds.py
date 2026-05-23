#!/usr/bin/env python3
"""Generate presentation background images (1920x1080)."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "backgrounds"
W, H = 19.2, 10.8  # inches at 100 dpi -> 1920x1080


def save(name: str):
    path = OUT / name
    plt.savefig(path, dpi=100, bbox_inches="tight", pad_inches=0, facecolor="#0B1F3A")
    plt.close()
    return path


def mesh_bg(seed=0, accent=(0, 0.79, 0.65)):
    np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    x = np.linspace(0, 1, 80)
    y = np.linspace(0, 1, 45)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(3 * X + seed) * np.cos(2 * Y) + 0.3 * np.random.randn(*X.shape)
    cmap = LinearSegmentedColormap.from_list("bg", ["#0B1F3A", "#132D50", "#1a3a6b"])
    ax.contourf(X, Y, Z, levels=40, cmap=cmap, alpha=0.95)
    for _ in range(40):
        ax.plot(
            [np.random.rand(), np.random.rand()],
            [np.random.rand(), np.random.rand()],
            color=(*accent, 0.15),
            lw=np.random.uniform(0.3, 1.2),
        )
    ax.add_patch(plt.Circle((0.85, 0.2), 0.25, color=(*accent, 0.08)))
    return fig, ax


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    configs = [
        ("bg_cover.png", 1, (0, 0.79, 0.65)),
        ("bg_section_01.png", 2, (0.22, 0.74, 0.97)),
        ("bg_section_02.png", 3, (0, 0.79, 0.65)),
        ("bg_section_03.png", 4, (0.96, 0.62, 0.04)),
        ("bg_section_04.png", 5, (0.66, 0.55, 0.98)),
        ("bg_section_05.png", 6, (0, 0.79, 0.65)),
        ("bg_thanks.png", 7, (0.22, 0.74, 0.97)),
    ]
    for fname, seed, accent in configs:
        fig, ax = mesh_bg(seed, accent)
        # dark overlay for text readability
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="#0B1F3A", alpha=0.35))
        if "cover" in fname or "thanks" in fname:
            ax.add_patch(plt.Rectangle((0, 0), 0.55, 1, color="#0B1F3A", alpha=0.5))
        save(fname)
    print(f"Backgrounds saved to {OUT}")


if __name__ == "__main__":
    main()
