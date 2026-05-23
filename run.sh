#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "=== MEE344 G05 STLF — tek komut kurulum ==="

if ! command -v python3 &>/dev/null; then
  echo "HATA: python3 bulunamadı."
  exit 1
fi

if [[ ! -d .venv ]]; then
  echo "Sanal ortam oluşturuluyor..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q --upgrade pip
pip install -q -r requirements.txt

if [[ ! -f models/adaboost.joblib ]]; then
  echo "Pipeline çalıştırılıyor..."
  python scripts/run_all.py
else
  echo "Modeller mevcut — pipeline atlandı."
fi

echo "Web sunucusu: http://127.0.0.1:8000"
if command -v xdg-open &>/dev/null; then xdg-open http://127.0.0.1:8000 & fi
python scripts/run_server.py
