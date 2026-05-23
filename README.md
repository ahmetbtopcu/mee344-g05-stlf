<h1 align="center">Türkiye Saatlik Elektrik Tüketim Tahmini</h1>

<p align="center">
  <strong>Decision Tree + AdaBoost · Test R² ≈ 0.95 · RMSE ≈ 1040 MWh · MAPE ≈ 1.67%</strong>
</p>

<p align="center">
  <a href="https://mee344-g05-stlf.vercel.app"><img src="https://img.shields.io/badge/Live%20Demo-Vercel-00C9A7?style=flat-square" alt="Live Demo"/></a>
  <a href="https://github.com/ahmetbtopcu/mee344-g05-stlf"><img src="https://img.shields.io/badge/GitHub-Repo-0B1F3A?style=flat-square&logo=github" alt="GitHub"/></a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=flat-square" alt="sklearn"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT"/>
</p>

**MEE344 Makine Öğrenmesi — Grup G05** · EPİAŞ gerçek zamanlı üretim + tüketim (31.07.2025 – 29.10.2025)

## Canlı demo

**https://mee344-g05-stlf.vercel.app** — backtest + 24 saat ileri tahmin

```bash
# Windows
run.bat

# veya
py -3 -m pip install -r requirements.txt
py -3 scripts/run_server.py
```

## Ne yapıyor?

Saatlik **elektrik tüketimini (MWh)** tahmin eder: lag özellikleri, döngüsel zaman, üretim kaynakları → **Decision Tree** + **AdaBoost**.

## Sonuçlar (hold-out test)

| Model | RMSE (MWh) | R² | MAPE |
|-------|------------|-----|------|
| **AdaBoost** | **1040** | **0.951** | **1.67%** |
| Decision Tree | 1311 | 0.923 | 2.38% |
| Baseline (168h) | 1489 | 0.900 | 2.49% |

Detay: [`reports/metrics.json`](reports/metrics.json) · Rapor: [`reports/final_report.md`](reports/final_report.md) · Sunum: [`slides/G05_STLF_DT_AdaBoost.pptx`](slides/G05_STLF_DT_AdaBoost.pptx)

## Hızlı başlangıç

```bash
git clone https://github.com/ahmetbtopcu/mee344-g05-stlf.git
cd mee344-g05-stlf
py -3 -m pip install -r requirements.txt
py -3 scripts/run_all.py    # veri + eğitim (ilk kurulum)
py -3 scripts/run_server.py
```

## Proje yapısı

```
mee344-g05-stlf/
├── api/              # Vercel serverless
├── web/ + public/    # FastAPI + arayüz
├── src/mee344_g05/   # Python paketi
├── scripts/          # Pipeline
├── models/           # Eğitilmiş modeller
├── data/raw/         # EPİAŞ CSV
├── reports/          # metrics.json, final_report.md
├── slides/           # Sunum (pptx)
└── docs/
```

## Grup

Berhan Kaya · Ahmet Bayram Topçu · Yusuf Duman · Furkan Efe Demirbel · Tekgül Eroğlu

## Lisans

[MIT](LICENSE)
