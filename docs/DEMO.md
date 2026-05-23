# Web demo — nasıl açılır?

## Hızlı (tek komut)

**Windows:** `run.bat`  
**Linux/macOS:** `chmod +x run.sh && ./run.sh`

Tarayıcıda: **http://127.0.0.1:8000**

## Manuel

```bash
cd mee344-g05-stlf
py -3 -m pip install -r requirements.txt
py -3 scripts/run_server.py
```

Modeller yoksa önce:

```bash
py -3 scripts/run_all.py
```

## Arayüz özellikleri

| Özellik | Açıklama |
|---------|----------|
| KPI kartları | Test RMSE, R², MAPE (AdaBoost) — sayaç animasyonu |
| Backtest | Son 48 saat gerçek vs DT / AdaBoost |
| İleri tahmin | 12 / 24 / 48 saat forecast |
| Tema | Açık / koyu (localStorage) |
| API | `/docs` — Swagger |

## Vercel (canlı)

Bkz. [DEPLOY_VERCEL.md](DEPLOY_VERCEL.md). Statik arayüz `public/`; API `api/index.py`.
