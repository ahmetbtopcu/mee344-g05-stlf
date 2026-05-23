"""Presentation design system — colors, dimensions, matplotlib style."""

from __future__ import annotations

# Brand palette (energy / grid analytics)
NAVY = "#0B1F3A"
NAVY_LIGHT = "#132D50"
TEAL = "#00C9A7"
SKY = "#38BDF8"
AMBER = "#F59E0B"
SLATE = "#64748B"
WHITE = "#FFFFFF"
OFF_WHITE = "#F8FAFC"
CARD = "#EEF2F7"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#475569"

# Matplotlib presentation style
MPL_RC = {
    "figure.facecolor": OFF_WHITE,
    "axes.facecolor": WHITE,
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": TEXT_DARK,
    "axes.titlecolor": NAVY,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "xtick.color": TEXT_MUTED,
    "ytick.color": TEXT_MUTED,
    "grid.color": "#E2E8F0",
    "grid.alpha": 0.8,
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
    "lines.linewidth": 2.0,
    "figure.dpi": 150,
}

PPT_W = 13.333  # inches 16:9
PPT_H = 7.5
HEADER_H = 0.95  # inches
MARGIN = 0.45
