from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.hepatitis_api_models import (
    HepatitisPredictionRequest,
    HepatitisPredictionResponse,
    HepatitisHealthResponse
)

router = APIRouter(prefix="/hepatitis", tags=["🧪 Hepatitis C (Diagnóstico de Laboratorio)"])

def _execute_prediction(payload: HepatitisPredictionRequest) -> HepatitisPredictionResponse:
    raw_res = ml_service.predict_hepatitis(
        age=payload.age,
        sex=payload.sex,
        alb=payload.alb,
        alp=payload.alp,
        alt=payload.alt,
        ast=payload.ast,
        bil=payload.bil,
        che=payload.che,
        chol=payload.chol,
        crea=payload.crea,
        ggt=payload.ggt,
        prot=payload.prot
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error diagnosticando Hepatitis C"))

    return HepatitisPredictionResponse(
        success=True,
        patologia_detectada=bool(raw_res["patologia_detectada"]),
        diagnostico=str(raw_res["diagnostico"]),
        probabilidad_patologia=float(raw_res["probabilidad_patologia"]),
        confidence=float(raw_res["confidence"]),
        recomendacion=str(raw_res["recomendacion"]),
        metricas_modelo=raw_res.get("metricas")
    )

@router.post("/predict", response_model=HepatitisPredictionResponse)
def predict_hepatitis_endpoint(payload: HepatitisPredictionRequest):
    """Diagnóstico predictivo de Hepatitis C basado en biomarcadores hepáticos séricos"""
    return _execute_prediction(payload)

@router.post("", response_model=HepatitisPredictionResponse)
def predict_hepatitis_root(payload: HepatitisPredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=HepatitisHealthResponse)
def hepatitis_health():
    """Health check del modelo de Hepatitis C"""
    pkg = ml_service.models.get("hepatitis")
    if not pkg:
        return HepatitisHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            model_metrics=None
        )

    return HepatitisHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        model_metrics=pkg.get("metrics")
    )
