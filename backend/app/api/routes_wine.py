from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.wine_api_models import (
    WinePredictionRequest,
    WinePredictionResponse,
    WineHealthResponse
)

router = APIRouter(prefix="/vino", tags=["🍷 Vino (Calidad Enológica)"])

def _evaluate_sensory_balance(alcohol: float, fixed_acidity: float, residual_sugar: float) -> Dict[str, Any]:
    if alcohol < 11.0:
        alc_txt = "Ligero / Graduación baja"
    elif alcohol <= 13.5:
        alc_txt = "Equilibrado y redondo"
    else:
        alc_txt = "Cálido / Estructura robusta"

    if fixed_acidity < 6.5:
        acid_txt = "Acidez suave / Madura"
    elif fixed_acidity <= 8.5:
        acid_txt = "Frescura y vivacidad óptimas"
    else:
        acid_txt = "Alta acidez / Marcada frescura"

    if residual_sugar < 4.0:
        sugar_txt = "Seco (Dry)"
    elif residual_sugar < 12.0:
        sugar_txt = "Semiseco (Medium-dry)"
    else:
        sugar_txt = "Semidulce / Dulce"

    return {
        "alcohol_profile": alc_txt,
        "acidity_profile": acid_txt,
        "sweetness_profile": sugar_txt
    }

def _calculate_confidence(probability: float) -> float:
    # A mayor distancia del umbral del 50%, mayor certeza en la clasificación
    distance_from_50 = abs(probability - 50.0)
    score = 65.0 + (distance_from_50 * 0.6)
    return round(min(max(score, 60.0), 96.0), 1)

def _execute_prediction(payload: WinePredictionRequest) -> WinePredictionResponse:
    raw_res = ml_service.predict_vino(
        fixed_acidity=payload.fixed_acidity,
        volatile_acidity=payload.volatile_acidity,
        citric_acid=payload.citric_acid,
        residual_sugar=payload.residual_sugar,
        chlorides=payload.chlorides,
        free_sulfur_dioxide=payload.free_sulfur_dioxide,
        total_sulfur_dioxide=payload.total_sulfur_dioxide,
        density=payload.density,
        ph=payload.ph,
        sulphates=payload.sulphates,
        alcohol=payload.alcohol,
        is_red=payload.is_red
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error evaluando vino"))

    prob = float(raw_res["probabilidad_alta_calidad"])
    calidad_alta = bool(raw_res["calidad_alta"])
    diagnostico = str(raw_res["diagnostico"])
    confidence = _calculate_confidence(prob)
    balance = _evaluate_sensory_balance(payload.alcohol, payload.fixed_acidity, payload.residual_sugar)

    if prob >= 75.0:
        tier = "Gran Reserva / Premium Certificado"
    elif prob >= 50.0:
        tier = "Selección Especial / Alta Calidad"
    elif prob >= 35.0:
        tier = "Cosecha Estándar / Calidad Comercial"
    else:
        tier = "Calidad Básica / Requiere Ajustes Enológicos"

    tipo_vino = "Tinto" if payload.is_red == 1 else "Blanco"
    interpretation = (
        f"El examen enológico dictamina un vino {tipo_vino} clasificado como {diagnostico} "
        f"con {prob:.1f}% de certidumbre. Presenta un perfil de alcohol {balance['alcohol_profile'].lower()}, "
        f"acidez {balance['acidity_profile'].lower()} y dulzor {balance['sweetness_profile'].lower()}."
    )

    pkg = ml_service.models.get("vino", {})

    return WinePredictionResponse(
        success=True,
        calidad_alta=calidad_alta,
        diagnostico=diagnostico,
        probabilidad_alta_calidad=prob,
        confidence=confidence,
        quality_tier=tier,
        sensory_balance=balance,
        interpretation=interpretation,
        model_info={
            "model_type": "Evaluación de Calidad de Vino",
            "features_used": len(pkg.get("features", [])),
            "wine_type": tipo_vino,
            "alcohol": payload.alcohol,
            "ph": payload.ph
        }
    )

@router.post("/predict", response_model=WinePredictionResponse)
def predict_wine_quality(payload: WinePredictionRequest):
    """Evalúa las características químicas y clasifica la calidad del vino"""
    return _execute_prediction(payload)

@router.post("", response_model=WinePredictionResponse)
def predict_wine_root(payload: WinePredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=WineHealthResponse)
def wine_health_check():
    """Health check específico del modelo enológico"""
    pkg = ml_service.models.get("vino")
    if not pkg:
        return WineHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            wine_types=[],
            model_metrics=None
        )

    return WineHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        wine_types=["Vino Blanco (is_red=0)", "Vino Tinto (is_red=1)"],
        model_metrics=pkg.get("metrics")
    )
