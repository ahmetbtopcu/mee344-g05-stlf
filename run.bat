@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo === MEE344 G05 STLF — tek komut kurulum ===

where py >nul 2>&1
if errorlevel 1 (
  echo HATA: Python bulunamadi. py -3 veya python kurun.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Sanal ortam olusturuluyor...
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat

echo Bagimliliklar yukleniyor...
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt

if not exist "models\adaboost.joblib" (
  echo Pipeline calistiriliyor (ilk kurulum)...
  python scripts\run_all.py
) else (
  echo Modeller mevcut — pipeline atlandi. Yeniden egitmek icin: python scripts\run_all.py
)

echo Web sunucusu baslatiliyor: http://127.0.0.1:8000
start "" http://127.0.0.1:8000
python scripts\run_server.py
