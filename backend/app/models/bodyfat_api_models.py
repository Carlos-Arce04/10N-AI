from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class BodyFatPredictionRequest(BaseModel):
    """Request para estimación de porcentaje de grasa corporal según medidas antropométricas"""
    age: float = Field(29.0, description="Edad del individuo en años", example=29.0)
    weight: float = Field(154.25, description="Peso corporal en libras (lbs)", example=154.25)
    height: float = Field(67.75, description="Estatura en pulgadas (in)", example=67.75)
    neck: float = Field(36.2, description="Circunferencia de cuello en cm", example=36.2)
    chest: float = Field(93.1, description="Circunferencia de pecho en cm", example=93.1)
    abdomen: float = Field(85.2, description="Circunferencia de abdomen en cm", example=85.2)
    hip: float = Field(94.5, description="Circunferencia de cadera en cm", example=94.5)
    thigh: float = Field(59.0, description="Circunferencia de muslo en cm", example=59.0)
    knee: float = Field(37.3, description="Circunferencia de rodilla en cm", example=37.3)
    ankle: float = Field(21.9, description="Circunferencia de tobillo en cm", example=21.9)
    biceps: float = Field(32.0, description="Circunferencia de bíceps en cm", example=32.0)
    forearm: float = Field(27.4, description="Circunferencia de antebrazo en cm", example=27.4)
    wrist: float = Field(17.1, description="Circunferencia de muñeca en cm", example=17.1)

class BodyFatPredictionResponse(BaseModel):
    """Response con porcentaje de grasa corporal y categoría antropométrica"""
    success: bool = Field(True, description="Indica si la inferencia fue exitosa")
    grasa_corporal_pct: float = Field(..., description="Porcentaje de grasa corporal estimado (%)")
    categoria: str = Field(..., description="Categoría de composición corporal (Atleta, Fitness, Aceptable, Elevado)")
    rango_saludable: str = Field(..., description="Rango de referencia según estándares médicos")
    confidence: float = Field(..., description="Nivel de confianza estadística del cálculo (%)")
    interpretacion: str = Field(..., description="Explicación clínica en lenguaje natural")
    metricas_modelo: Optional[Dict[str, Any]] = Field(default=None, description="Métricas R2, MAE y RMSE del modelo")

class BodyFatHealthResponse(BaseModel):
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(13, description="Número de variables de entrada requeridas")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Métricas de evaluación del modelo")
