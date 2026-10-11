from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.avocado_api_models import (
    AvocadoPredictionRequest,
    AvocadoPredictionResponse,
    AvocadoHealthResponse,
    AvocadoRegionsResponse,
    AvocadoTypesResponse
)

router = APIRouter(prefix="/aguacate", tags=["🥑 Aguacate (Proyección de Precios)"])

def _categorize_price(price: float, is_organic: bool) -> str:
    if is_organic:
        if price < 1.40: return "Accesible / Económico"
        elif price <= 2.20: return "Moderado / Estándar"
        else: return "Alto / Premium"
    else:
        if price < 1.00: return "Accesible / Económico"
        elif price <= 1.60: return "Moderado / Estándar"
        else: return "Alto / Premium"

def _get_market_context(month: int, region: str, avocado_type: str) -> Dict[str, Any]:
    seasons = {
        (12, 1, 2): "Invierno",
        (3, 4, 5): "Primavera",
        (6, 7, 8): "Verano",
        (9, 10, 11): "Otoño"
    }
    season = "Desconocida"
    for months_tuple, s_name in seasons.items():
        if month in months_tuple:
            season = s_name
            break

    return {
        "region": region,
        "season": season,
        "month": month,
        "type": avocado_type,
        "demand_period": "Alta demanda" if month in [5, 6, 7, 11, 12] else "Demanda regular",
        "harvest_season": "Período de cosecha activo" if month in [3, 4, 5, 9, 10] else "Suministro de reserva"
    }

def _calculate_confidence(prediction: float, month: int, is_organic: bool) -> float:
    score = 80.0
    if 0.70 <= prediction <= 2.80:
        score += 8.0
    elif prediction > 3.0 or prediction < 0.5:
        score -= 10.0
    if month in [3, 4, 5, 9, 10]:
        score += 4.0
    if not is_organic:
        score += 3.0
    return round(min(max(score, 45.0), 96.0), 1)

def _execute_prediction(payload: AvocadoPredictionRequest) -> AvocadoPredictionResponse:
    # Resolver fecha, año y mes
    year = payload.year or 2026
    month = payload.month or 9
    if payload.date:
        try:
            dt = datetime.strptime(payload.date, "%Y-%m-%d")
            year = dt.year
            month = dt.month
        except Exception:
            pass

    # Resolver tipo de cultivo
    if payload.is_organic is not None:
        is_organic = 1 if payload.is_organic == 1 else 0
    else:
        is_organic = 1 if (payload.type and payload.type.lower() == "organic") else 0

    tipo_str = "Orgánico" if is_organic == 1 else "Convencional"
    region_str = payload.region or "California"

    raw_res = ml_service.predict_aguacate(
        total_volume=payload.total_volume or 75000.0,
        plu_4046=payload.plu_4046 or 15000.0,
        plu_4225=payload.plu_4225 or 20000.0,
        plu_4770=payload.plu_4770 or 1000.0,
        total_bags=payload.total_bags or 14000.0,
        small_bags=payload.small_bags or 10000.0,
        large_bags=payload.large_bags or 3800.0,
        xlarge_bags=payload.xlarge_bags or 200.0,
        year=year,
        month=month,
        is_organic=is_organic,
        region=region_str
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error calculando proyección"))

    precio = float(raw_res["precio_unitario_usd"])
    confidence = _calculate_confidence(precio, month, is_organic == 1)
    category = _categorize_price(precio, is_organic == 1)
    context = _get_market_context(month, region_str, tipo_str)

    interpretation = (
        f"Se proyecta un precio estimado de ${precio:.2f} USD por unidad para aguacate {tipo_str} "
        f"en {region_str} durante {context['season'].lower()}. Este nivel de precio se considera {category.lower()} "
        f"para el ciclo de mercado correspondiente."
    )

    pkg = ml_service.models.get("aguacate", {})

    return AvocadoPredictionResponse(
        success=True,
        prediction=precio,
        precio_unitario_usd=precio,
        precio_estimado_usd=precio,
        tipo_cultivo=tipo_str,
        region=region_str,
        confidence=confidence,
        price_category=category,
        market_context=context,
        interpretation=interpretation,
        model_info={
            "model_type": "Proyección de Precio del Aguacate",
            "features_used": len(pkg.get("features", [])),
            "region": region_str,
            "type": tipo_str,
            "year": year,
            "month": month
        }
    )

@router.post("/predict", response_model=AvocadoPredictionResponse)
def predict_avocado_price(payload: AvocadoPredictionRequest):
    """Realiza la proyección del precio del aguacate con contexto de mercado y confianza"""
    return _execute_prediction(payload)

@router.post("", response_model=AvocadoPredictionResponse)
def predict_avocado_root(payload: AvocadoPredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=AvocadoHealthResponse)
def avocado_health_check():
    """Health check específico del modelo de aguacate"""
    pkg = ml_service.models.get("aguacate")
    if not pkg:
        return AvocadoHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            supported_regions=[],
            supported_types=[],
            model_metrics=None
        )

    features = pkg.get("features", [])
    regions = [f.replace("region_", "") for f in features if f.startswith("region_")]

    return AvocadoHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(features),
        supported_regions=regions,
        supported_types=["Orgánico (organic)", "Convencional (conventional)"],
        model_metrics=pkg.get("metrics")
    )

@router.get("/regions", response_model=AvocadoRegionsResponse)
def get_avocado_regions():
    """Retorna la lista de todas las regiones geográficas soportadas por el modelo"""
    pkg = ml_service.models.get("aguacate", {})
    features = pkg.get("features", [])
    regions = [f.replace("region_", "") for f in features if f.startswith("region_")]
    if not regions:
        regions = ["California", "NewYork", "Chicago", "LosAngeles", "Plains", "Southeast", "West"]
    return AvocadoRegionsResponse(supported_regions=regions)

@router.get("/types", response_model=AvocadoTypesResponse)
def get_avocado_types():
    """Retorna los tipos de cultivo soportados"""
    return AvocadoTypesResponse(supported_types=["conventional", "organic"])
