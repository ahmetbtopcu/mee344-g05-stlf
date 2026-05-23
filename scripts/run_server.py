#!/usr/bin/env python3
"""Yerel geliştirme sunucusu — http://127.0.0.1:8000"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    from web.server import main

    main()
