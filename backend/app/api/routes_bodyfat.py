from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.bodyfat_api_models import (
    BodyFatPredictionRequest,
    BodyFatPredictionResponse,
    BodyFatHealthResponse
)

router = APIRouter(prefix="/bodyfat", tags=["🏃 Grasa Corporal (Composición Antropométrica)"])

def _execute_prediction(payload: BodyFatPredictionRequest) -> BodyFatPredictionResponse:
    raw_res = ml_service.predict_bodyfat(
        age=payload.age,
        weight=payload.weight,
        height=payload.height,
        neck=payload.neck,
        chest=payload.chest,
        abdomen=payload.abdomen,
        hip=payload.hip,
        thigh=payload.thigh,
        knee=payload.knee,
        ankle=payload.ankle,
        biceps=payload.biceps,
        forearm=payload.forearm,
        wrist=payload.wrist
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error calculando grasa corporal"))

    return BodyFatPredictionResponse(
        success=True,
        grasa_corporal_pct=float(raw_res["grasa_corporal_pct"]),
        categoria=str(raw_res["categoria"]),
        rango_saludable=str(raw_res["rango_saludable"]),
        confidence=float(raw_res["confidence"]),
        interpretacion=str(raw_res["interpretacion"]),
        metricas_modelo=raw_res.get("metricas")
    )

@router.post("/predict", response_model=BodyFatPredictionResponse)
def predict_bodyfat_endpoint(payload: BodyFatPredictionRequest):
    """Estima el porcentaje de grasa corporal a partir de variables antropométricas"""
    return _execute_prediction(payload)

@router.post("", response_model=BodyFatPredictionResponse)
def predict_bodyfat_root(payload: BodyFatPredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=BodyFatHealthResponse)
def bodyfat_health():
    """Health check del modelo de estimación de grasa corporal"""
    pkg = ml_service.models.get("bodyfat")
    if not pkg:
        return BodyFatHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            model_metrics=None
        )

    return BodyFatHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        model_metrics=pkg.get("metrics")
    )
