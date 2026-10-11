from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class CarPredictionRequest(BaseModel):
    """Request para tasación y valuación comercial de vehículos usados"""
    present_price: float = Field(..., description="Precio nuevo en agencia (en Lakhs indios, ref ~1,200 USD c/u)", example=9.54)
    kms_driven: int = Field(..., description="Kilometraje total recorrido", example=43000)
    anio: Optional[int] = Field(None, description="Año de fabricación", example=2018)
    year: Optional[int] = Field(None, description="Año alternativo (en inglés)", example=2018)
    fuel_type: str = Field("Diesel", description="Tipo de combustible: Diesel, Petrol, CNG", example="Diesel")
    seller_type: str = Field("Dealer", description="Canal de venta: Dealer o Individual", example="Dealer")
    transmission: str = Field("Manual", description="Transmisión: Manual o Automatic", example="Manual")
    owner: int = Field(0, description="Número de propietarios anteriores (0, 1, 2...)", example=0)

class CarPredictionResponse(BaseModel):
    """Response con tasación de mercado y análisis de depreciación"""
    success: bool = Field(True, description="Inferencia exitosa")
    precio_estimado_usd: float = Field(..., description="Valor proyectado en dólares estadounidenses")
    precio_estimado_lakhs: float = Field(..., description="Valor calculado en Lakhs")
    antiguedad_anios: int = Field(..., description="Antigüedad del vehículo en años")
    confidence: float = Field(..., description="Confianza estadística de la tasación (0-100%)")
    depreciation_percentage: float = Field(..., description="Porcentaje de depreciación acumulado")
    price_tier: str = Field(..., description="Segmento comercial (Económico, Gama Media, Alta Gama)")
    market_context: Dict[str, Any] = Field(..., description="Contexto de kilometraje, depreciación anual y transmisión")
    interpretation: str = Field(..., description="Interpretación detallada en lenguaje natural")
    model_info: Dict[str, Any] = Field(..., description="Metadatos del modelo")

class CarHealthResponse(BaseModel):
    """Health check del modelo de tasación de autos"""
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(..., description="Número de variables de entrada")
    supported_fuel_types: List[str] = Field(["Diesel", "Petrol", "CNG"], description="Combustibles admitidos")
    supported_transmissions: List[str] = Field(["Manual", "Automatic"], description="Transmisiones admitidas")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="R2, MAE y RMSE del modelo")

class CarOptionsResponse(BaseModel):
    fuel_types: List[str]
    seller_types: List[str]
    transmissions: List[str]
