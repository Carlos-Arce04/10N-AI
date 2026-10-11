from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class StrokePredictionRequest(BaseModel):
    """Request para triaje y evaluación de riesgo de accidente cerebrovascular (ACV / Stroke)"""
    age: float = Field(65.0, description="Edad del paciente en años", ge=0, le=120, example=65.0)
    hypertension: int = Field(1, description="Hipertensión arterial (1: Sí, 0: No)", example=1)
    heart_disease: int = Field(0, description="Antecedente de cardiopatía (1: Sí, 0: No)", example=0)
    avg_glucose_level: float = Field(180.0, description="Nivel promedio de glucosa en sangre (mg/dL)", ge=40, example=180.0)
    bmi: float = Field(29.5, description="Índice de masa corporal (BMI)", ge=10, le=70, example=29.5)
    gender: str = Field("Male", description="Género (Male, Female)", example="Male")
    ever_married: str = Field("Yes", description="Estado civil (Yes, No)", example="Yes")
    work_type: str = Field("Private", description="Tipo de trabajo (Private, Self-employed, Govt_job, children, Never_worked)", example="Private")
    residence_type: str = Field("Urban", description="Tipo de residencia (Urban, Rural)", example="Urban")
    smoking_status: str = Field("smokes", description="Hábito de fumar (formerly smoked, never smoked, smokes, Unknown)", example="smokes")

class StrokePredictionResponse(BaseModel):
    """Response con estratificación de riesgo cardiovascular/cerebral"""
    success: bool = Field(True, description="Evaluación completada")
    alerta_stroke: bool = Field(..., description="Booleano: True si existe riesgo significativo de ACV")
    diagnostico: str = Field(..., description="Veredicto médico/preventivo")
    probabilidad_evento_vascular: float = Field(..., description="Probabilidad de sufrir un evento cerebrovascular (0-100%)")
    recomendacion: str = Field(..., description="Protocolo clínico o preventivo sugerido")
    confidence: float = Field(..., description="Confianza diagnóstica del modelo")
    clinical_risk: str = Field(..., description="Nivel de riesgo clínico: Bajo, Moderado o Elevado")
    risk_factors_detected: List[str] = Field(..., description="Factores de riesgo identificados en el paciente")
    interpretation: str = Field(..., description="Explicación en lenguaje claro para el paciente o médico")
    model_info: Dict[str, Any] = Field(..., description="Metadatos del modelo")

class StrokeHealthResponse(BaseModel):
    """Health check del modelo de riesgo de ACV"""
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(..., description="Número de variables clínicas")
    supported_genders: List[str] = Field(["Male", "Female"], description="Géneros contemplados")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Recall y ROC-AUC del modelo")

class StrokeOptionsResponse(BaseModel):
    work_types: List[str]
    smoking_statuses: List[str]
    residence_types: List[str]
