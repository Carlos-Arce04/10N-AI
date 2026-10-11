from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class ChurnPredictionRequest(BaseModel):
    """Request para predicción de riesgo de fuga de clientes (Churn)"""
    tenure: int = Field(3, description="Meses de permanencia con el servicio", ge=0, example=3)
    monthly_charges: float = Field(85.50, description="Monto cobrado mensualmente en USD", ge=0, example=85.50)
    total_charges: float = Field(256.50, description="Gasto acumulado total en USD", ge=0, example=256.50)
    contract: str = Field("Month-to-month", description="Tipo de contrato (Month-to-month, One year, Two year)", example="Month-to-month")
    internet_service: str = Field("Fiber optic", description="Tipo de servicio de internet (Fiber optic, DSL, No)", example="Fiber optic")
    tech_support: str = Field("No", description="Soporte técnico contratado (Yes, No, No internet service)", example="No")
    online_security: str = Field("No", description="Seguridad en línea (Yes, No, No internet service)", example="No")
    paperless_billing: str = Field("Yes", description="Facturación digital (Yes, No)", example="Yes")
    payment_method: str = Field("Electronic check", description="Método de pago", example="Electronic check")
    senior: int = Field(0, description="1: Adulto mayor, 0: No", example=0)
    partner: str = Field("No", description="Tiene pareja/cónyuge (Yes, No)", example="No")

class ChurnPredictionResponse(BaseModel):
    """Response con diagnóstico de retención y plan de fidelización"""
    success: bool = Field(True, description="Inferencia completada")
    en_riesgo_churn: bool = Field(..., description="Booleano: True si el cliente probablemente cancelará")
    diagnostico: str = Field(..., description="Veredicto de retención principal")
    probabilidad_cancelacion: float = Field(..., description="Probabilidad estimada de deserción (0-100%)")
    recomendacion: str = Field(..., description="Acción estratégica recomendada")
    confidence: float = Field(..., description="Confianza estadística del modelo")
    risk_level: str = Field(..., description="Nivel de riesgo: Seguro, Moderado o Crítico")
    retention_tactics: List[str] = Field(..., description="Lista de tácticas sugeridas para el equipo de ventas/éxito")
    interpretation: str = Field(..., description="Interpretación detallada en lenguaje natural")
    model_info: Dict[str, Any] = Field(..., description="Metadatos del modelo")

class ChurnHealthResponse(BaseModel):
    """Health check del modelo de retención de clientes"""
    status: str = Field("healthy", description="Estado del servicio")
    model_loaded: bool = Field(..., description="Indica si el modelo está en memoria")
    features_count: int = Field(..., description="Número de variables analizadas")
    contracts_supported: List[str] = Field(["Month-to-month", "One year", "Two year"], description="Contratos soportados")
    model_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Accuracy, Recall y ROC-AUC")

class ChurnOptionsResponse(BaseModel):
    contracts: List[str]
    internet_services: List[str]
    payment_methods: List[str]
