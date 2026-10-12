from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class CirrhosisPredictionRequest(BaseModel):
    """Request para clasificación del estadio histológico de cirrosis hepática (Estadios 1 al 4)"""
    n_days: float = Field(1000.0, description="Días de seguimiento clínico acumulados", example=1200.0)
    age_years: float = Field(50.0, description="Edad del paciente en años", example=52.0)
    sex: str = Field("F", description="Sexo biológico: 'F' (femenino) o 'M' (masculino)", example="F")
    bilirubin: float = Field(1.5, description="Bilirrubina sérica en mg/dl", example=1.5)
    cholesterol: float = Field(260.0, description="Colesterol sérico en mg/dl", example=260.0)
    albumin: float = Field(3.4, description="Albúmina sérica en g/dl", example=3.4)
    copper: float = Field(70.0, description="Cobre en orina en µg/día", example=70.0)
    alk_phos: float = Field(1200.0, description="Fosfatasa alcalina en U/litro", example=1200.0)
    sgot: float = Field(110.0, description="Transaminasa SGOT en U/ml", example=110.0)
    tryglicerides: float = Field(115.0, description="Triglicéridos en mg/dl", example=115.0)
    platelets: float = Field(250.0, description="Recuento de plaquetas por ml/1000", example=250.0)
    prothrombin: float = Field(10.6, description="Tiempo de protrombina en segundos", example=10.6)
    drug: str = Field("D-penicillamine", description="Fármaco: 'D-penicillamine' o 'Placebo'", example="D-penicillamine")
    ascites: str = Field("N", description="Presencia de ascitis: 'N' o 'Y'", example="N")
    hepatomegaly: str = Field("N", description="Presencia de hepatomegalia: 'N' o 'Y'", example="N")
    spiders: str = Field("N", description="Arañas vasculares: 'N' o 'Y'", example="N")
    edema: str = Field("N", description="Edema: 'N' (sin edema), 'S' (sin diuréticos), 'Y' (a pesar de diuréticos)", example="N")
    status: str = Field("C", description="Estado clínico: 'C' (censurado/vivo), 'CL' (trasplante), 'D' (fallecido)", example="C")

class CirrhosisPredictionResponse(BaseModel):
    """Response con estadio de cirrosis y probabilidades por nivel"""
    success: bool = Field(True, description="Indica si la inferencia fue exitosa")
    estadio_predicho: int = Field(..., description="Estadio histológico clasificado (1 a 4)")
    nombre_estadio: str = Field(..., description="Descripción clínica del estadio")
    severidad: str = Field(..., description="Nivel de severidad clínica (Leve, Moderado, Severo, Terminal)")
    probabilidades_estadios: Dict[str, float] = Field(..., description="Probabilidad asignada a cada estadio histológico (%)")
    confidence: float = Field(..., description="Certeza de la clasificación máxima (%)")
    interpretacion: str = Field(..., description="Interpretación clínica y pronóstico")
    metricas_modelo: Optional[Dict[str, Any]] = Field(default=None, description="Métricas Accuracy y F1 ponderado")

class CirrhosisHealthResponse(BaseModel):
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(20, description="Número de variables de entrada requeridas")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Métricas del modelo")
