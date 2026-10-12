from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.bitcoin_api_models import (
    BitcoinPredictionRequest,
    BitcoinPredictionResponse,
    BitcoinHealthResponse
)

router = APIRouter(prefix="/bitcoin", tags=["₿ Bitcoin (Proyección Financiera Cripto)"])

def _execute_prediction(payload: BitcoinPredictionRequest) -> BitcoinPredictionResponse:
    raw_res = ml_service.predict_bitcoin(
        open=payload.open,
        high=payload.high,
        low=payload.low,
        volume=payload.volume,
        market_cap=payload.market_cap
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error calculando proyección de Bitcoin"))

    return BitcoinPredictionResponse(
        success=True,
        precio_cierre_usd=float(raw_res["precio_cierre_usd"]),
        variacion_proyectada_pct=float(raw_res["variacion_proyectada_pct"]),
        tendencia=str(raw_res["tendencia"]),
        rango_dia_usd=float(raw_res["rango_dia_usd"]),
        confidence=float(raw_res["confidence"]),
        interpretacion=str(raw_res["interpretacion"]),
        metricas_modelo=raw_res.get("metricas")
    )

@router.post("/predict", response_model=BitcoinPredictionResponse)
def predict_bitcoin_endpoint(payload: BitcoinPredictionRequest):
    """Estima el precio de cierre de Bitcoin (BTC/USD) en función de variables de mercado"""
    return _execute_prediction(payload)

@router.post("", response_model=BitcoinPredictionResponse)
def predict_bitcoin_root(payload: BitcoinPredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=BitcoinHealthResponse)
def bitcoin_health():
    """Health check del modelo de Bitcoin"""
    pkg = ml_service.models.get("bitcoin")
    if not pkg:
        return BitcoinHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            model_metrics=None
        )

    return BitcoinHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        model_metrics=pkg.get("metrics")
    )
