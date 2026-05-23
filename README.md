<h1 align="center">Türkiye Saatlik Elektrik Tüketim Tahmini</h1>

<p align="center">
  <img src="assets/backgrounds/bg_cover.png" width="800" alt="MEE344 G05 — STLF banner"/>
  <br><br>
  <strong>Decision Tree + AdaBoost · Test R² ≈ 0.95 · RMSE ≈ 1040 MWh · MAPE ≈ 1.67%</strong>
</p>

<p align="center">
  <a href="https://mee344-g05-stlf.vercel.app"><img src="https://img.shields.io/badge/Live%20Demo-Vercel-00C9A7?style=flat-square" alt="Live Demo"/></a>
  <a href="https://github.com/XGami/mee344-g05-stlf"><img src="https://img.shields.io/badge/GitHub-Repo-0B1F3A?style=flat-square&logo=github" alt="GitHub"/></a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=flat-square" alt="sklearn"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT"/>
</p>

**MEE344 Makine Öğrenmesi — Grup G05** · EPİAŞ gerçek zamanlı üretim + tüketim (31.07.2025 – 29.10.2025)

## 30 saniyede demo

```bash
# Windows
run.bat

# veya manuel
py -3 -m pip install -r requirements.txt
py -3 scripts/run_server.py
```

→ **http://127.0.0.1:8000** — backtest grafiği + 24 saat ileri tahmin

## Ne yapıyor?

Saatlik **elektrik tüketimini (MWh)** tahmin eder. Geçmiş tüketim lag’leri, döngüsel zaman özellikleri, tatil bayrakları ve üretim kaynakları (rüzgar, güneş, termik vb.) kullanılır.

```mermaid
flowchart TB
  subgraph data [Veri]
    CSV[EPİAŞ CSV]
    FE[26 feature]
  end
  subgraph models [Modeller]
    DT[Decision Tree]
    AB[AdaBoost]
  end
  CSV --> FE --> DT
  FE --> AB
  AB --> WEB[FastAPI + Chart.js]
```

## Ekran görüntüleri

| Ana sayfa | Backtest | İleri tahmin |
|-----------|----------|--------------|
| ![overview](assets/screenshots/web_overview.png) | ![backtest](assets/screenshots/web_backtest.png) | ![forecast](assets/screenshots/web_forecast.png) |

## Sonuçlar (hold-out test)

| Model | RMSE (MWh) | R² | MAPE |
|-------|------------|-----|------|
| **AdaBoost** | **1040** | **0.951** | **1.67%** |
| Decision Tree | 1311 | 0.923 | 2.38% |
| Baseline (168h) | 1489 | 0.900 | 2.49% |

Detay: [`reports/metrics.json`](reports/metrics.json) · Rapor: [`reports/final_report.md`](reports/final_report.md)

## Hızlı başlangıç

```bash
git clone https://github.com/XGami/mee344-g05-stlf.git
cd mee344-g05-stlf
py -3 -m pip install -r requirements.txt
py -3 scripts/run_all.py          # veri + eğitim + figürler + pptx
py -3 scripts/run_server.py       # web
```

Ham CSV’ler `data/raw/` içinde olmalı (repo ile birlikte veya EPİAŞ export).

## Proje yapısı

```
mee344-g05-stlf/
├── api/              # Vercel serverless
├── web/              # FastAPI + static UI
├── public/           # Vercel static frontend
├── src/mee344_g05/   # Python paketi
├── scripts/          # Pipeline + sunum + sunucu
├── models/           # Eğitilmiş joblib
├── reports/          # Metrikler + figürler
├── slides/           # G05_STLF_DT_AdaBoost.pptx
├── assets/           # Arka planlar + ekran görüntüleri
└── docs/             # DEMO, DEPLOY, HOW_IT_WORKS, QA
```

## Grup

Berhan Kaya · Ahmet Bayram Topçu · Yusuf Duman · Furkan Efe Demirbel · Tekgül Eroğlu

## Lisans

[MIT](LICENSE)

## Dokümantasyon

- [Web demo](docs/DEMO.md)
- [Model açıklaması](docs/HOW_IT_WORKS.md)
- [Vercel deploy](docs/DEPLOY_VERCEL.md)
- [Sunum Q&A](docs/QA_PREP.md)
