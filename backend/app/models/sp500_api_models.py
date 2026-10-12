from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class SP500PredictionRequest(BaseModel):
    """Request para predicción del precio de cierre de acciones del índice S&P 500"""
    open: float = Field(150.0, description="Precio de apertura de la acción en USD", example=150.0)
    high: float = Field(152.5, description="Precio máximo intradiario en USD", example=152.5)
    low: float = Field(149.0, description="Precio mínimo intradiario en USD", example=149.0)
    volume: float = Field(1200000.0, description="Volumen diario de acciones negociadas", example=1200000.0)

class SP500PredictionResponse(BaseModel):
    """Response con el precio de cierre estimado de la acción del S&P 500"""
    success: bool = Field(True, description="Indica si la inferencia fue exitosa")
    precio_cierre_usd: float = Field(..., description="Precio de cierre proyectado en USD")
    variacion_proyectada_pct: float = Field(..., description="Variación porcentual esperada respecto a Open (%)")
    tendencia: str = Field(..., description="Tendencia proyectada (Alcista / Bajista / Neutral)")
    rango_volatilidad_usd: float = Field(..., description="Rango de volatilidad del día (High - Low) en USD")
    confidence: float = Field(..., description="Nivel de confianza estadística del modelo (%)")
    interpretacion: str = Field(..., description="Lectura bursátil y resumen técnico")
    metricas_modelo: Optional[Dict[str, Any]] = Field(default=None, description="Métricas R2, MAE y RMSE del modelo")

class SP500HealthResponse(BaseModel):
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(4, description="Número de variables de entrada requeridas")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Métricas del modelo")
