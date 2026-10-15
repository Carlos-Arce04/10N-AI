from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class BitcoinPredictionRequest(BaseModel):
    """Request para proyección y predicción del precio de cierre de Bitcoin (BTC/USD)"""
    open: float = Field(2500.0, description="Precio de apertura en USD", example=2500.0)
    high: float = Field(2580.0, description="Precio máximo del periodo en USD", example=2580.0)
    low: float = Field(2470.0, description="Precio mínimo del periodo en USD", example=2470.0)
    volume: float = Field(1500000000.0, description="Volumen transaccionado en USD", example=1500000000.0)
    market_cap: float = Field(41000000000.0, description="Capitalización de mercado en USD", example=41000000000.0)

class BitcoinPredictionResponse(BaseModel):
    """Response con predicción del precio de Bitcoin"""
    success: bool = Field(True, description="Indica si la inferencia fue exitosa")
    precio_cierre_usd: float = Field(..., description="Precio de cierre proyectado en USD")
    variacion_proyectada_pct: float = Field(..., description="Variación porcentual esperada respecto a Open (%)")
    tendencia: str = Field(..., description="Tendencia proyectada (Alcista / Bajista / Neutral)")
    rango_dia_usd: float = Field(..., description="Amplitud intradiaria (High - Low) en USD")
    confidence: float = Field(..., description="Nivel de confianza estadística del modelo (%)")
    interpretacion: str = Field(..., description="Lectura financiera automatizada")
    metricas_modelo: Optional[Dict[str, Any]] = Field(default=None, description="Métricas R2, MAE y RMSE del modelo")

class BitcoinHealthResponse(BaseModel):
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(5, description="Número de variables de entrada requeridas")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Métricas del modelo")
