from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class WinePredictionRequest(BaseModel):
    """Request para evaluación enológica y clasificación de calidad de vino"""
    fixed_acidity: float = Field(7.2, description="Acidez fija (ácido tartárico g/dm3)", example=7.2)
    volatile_acidity: float = Field(0.25, description="Acidez volátil (ácido acético g/dm3)", example=0.25)
    citric_acid: float = Field(0.38, description="Ácido cítrico (g/dm3)", example=0.38)
    residual_sugar: float = Field(2.0, description="Azúcar residual (g/dm3)", example=2.0)
    chlorides: float = Field(0.04, description="Cloruros (sal g/dm3)", example=0.04)
    free_sulfur_dioxide: float = Field(30.0, description="Dióxido de azufre libre (mg/dm3)", example=30.0)
    total_sulfur_dioxide: float = Field(110.0, description="Dióxido de azufre total (mg/dm3)", example=110.0)
    density: float = Field(0.992, description="Densidad (g/cm3)", example=0.992)
    ph: float = Field(3.25, description="Nivel de pH", example=3.25)
    sulphates: float = Field(0.55, description="Sulfatos (sulfato de potasio g/dm3)", example=0.55)
    alcohol: float = Field(12.2, description="Graduación alcohólica (% vol)", example=12.2)
    is_red: int = Field(0, description="0: Blanco, 1: Tinto", example=0)

class WinePredictionResponse(BaseModel):
    """Response con diagnóstico enológico y nivel de calidad"""
    success: bool = Field(True, description="Inferencia completada con éxito")
    calidad_alta: bool = Field(..., description="Booleano: True si califica como vino de alta calidad")
    diagnostico: str = Field(..., description="Veredicto enológico principal")
    probabilidad_alta_calidad: float = Field(..., description="Probabilidad de pertenecer a categoría premium (0-100%)")
    confidence: float = Field(..., description="Confianza general del análisis (0-100%)")
    quality_tier: str = Field(..., description="Nivel: Regular, Selección Especial o Gran Reserva")
    sensory_balance: Dict[str, Any] = Field(..., description="Evaluación de acidez, alcohol y cuerpo")
    interpretation: str = Field(..., description="Interpretación en lenguaje natural")
    model_info: Dict[str, Any] = Field(..., description="Metadatos del modelo")

class WineHealthResponse(BaseModel):
    """Health check del modelo de vino"""
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está activo")
    features_count: int = Field(..., description="Número de características evaluadas")
    wine_types: List[str] = Field(["Vino Blanco", "Vino Tinto"], description="Variedades soportadas")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Métricas de precisión y recall")
