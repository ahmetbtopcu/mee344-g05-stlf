"""
Vercel serverless entry — tüm /api/* istekleri bu FastAPI uygulamasına gider.
https://vercel.com/docs/functions/runtimes/python
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from web.app_core import app  # noqa: E402

# Vercel ASGI handler
app = app
