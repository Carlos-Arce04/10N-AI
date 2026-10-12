from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.sp500_api_models import (
    SP500PredictionRequest,
    SP500PredictionResponse,
    SP500HealthResponse
)

router = APIRouter(prefix="/sp500", tags=["📈 S&P 500 (Predicción Bursátil de Acciones)"])

def _execute_prediction(payload: SP500PredictionRequest) -> SP500PredictionResponse:
    raw_res = ml_service.predict_sp500(
        open=payload.open,
        high=payload.high,
        low=payload.low,
        volume=payload.volume
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error calculando proyección de S&P 500"))

    return SP500PredictionResponse(
        success=True,
        precio_cierre_usd=float(raw_res["precio_cierre_usd"]),
        variacion_proyectada_pct=float(raw_res["variacion_proyectada_pct"]),
        tendencia=str(raw_res["tendencia"]),
        rango_volatilidad_usd=float(raw_res["rango_volatilidad_usd"]),
        confidence=float(raw_res["confidence"]),
        interpretacion=str(raw_res["interpretacion"]),
        metricas_modelo=raw_res.get("metricas")
    )

@router.post("/predict", response_model=SP500PredictionResponse)
def predict_sp500_endpoint(payload: SP500PredictionRequest):
    """Estima el precio de cierre bursátil de una acción del S&P 500"""
    return _execute_prediction(payload)

@router.post("", response_model=SP500PredictionResponse)
def predict_sp500_root(payload: SP500PredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=SP500HealthResponse)
def sp500_health():
    """Health check del modelo de S&P 500"""
    pkg = ml_service.models.get("sp500")
    if not pkg:
        return SP500HealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            model_metrics=None
        )

    return SP500HealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        model_metrics=pkg.get("metrics")
    )
