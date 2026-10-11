from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.stroke_api_models import (
    StrokePredictionRequest,
    StrokePredictionResponse,
    StrokeHealthResponse,
    StrokeOptionsResponse
)

router = APIRouter(prefix="/stroke", tags=["🧠 Salud (Riesgo de ACV / Stroke)"])

def _detect_risk_factors(payload: StrokePredictionRequest) -> List[str]:
    factors = []
    if payload.age >= 60.0:
        factors.append(f"Edad de riesgo ({payload.age:.0f} años)")
    if payload.hypertension == 1:
        factors.append("Hipertensión arterial diagnosticada")
    if payload.heart_disease == 1:
        factors.append("Antecedente de cardiopatía previa")
    if payload.avg_glucose_level >= 140.0:
        factors.append(f"Nivel de glucosa elevado ({payload.avg_glucose_level:.1f} mg/dL)")
    if payload.bmi >= 30.0:
        factors.append(f"Índice de masa corporal en rango de obesidad ({payload.bmi:.1f} BMI)")
    if payload.smoking_status in ["smokes", "formerly smoked"]:
        factors.append(f"Historial de tabaquismo ({payload.smoking_status})")
    
    if not factors:
        factors.append("No se detectaron factores de comorbilidad críticos")
    return factors

def _calculate_stroke_confidence(prob: float) -> float:
    score = 72.0 + (abs(prob - 20.0) * 0.5)
    return round(min(max(score, 60.0), 94.0), 1)

def _execute_prediction(payload: StrokePredictionRequest) -> StrokePredictionResponse:
    raw_res = ml_service.predict_stroke(
        age=payload.age,
        hypertension=payload.hypertension,
        heart_disease=payload.heart_disease,
        avg_glucose_level=payload.avg_glucose_level,
        bmi=payload.bmi,
        gender=payload.gender or "Male",
        ever_married=payload.ever_married or "Yes",
        work_type=payload.work_type or "Private",
        residence_type=payload.residence_type or "Urban",
        smoking_status=payload.smoking_status or "smokes"
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error calculando riesgo clínico"))

    prob = float(raw_res["probabilidad_evento_vascular"])
    alerta = bool(raw_res["alerta_stroke"])
    diagnostico = str(raw_res["diagnostico"])
    recomendacion = str(raw_res["recomendacion"])
    confidence = _calculate_stroke_confidence(prob)
    factors = _detect_risk_factors(payload)

    if prob >= 15.0 or alerta:
        clinical_risk = "Riesgo Elevado / Alerta Médica"
    elif prob >= 7.0:
        clinical_risk = "Riesgo Moderado / Monitoreo Clínico Preventivo"
    else:
        clinical_risk = "Riesgo Basal / Control Preventivo Estándar"

    interpretation = (
        f"Evaluación preventiva completada: {diagnostico} con una probabilidad estimada de evento vascular "
        f"del {prob:.1f}%. Factores detectados: {', '.join(factors)}. {recomendacion}"
    )

    pkg = ml_service.models.get("stroke", {})

    return StrokePredictionResponse(
        success=True,
        alerta_stroke=alerta,
        diagnostico=diagnostico,
        probabilidad_evento_vascular=prob,
        recomendacion=recomendacion,
        confidence=confidence,
        clinical_risk=clinical_risk,
        risk_factors_detected=factors,
        interpretation=interpretation,
        model_info={
            "model_type": "Evaluación de Riesgo de ACV",
            "features_used": len(pkg.get("features", [])),
            "age": payload.age,
            "hypertension": payload.hypertension,
            "glucose": payload.avg_glucose_level
        }
    )

@router.post("/predict", response_model=StrokePredictionResponse)
def predict_stroke_risk(payload: StrokePredictionRequest):
    """Evalúa variables clínicas preventivas y estratifica el riesgo de ACV"""
    return _execute_prediction(payload)

@router.post("", response_model=StrokePredictionResponse)
def predict_stroke_root(payload: StrokePredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=StrokeHealthResponse)
def stroke_health_check():
    """Health check específico del modelo de salud preventiva"""
    pkg = ml_service.models.get("stroke")
    if not pkg:
        return StrokeHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            supported_genders=[],
            model_metrics=None
        )

    return StrokeHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        supported_genders=["Male", "Female"],
        model_metrics=pkg.get("metrics")
    )

@router.get("/options", response_model=StrokeOptionsResponse)
def get_stroke_options():
    """Retorna las opciones soportadas para variables categóricas"""
    return StrokeOptionsResponse(
        work_types=["Private", "Self-employed", "Govt_job", "children", "Never_worked"],
        smoking_statuses=["formerly smoked", "never smoked", "smokes", "Unknown"],
        residence_types=["Urban", "Rural"]
    )
