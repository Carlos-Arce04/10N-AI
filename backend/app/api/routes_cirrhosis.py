from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.cirrhosis_api_models import (
    CirrhosisPredictionRequest,
    CirrhosisPredictionResponse,
    CirrhosisHealthResponse
)

router = APIRouter(prefix="/cirrosis", tags=["🏥 Cirrosis Hepática (Estadificación Clínica)"])

def _execute_prediction(payload: CirrhosisPredictionRequest) -> CirrhosisPredictionResponse:
    raw_res = ml_service.predict_cirrosis(
        n_days=payload.n_days,
        age_years=payload.age_years,
        sex=payload.sex,
        bilirubin=payload.bilirubin,
        cholesterol=payload.cholesterol,
        albumin=payload.albumin,
        copper=payload.copper,
        alk_phos=payload.alk_phos,
        sgot=payload.sgot,
        tryglicerides=payload.tryglicerides,
        platelets=payload.platelets,
        prothrombin=payload.prothrombin,
        drug=payload.drug,
        ascites=payload.ascites,
        hepatomegaly=payload.hepatomegaly,
        spiders=payload.spiders,
        edema=payload.edema,
        status=payload.status
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error clasificando estadio de cirrosis"))

    return CirrhosisPredictionResponse(
        success=True,
        estadio_predicho=int(raw_res["estadio_predicho"]),
        nombre_estadio=str(raw_res["nombre_estadio"]),
        severidad=str(raw_res["severidad"]),
        probabilidades_estadios=raw_res["probabilidades_estadios"],
        confidence=float(raw_res["confidence"]),
        interpretacion=str(raw_res["interpretacion"]),
        metricas_modelo=raw_res.get("metricas")
    )

@router.post("/predict", response_model=CirrhosisPredictionResponse)
def predict_cirrosis_endpoint(payload: CirrhosisPredictionRequest):
    """Clasificación histológica y estimación del estadio de cirrosis (Estadios 1 al 4)"""
    return _execute_prediction(payload)

@router.post("", response_model=CirrhosisPredictionResponse)
def predict_cirrosis_root(payload: CirrhosisPredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=CirrhosisHealthResponse)
def cirrosis_health():
    """Health check del modelo de cirrosis hepática"""
    pkg = ml_service.models.get("cirrosis")
    if not pkg:
        return CirrhosisHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            model_metrics=None
        )

    return CirrhosisHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        model_metrics=pkg.get("metrics")
    )
