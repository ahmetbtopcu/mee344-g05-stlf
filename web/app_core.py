"""FastAPI app factory — local (uvicorn) ve Vercel (serverless) için ortak."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mee344_g05.config import REPORTS_DIR
from mee344_g05.inference import STLFPredictor

STATIC = Path(__file__).parent / "static"
PUBLIC = ROOT / "public"

predictor: STLFPredictor | None = None


def get_predictor() -> STLFPredictor:
    global predictor
    if predictor is None:
        predictor = STLFPredictor()
    return predictor


class ForecastRequest(BaseModel):
    hours: int = Field(24, ge=1, le=168)


def create_app() -> FastAPI:
    app = FastAPI(
        title="G05 STLF — Canlı Tüketim Tahmini",
        description="Decision Tree + AdaBoost · EPİAŞ saatlik tüketim",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=HTMLResponse)
    def home():
        for path in (STATIC / "index.html", PUBLIC / "index.html"):
            if path.exists():
                return HTMLResponse(path.read_text(encoding="utf-8"))
        return HTMLResponse("<h1>G05 STLF</h1><p>index.html bulunamadı</p>")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "mee344-g05-stlf"}

    @app.get("/api/info")
    def info():
        return get_predictor().info()

    @app.get("/api/metrics")
    def metrics():
        path = REPORTS_DIR / "metrics.json"
        if not path.exists():
            raise HTTPException(404, "metrics.json yok — önce eğitim pipeline çalıştırın")
        return json.loads(path.read_text(encoding="utf-8"))

    @app.get("/api/actuals")
    def actuals(hours: int = Query(72, ge=1, le=500)):
        return {"hours": hours, "data": get_predictor().recent_actuals(hours)}

    @app.get("/api/backtest")
    def backtest(hours: int = Query(48, ge=1, le=336)):
        return {"hours": hours, "data": get_predictor().backtest_sample(hours)}

    @app.get("/api/predict")
    def predict_at(ts: str = Query(...)):
        try:
            return get_predictor().predict_at(ts).__dict__
        except ValueError as e:
            raise HTTPException(400, str(e)) from e

    @app.get("/api/forecast")
    def forecast(hours: int = Query(24, ge=1, le=168)):
        results = get_predictor().forecast(hours)
        return {
            "hours": hours,
            "note": "İleri saatler: üretim son saatten taşınır; tüketim zincirleme tahmin.",
            "predictions": [r.__dict__ for r in results],
        }

    @app.post("/api/forecast")
    def forecast_post(body: ForecastRequest):
        results = get_predictor().forecast(body.hours)
        return {"hours": body.hours, "predictions": [r.__dict__ for r in results]}

    @app.post("/api/reload")
    def reload_data():
        global predictor
        predictor = STLFPredictor()
        return {"status": "reloaded", **predictor.info()}

    return app


app = create_app()
