from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.churn_api_models import (
    ChurnPredictionRequest,
    ChurnPredictionResponse,
    ChurnHealthResponse,
    ChurnOptionsResponse
)

router = APIRouter(prefix="/churn", tags=["👥 Retención de Clientes (Churn)"])

def _calculate_churn_confidence(probability: float) -> float:
    distance_from_50 = abs(probability - 50.0)
    score = 68.0 + (distance_from_50 * 0.55)
    return round(min(max(score, 60.0), 96.0), 1)

def _execute_prediction(payload: ChurnPredictionRequest) -> ChurnPredictionResponse:
    raw_res = ml_service.predict_churn(
        tenure=payload.tenure,
        monthly_charges=payload.monthly_charges,
        total_charges=payload.total_charges,
        contract=payload.contract or "Month-to-month",
        internet_service=payload.internet_service or "Fiber optic",
        tech_support=payload.tech_support or "No",
        online_security=payload.online_security or "No",
        paperless_billing=payload.paperless_billing or "Yes",
        payment_method=payload.payment_method or "Electronic check",
        senior=payload.senior or 0,
        partner=payload.partner or "No"
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error calculando riesgo de fuga"))

    prob = float(raw_res["probabilidad_cancelacion"])
    en_riesgo = bool(raw_res["en_riesgo_churn"])
    diagnostico = str(raw_res["diagnostico"])
    recomendacion = str(raw_res["recomendacion"])
    confidence = _calculate_churn_confidence(prob)

    if prob >= 70.0:
        level = "Crítico / Alta Probabilidad de Fuga Inminente"
        tactics = [
            "Ofrecer descuento del 20% al migrar a contrato anual de permanencia.",
            "Asignar soporte técnico prémium gratuito durante los primeros 6 meses.",
            "Contacto proactivo directo del equipo de Customer Success en menos de 48 horas."
        ]
    elif prob >= 40.0:
        level = "Moderado / Requiere Monitoreo Preventivo"
        tactics = [
            "Enviar encuesta breve de satisfacción para detectar fricciones de servicio.",
            "Ofrecer beneficios o bonificación en servicios complementarios (seguridad online).",
            "Monitorear reclamos de facturación del último período."
        ]
    else:
        level = "Bajo / Cliente Fidelizado y Estable"
        tactics = [
            "Mantener protocolo estándar de servicio y atención de calidad.",
            "Evaluar oportunidades de upgrade o servicios adicionales.",
            "Reconocer fidelidad con promociones de lealtad periódicas."
        ]

    interpretation = (
        f"El análisis de retención clasifica la cuenta como {diagnostico} con una probabilidad de cancelación "
        f"del {prob:.1f}%. Diagnóstico de riesgo: {level}. {recomendacion}"
    )

    pkg = ml_service.models.get("churn", {})

    return ChurnPredictionResponse(
        success=True,
        en_riesgo_churn=en_riesgo,
        diagnostico=diagnostico,
        probabilidad_cancelacion=prob,
        recomendacion=recomendacion,
        confidence=confidence,
        risk_level=level,
        retention_tactics=tactics,
        interpretation=interpretation,
        model_info={
            "model_type": "Análisis de Retención de Clientes",
            "features_used": len(pkg.get("features", [])),
            "tenure_months": payload.tenure,
            "contract": payload.contract,
            "monthly_charges": payload.monthly_charges
        }
    )

@router.post("/predict", response_model=ChurnPredictionResponse)
def predict_churn_risk(payload: ChurnPredictionRequest):
    """Evalúa la probabilidad de deserción del cliente y sugiere tácticas de fidelización"""
    return _execute_prediction(payload)

@router.post("", response_model=ChurnPredictionResponse)
def predict_churn_root(payload: ChurnPredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=ChurnHealthResponse)
def churn_health_check():
    """Health check específico del modelo de clientes"""
    pkg = ml_service.models.get("churn")
    if not pkg:
        return ChurnHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            contracts_supported=[],
            model_metrics=None
        )

    return ChurnHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        contracts_supported=["Month-to-month", "One year", "Two year"],
        model_metrics=pkg.get("metrics")
    )

@router.get("/options", response_model=ChurnOptionsResponse)
def get_churn_options():
    """Retorna las opciones soportadas para formularios o interfaces frontend"""
    return ChurnOptionsResponse(
        contracts=["Month-to-month", "One year", "Two year"],
        internet_services=["Fiber optic", "DSL", "No"],
        payment_methods=["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
    )
