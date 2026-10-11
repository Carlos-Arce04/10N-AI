from pydantic import BaseModel, Field
from typing import Dict, Optional, Literal, Any, List

class AvocadoPredictionRequest(BaseModel):
    """Request para predicción de precios de aguacate"""
    date: Optional[str] = Field("2026-09-15", description="Fecha de proyección (YYYY-MM-DD)", example="2026-09-15")
    region: str = Field("California", description="Región geográfica de mercado", example="California")
    type: Optional[Literal["conventional", "organic"]] = Field("organic", description="Tipo de cultivo", example="organic")
    
    # Compatibilidad con parámetros directos de simulación
    is_organic: Optional[int] = Field(None, description="1: Orgánico, 0: Convencional", example=1)
    year: Optional[int] = Field(None, description="Año de proyección", example=2026)
    month: Optional[int] = Field(None, description="Mes (1-12)", example=9)

    # Volúmenes y bolsas (con valores típicos por defecto)
    total_volume: Optional[float] = Field(default=75000.0, description="Volumen total de ventas", ge=0, example=75000.0)
    plu_4046: Optional[float] = Field(default=15000.0, description="Volumen PLU 4046 (pequeños)", ge=0, example=15000.0)
    plu_4225: Optional[float] = Field(default=20000.0, description="Volumen PLU 4225 (medianos/grandes)", ge=0, example=20000.0)
    plu_4770: Optional[float] = Field(default=1000.0, description="Volumen PLU 4770 (extra grandes)", ge=0, example=1000.0)
    total_bags: Optional[float] = Field(default=14000.0, description="Total de bolsas", ge=0, example=14000.0)
    small_bags: Optional[float] = Field(default=10000.0, description="Bolsas pequeñas", ge=0, example=10000.0)
    large_bags: Optional[float] = Field(default=3800.0, description="Bolsas grandes", ge=0, example=3800.0)
    xlarge_bags: Optional[float] = Field(default=200.0, description="Bolsas extra grandes", ge=0, example=200.0)

class AvocadoPredictionResponse(BaseModel):
    """Response con predicción enriquecida de precio de aguacate"""
    success: bool = Field(True, description="Indica si la inferencia fue exitosa")
    prediction: float = Field(..., description="Precio predicho por unidad en USD")
    precio_unitario_usd: float = Field(..., description="Precio unitario referencial")
    precio_estimado_usd: float = Field(..., description="Alias compatible para el frontend")
    tipo_cultivo: str = Field(..., description="Tipo de cultivo (Orgánico / Convencional)")
    region: str = Field(..., description="Región analizada")
    confidence: float = Field(..., description="Nivel de confianza de la predicción (0-100%)")
    price_category: str = Field(..., description="Categoría de precio (bajo, accesible, moderado, premium)")
    market_context: Dict[str, Any] = Field(..., description="Contexto de mercado y estacionalidad")
    interpretation: str = Field(..., description="Interpretación en lenguaje natural")
    model_info: Dict[str, Any] = Field(..., description="Metadatos del modelo")

class AvocadoHealthResponse(BaseModel):
    """Response para health check del modelo de aguacate"""
    status: str = Field("healthy", description="Estado del modelo")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(..., description="Cantidad de características")
    supported_regions: List[str] = Field(..., description="Regiones soportadas")
    supported_types: List[str] = Field(..., description="Tipos de cultivo soportados")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Métricas de evaluación del modelo")

class AvocadoRegionsResponse(BaseModel):
    supported_regions: List[str]

class AvocadoTypesResponse(BaseModel):
    supported_types: List[str]
