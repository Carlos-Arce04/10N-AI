from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class HepatitisPredictionRequest(BaseModel):
    """Request para clasificación diagnóstica de Hepatitis C / Patología Hepática"""
    age: float = Field(32.0, description="Edad del paciente en años", example=32.0)
    sex: str = Field("m", description="Sexo biológico: 'm' (masculino) o 'f' (femenino)", example="m")
    alb: float = Field(38.5, description="Albúmina sérica (ALB) en g/L", example=38.5)
    alp: float = Field(52.5, description="Fosfatasa alcalina (ALP) en U/L", example=52.5)
    alt: float = Field(7.7, description="Alanina aminotransferasa (ALT) en U/L", example=7.7)
    ast: float = Field(22.1, description="Aspartato aminotransferasa (AST) en U/L", example=22.1)
    bil: float = Field(7.5, description="Bilirrubina total (BIL) en µmol/L", example=7.5)
    che: float = Field(6.93, description="Colinesterasa (CHE) en kU/L", example=6.93)
    chol: float = Field(3.23, description="Colesterol sérico (CHOL) en mmol/L", example=3.23)
    crea: float = Field(106.0, description="Creatinina sérica (CREA) en µmol/L", example=106.0)
    ggt: float = Field(12.1, description="Gamma-glutamiltransferasa (GGT) en U/L", example=12.1)
    prot: float = Field(69.0, description="Proteínas totales (PROT) en g/L", example=69.0)

class HepatitisPredictionResponse(BaseModel):
    """Response del diagnóstico de Hepatitis C"""
    success: bool = Field(True, description="Indica si el diagnóstico se completó")
    patologia_detectada: bool = Field(..., description="True si existe sospecha de patología hepática")
    diagnostico: str = Field(..., description="Diagnóstico en lenguaje natural (Normal vs Patología)")
    probabilidad_patologia: float = Field(..., description="Probabilidad estimada de patología hepática (%)")
    confidence: float = Field(..., description="Certeza de la clasificación (%)")
    recomendacion: str = Field(..., description="Guía clínica recomendada para seguimiento")
    metricas_modelo: Optional[Dict[str, Any]] = Field(default=None, description="Métricas Accuracy, F1, ROC-AUC del modelo")

class HepatitisHealthResponse(BaseModel):
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(12, description="Número de biomarcadores requeridos")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Métricas del modelo")
