# Yerel çalıştırma ve Vercel deploy

## 1) Yerel web sunucusu

```powershell
cd mee344-g05-stlf
py -3 -m pip install -r requirements.txt
py -3 scripts/run_server.py
```

Tarayıcı: **http://127.0.0.1:8000**

- Ana sayfa: grafik + backtest + 24s ileri tahmin
- API: http://127.0.0.1:8000/docs

## 2) Vercel’e deploy (hazır olduğunda)

### Ön koşul

- [Vercel CLI](https://vercel.com/docs/cli): `npm i -g vercel`
- Proje kökünde modeller ve `data/processed/` mevcut olmalı

### İlk deploy

```powershell
cd mee344-g05-stlf
vercel login
vercel
```

Sorular: proje adı, root = `.` (mee344-g05-stlf)

### Production

```powershell
vercel --prod
```

### Yapı

| Path | Ne |
|------|-----|
| `public/index.html` | Statik arayüz |
| `api/index.py` | FastAPI (tahmin API) |
| `vercel.json` | Rewrite + 3GB RAM function |

### Notlar

- **Cold start:** İlk istek 10–30 sn sürebilir (sklearn + model yükleme).
- **Boyut:** `adaboost.joblib` ~6 MB — Vercel limitleri içinde.
- **Canlı EPİAŞ:** Şu an CSV/parquet; gerçek zamanlı feed için ayrı cron + `/api/reload` gerekir.

### Sorun giderme

| Sorun | Çözüm |
|-------|--------|
| 404 `/api/forecast` | `vercel.json` rewrites kontrol |
| 500 function | Vercel Logs → `models/` ve `data/processed/` deploy’da mı? |
| CORS | Zaten `*` açık |
