from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ml_service import ml_service
from app.models.car_api_models import (
    CarPredictionRequest,
    CarPredictionResponse,
    CarHealthResponse,
    CarOptionsResponse
)

router = APIRouter(prefix="/auto", tags=["🚗 Autos (Tasación de Vehículos Usados)"])

def _calculate_car_confidence(vehicle_age: int, kms_driven: int) -> float:
    score = 80.0
    if 2 <= vehicle_age <= 8:
        score += 8.0
    elif vehicle_age > 12:
        score -= 10.0

    if 10000 <= kms_driven <= 90000:
        score += 5.0
    elif kms_driven > 150000:
        score -= 8.0

    return round(min(max(score, 50.0), 95.0), 1)

def _execute_prediction(payload: CarPredictionRequest) -> CarPredictionResponse:
    anio = payload.anio if payload.anio is not None else (payload.year if payload.year is not None else 2018)
    
    raw_res = ml_service.predict_auto(
        present_price=payload.present_price,
        kms_driven=payload.kms_driven,
        anio=anio,
        fuel_type=payload.fuel_type or "Petrol",
        seller_type=payload.seller_type or "Dealer",
        transmission=payload.transmission or "Manual",
        owner=payload.owner or 0
    )

    if not raw_res.get("success"):
        raise HTTPException(status_code=500, detail=raw_res.get("error", "Error calculando tasación de auto"))

    precio_usd = float(raw_res["precio_estimado_usd"])
    precio_lakhs = float(raw_res["precio_estimado_lakhs"])
    antiguedad = int(raw_res["antiguedad_anios"])

    # Cálculo de depreciación frente al precio original
    precio_nuevo_usd = float(payload.present_price) * 1200.0
    if precio_nuevo_usd > 0:
        deprec_pct = round(max(0.0, min(100.0, (1.0 - (precio_usd / precio_nuevo_usd)) * 100.0)), 1)
    else:
        deprec_pct = 0.0

    confidence = _calculate_car_confidence(antiguedad, payload.kms_driven)

    if precio_usd < 5000.0:
        tier = "Segmento Económico / Entrada"
    elif precio_usd <= 15000.0:
        tier = "Gama Media / Confort Familiar"
    else:
        tier = "Alta Gama / Ejecutivo"

    kms_por_anio = round(payload.kms_driven / max(1, antiguedad))
    context = {
        "fuel_type": payload.fuel_type,
        "transmission": payload.transmission,
        "seller_type": payload.seller_type,
        "owners": payload.owner,
        "annual_mileage_km": kms_por_anio,
        "mileage_intensity": "Uso bajo" if kms_por_anio < 10000 else ("Uso promedio" if kms_por_anio <= 20000 else "Uso intensivo")
    }

    interpretation = (
        f"Para este vehículo con {antiguedad} años de antigüedad y {payload.kms_driven:,} km acumulados "
        f"({payload.fuel_type}, transmisión {payload.transmission}), se proyecta un valor de mercado de "
        f"${precio_usd:,.2f} USD ({precio_lakhs} lakhs). Registra una depreciación estimada del {deprec_pct}% "
        f"respecto al valor de agencia."
    )

    pkg = ml_service.models.get("autos", {})

    return CarPredictionResponse(
        success=True,
        precio_estimado_usd=precio_usd,
        precio_estimado_lakhs=precio_lakhs,
        antiguedad_anios=antiguedad,
        confidence=confidence,
        depreciation_percentage=deprec_pct,
        price_tier=tier,
        market_context=context,
        interpretation=interpretation,
        model_info={
            "model_type": "Cotizador de Vehículos Usados",
            "features_used": len(pkg.get("features", [])),
            "fabrication_year": anio,
            "kms": payload.kms_driven
        }
    )

@router.post("/predict", response_model=CarPredictionResponse)
def predict_car_value(payload: CarPredictionRequest):
    """Estima el valor comercial de un vehículo usado con análisis de depreciación"""
    return _execute_prediction(payload)

@router.post("", response_model=CarPredictionResponse)
def predict_car_root(payload: CarPredictionRequest):
    """Alias raíz para compatibilidad con el simulador interactivo"""
    return _execute_prediction(payload)

@router.get("/health", response_model=CarHealthResponse)
def car_health_check():
    """Health check específico del modelo de vehículos"""
    pkg = ml_service.models.get("autos")
    if not pkg:
        return CarHealthResponse(
            status="unhealthy",
            model_loaded=False,
            features_count=0,
            supported_fuel_types=[],
            supported_transmissions=[],
            model_metrics=None
        )

    return CarHealthResponse(
        status="healthy",
        model_loaded=True,
        features_count=len(pkg.get("features", [])),
        supported_fuel_types=["Diesel", "Petrol", "CNG"],
        supported_transmissions=["Manual", "Automatic"],
        model_metrics=pkg.get("metrics")
    )

@router.get("/options", response_model=CarOptionsResponse)
def get_car_options():
    """Retorna las opciones soportadas para formularios o interfaces frontend"""
    return CarOptionsResponse(
        fuel_types=["Diesel", "Petrol", "CNG"],
        seller_types=["Dealer", "Individual"],
        transmissions=["Manual", "Automatic"]
    )
