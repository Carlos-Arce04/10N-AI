from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/predict", tags=["Modelos de Machine Learning"])

# --- Esquemas de Entrada Pydantic ---
class AutoRequest(BaseModel):
    present_price: float = Field(..., description="Precio nuevo en agencia (lakhs)", example=9.54)
    kms_driven: int = Field(..., description="Kilometraje acumulado", example=43000)
    anio: Optional[int] = Field(None, description="Año de fabricación del vehículo", example=2018)
    year: Optional[int] = Field(None, description="Año alternativo (en inglés)", example=2018)
    fuel_type: str = Field("Diesel", description="Tipo de combustible (Petrol, Diesel, CNG)")
    seller_type: str = Field("Dealer", description="Canal de venta (Dealer, Individual)")
    transmission: str = Field("Manual", description="Tipo de transmisión (Manual, Automatic)")
    owner: int = Field(0, description="Cantidad de dueños anteriores")

class VinoRequest(BaseModel):
    fixed_acidity: float = Field(7.2, example=7.2)
    volatile_acidity: float = Field(0.25, example=0.25)
    citric_acid: float = Field(0.38, example=0.38)
    residual_sugar: float = Field(2.0, example=2.0)
    chlorides: float = Field(0.04, example=0.04)
    free_sulfur_dioxide: float = Field(30.0, example=30.0)
    total_sulfur_dioxide: float = Field(110.0, example=110.0)
    density: float = Field(0.992, example=0.992)
    ph: float = Field(3.25, example=3.25)
    sulphates: float = Field(0.55, example=0.55)
    alcohol: float = Field(12.2, example=12.2)
    is_red: int = Field(0, description="0: Blanco, 1: Tinto", example=0)

class ChurnRequest(BaseModel):
    tenure: int = Field(3, description="Meses de permanencia", example=3)
    monthly_charges: float = Field(85.50, description="Monto mensual", example=85.50)
    total_charges: float = Field(256.50, description="Total facturado", example=256.50)
    contract: str = Field("Month-to-month", example="Month-to-month")
    internet_service: str = Field("Fiber optic", example="Fiber optic")
    tech_support: str = Field("No", example="No")
    online_security: str = Field("No", example="No")
    paperless_billing: str = Field("Yes", example="Yes")
    payment_method: str = Field("Electronic check", example="Electronic check")
    senior: int = Field(0, example=0)
    partner: str = Field("No", example="No")

class AguacateRequest(BaseModel):
    total_volume: float = Field(75000.0, example=75000.0)
    plu_4046: float = Field(15000.0, example=15000.0)
    plu_4225: float = Field(20000.0, example=20000.0)
    plu_4770: float = Field(1000.0, example=1000.0)
    total_bags: float = Field(14000.0, example=14000.0)
    small_bags: float = Field(10000.0, example=10000.0)
    large_bags: float = Field(3800.0, example=3800.0)
    xlarge_bags: float = Field(200.0, example=200.0)
    year: int = Field(2026, example=2026)
    month: int = Field(9, example=9)
    is_organic: int = Field(1, description="1: Orgánico, 0: Convencional", example=1)
    region: str = Field("California", example="California")

class StrokeRequest(BaseModel):
    age: float = Field(67.0, description="Edad del paciente", example=67.0)
    hypertension: int = Field(1, description="1: Sí, 0: No", example=1)
    heart_disease: int = Field(1, description="1: Sí, 0: No", example=1)
    avg_glucose_level: float = Field(210.0, description="Glucosa en sangre (mg/dL)", example=210.0)
    bmi: float = Field(32.0, description="Índice de masa corporal", example=32.0)
    gender: str = Field("Male", example="Male")
    ever_married: str = Field("Yes", example="Yes")
    work_type: str = Field("Private", example="Private")
    residence_type: str = Field("Urban", example="Urban")
    smoking_status: str = Field("smokes", example="smokes")

# --- Endpoints de Predicción ---

@router.post("/auto")
def predecir_auto(payload: AutoRequest):
    anio_resuelto = payload.anio if payload.anio is not None else (payload.year if payload.year is not None else 2018)
    return ml_service.predict_auto(
        present_price=payload.present_price,
        kms_driven=payload.kms_driven,
        anio=anio_resuelto,
        fuel_type=payload.fuel_type,
        seller_type=payload.seller_type,
        transmission=payload.transmission,
        owner=payload.owner
    )

@router.post("/vino")
def predecir_vino(payload: VinoRequest):
    return ml_service.predict_vino(
        fixed_acidity=payload.fixed_acidity,
        volatile_acidity=payload.volatile_acidity,
        citric_acid=payload.citric_acid,
        residual_sugar=payload.residual_sugar,
        chlorides=payload.chlorides,
        free_sulfur_dioxide=payload.free_sulfur_dioxide,
        total_sulfur_dioxide=payload.total_sulfur_dioxide,
        density=payload.density,
        ph=payload.ph,
        sulphates=payload.sulphates,
        alcohol=payload.alcohol,
        is_red=payload.is_red
    )

@router.post("/churn")
def predecir_churn(payload: ChurnRequest):
    return ml_service.predict_churn(
        tenure=payload.tenure,
        monthly_charges=payload.monthly_charges,
        total_charges=payload.total_charges,
        contract=payload.contract,
        internet_service=payload.internet_service,
        tech_support=payload.tech_support,
        online_security=payload.online_security,
        paperless_billing=payload.paperless_billing,
        payment_method=payload.payment_method,
        senior=payload.senior,
        partner=payload.partner
    )

@router.post("/aguacate")
def predecir_aguacate(payload: AguacateRequest):
    return ml_service.predict_aguacate(
        total_volume=payload.total_volume,
        plu_4046=payload.plu_4046,
        plu_4225=payload.plu_4225,
        plu_4770=payload.plu_4770,
        total_bags=payload.total_bags,
        small_bags=payload.small_bags,
        large_bags=payload.large_bags,
        xlarge_bags=payload.xlarge_bags,
        year=payload.year,
        month=payload.month,
        is_organic=payload.is_organic,
        region=payload.region
    )

@router.post("/stroke")
def predecir_stroke(payload: StrokeRequest):
    return ml_service.predict_stroke(
        age=payload.age,
        hypertension=payload.hypertension,
        heart_disease=payload.heart_disease,
        avg_glucose_level=payload.avg_glucose_level,
        bmi=payload.bmi,
        gender=payload.gender,
        ever_married=payload.ever_married,
        work_type=payload.work_type,
        residence_type=payload.residence_type,
        smoking_status=payload.smoking_status
    )
