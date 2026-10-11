import logging
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any
from app.core.config import MODELS_DIR

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.load_all_models()

    def load_all_models(self):
        """Carga en memoria todos los modelos serializados disponibles en la carpeta models/"""
        archivos_modelos = {
            "autos": "modelo_01_autos.joblib",
            "vino": "modelo_02_vino.joblib",
            "churn": "modelo_03_churn.joblib",
            "aguacate": "modelo_04_aguacate.joblib",
            "stroke": "modelo_05_stroke.joblib"
        }

        for clave, archivo in archivos_modelos.items():
            ruta = MODELS_DIR / archivo
            if ruta.exists():
                try:
                    self.models[clave] = joblib.load(str(ruta))
                    logger.info(f"Modelo cargado exitosamente: {clave} ({archivo})")
                except Exception as e:
                    logger.error(f"Error cargando modelo {clave} desde {ruta}: {e}")
            else:
                logger.warning(f"Archivo de modelo no encontrado: {ruta}")

    # --- 01. Predicción de Autos ---
    def predict_auto(self, present_price: float, kms_driven: int, anio: int,
                     fuel_type: str = "Petrol", seller_type: str = "Dealer",
                     transmission: str = "Manual", owner: int = 0) -> Dict[str, Any]:
        pkg = self.models.get("autos")
        if not pkg:
            return {"success": False, "error": "Modelo de autos no está cargado."}

        features = pkg["features"]
        vehicle_age = 2026 - anio
        
        fila = {
            "Present_Price": present_price,
            "Kms_Driven": kms_driven,
            "Owner": owner,
            "Vehicle_Age": vehicle_age,
            "Fuel_Type_Diesel": 1 if fuel_type.lower() == "diesel" else 0,
            "Fuel_Type_Petrol": 1 if fuel_type.lower() == "petrol" else 0,
            "Seller_Type_Individual": 1 if seller_type.lower() == "individual" else 0,
            "Transmission_Manual": 1 if transmission.lower() == "manual" else 0
        }
        df_in = pd.DataFrame([fila])[features]
        precio_estimado = float(pkg["model"].predict(df_in)[0])

        return {
            "success": True,
            "modelo": "Random Forest Regressor (Clase 3)",
            "precio_estimado_lakhs": round(precio_estimado, 2),
            "precio_estimado_usd": round(precio_estimado * 1200, 2), # Estimado referencial
            "antiguedad_anios": vehicle_age,
            "metricas": pkg.get("metrics", {})
        }

    # --- 02. Calificación de Vino ---
    def predict_vino(self, fixed_acidity: float, volatile_acidity: float, citric_acid: float,
                     residual_sugar: float, chlorides: float, free_sulfur_dioxide: float,
                     total_sulfur_dioxide: float, density: float, ph: float,
                     sulphates: float, alcohol: float, is_red: int = 0) -> Dict[str, Any]:
        pkg = self.models.get("vino")
        if not pkg:
            return {"success": False, "error": "Modelo de vino no está cargado."}

        features = pkg["features"]
        fila = {
            "fixed acidity": fixed_acidity,
            "volatile acidity": volatile_acidity,
            "citric acid": citric_acid,
            "residual sugar": residual_sugar,
            "chlorides": chlorides,
            "free sulfur dioxide": free_sulfur_dioxide,
            "total sulfur dioxide": total_sulfur_dioxide,
            "density": density,
            "pH": ph,
            "sulphates": sulphates,
            "alcohol": alcohol,
            "type_red": is_red
        }
        df_in = pd.DataFrame([fila])[features]
        pred = int(pkg["model"].predict(df_in)[0])
        prob = float(pkg["model"].predict_proba(df_in)[0][1])

        return {
            "success": True,
            "modelo": "Random Forest Classifier (Clase 3)",
            "calidad_alta": bool(pred == 1),
            "diagnostico": "ALTA CALIDAD (Certificado Premium)" if pred == 1 else "CALIDAD ESTÁNDAR / REGULAR",
            "probabilidad_alta_calidad": round(prob * 100, 2),
            "metricas": pkg.get("metrics", {})
        }

    # --- 03. Abandono de Clientes (Churn) ---
    def predict_churn(self, tenure: int, monthly_charges: float, total_charges: float,
                      contract: str = "Month-to-month", internet_service: str = "Fiber optic",
                      tech_support: str = "No", online_security: str = "No",
                      paperless_billing: str = "Yes", payment_method: str = "Electronic check",
                      senior: int = 0, partner: str = "No") -> Dict[str, Any]:
        pkg = self.models.get("churn")
        if not pkg:
            return {"success": False, "error": "Modelo de churn no está cargado."}

        features = pkg["features"]
        fila = {col: 0 for col in features}
        fila["tenure"] = tenure
        fila["MonthlyCharges"] = monthly_charges
        fila["TotalCharges"] = total_charges
        fila["SeniorCitizen"] = senior

        if partner.lower() in ["yes", "si"]: fila["Partner_Yes"] = 1
        if paperless_billing.lower() in ["yes", "si"]: fila["PaperlessBilling_Yes"] = 1
        if "one" in contract.lower() or "1" in contract.lower(): fila["Contract_One year"] = 1
        if "two" in contract.lower() or "2" in contract.lower(): fila["Contract_Two year"] = 1
        if "fiber" in internet_service.lower(): fila["InternetService_Fiber optic"] = 1
        elif "no" in internet_service.lower(): fila["InternetService_No"] = 1
        if tech_support.lower() in ["yes", "si"]: fila["TechSupport_Yes"] = 1
        if online_security.lower() in ["yes", "si"]: fila["OnlineSecurity_Yes"] = 1
        if "electronic" in payment_method.lower(): fila["PaymentMethod_Electronic check"] = 1
        elif "credit" in payment_method.lower(): fila["PaymentMethod_Credit card (automatic)"] = 1
        elif "bank" in payment_method.lower(): fila["PaymentMethod_Bank transfer (automatic)"] = 1

        df_in = pd.DataFrame([fila])[features]
        pred = int(pkg["model"].predict(df_in)[0])
        prob = float(pkg["model"].predict_proba(df_in)[0][1])

        return {
            "success": True,
            "modelo": "Random Forest Balanced (Clase 5)",
            "en_riesgo_churn": bool(pred == 1),
            "diagnostico": "ALTO RIESGO DE FUGA (CHURN DETECTADO)" if pred == 1 else "CLIENTE ESTABLE / FIDELIZADO",
            "probabilidad_cancelacion": round(prob * 100, 2),
            "recomendacion": "Ofrecer bono de retención o migración a contrato anual inmediatamente." if pred == 1 else "Mantener comunicación estándar.",
            "metricas": pkg.get("metrics", {})
        }

    # --- 04. Precio del Aguacate ---
    def predict_aguacate(self, total_volume: float = 50000.0, plu_4046: float = 15000.0,
                          plu_4225: float = 20000.0, plu_4770: float = 1000.0,
                          total_bags: float = 14000.0, small_bags: float = 10000.0,
                          large_bags: float = 3800.0, xlarge_bags: float = 200.0,
                          year: int = 2026, month: int = 9, is_organic: int = 1,
                          region: str = "California") -> Dict[str, Any]:
        pkg = self.models.get("aguacate")
        if not pkg:
            return {"success": False, "error": "Modelo de aguacate no está cargado."}

        features = pkg["features"]
        fila = {col: 0.0 for col in features}
        fila["Total Volume"] = total_volume
        fila["4046"] = plu_4046
        fila["4225"] = plu_4225
        fila["4770"] = plu_4770
        fila["Total Bags"] = total_bags
        fila["Small Bags"] = small_bags
        fila["Large Bags"] = large_bags
        fila["XLarge Bags"] = xlarge_bags
        fila["year"] = year
        fila["Month"] = month
        fila["is_organic"] = is_organic

        col_reg = f"region_{region}"
        if col_reg in fila:
            fila[col_reg] = 1.0

        df_in = pd.DataFrame([fila])[features]
        if pkg.get("scaler"):
            df_proc = pkg["scaler"].transform(df_in)
            precio = float(pkg["model"].predict(df_proc)[0])
        else:
            precio = float(pkg["model"].predict(df_in)[0])

        return {
            "success": True,
            "modelo": pkg.get("nombre", "Random Forest Regressor (Clase 3)"),
            "precio_unitario_usd": round(precio, 2),
            "precio_estimado_usd": round(precio, 2),
            "tipo_cultivo": "Orgánico" if is_organic == 1 else "Convencional",
            "region": region,
            "metricas": pkg.get("metrics", {})
        }

    # --- 05. Diagnóstico de Stroke (ACV) ---
    def predict_stroke(self, age: float, hypertension: int, heart_disease: int,
                       avg_glucose_level: float, bmi: float, gender: str = "Male",
                       ever_married: str = "Yes", work_type: str = "Private",
                       residence_type: str = "Urban", smoking_status: str = "smokes") -> Dict[str, Any]:
        pkg = self.models.get("stroke")
        if not pkg:
            return {"success": False, "error": "Modelo de stroke no está cargado."}

        features = pkg["features"]
        fila = {col: 0 for col in features}
        fila["age"] = age
        fila["hypertension"] = hypertension
        fila["heart_disease"] = heart_disease
        fila["avg_glucose_level"] = avg_glucose_level
        fila["bmi"] = bmi

        if gender.lower() == "male": fila["gender_Male"] = 1
        if ever_married.lower() in ["yes", "si"]: fila["ever_married_Yes"] = 1
        col_w = f"work_type_{work_type}"
        if col_w in fila: fila[col_w] = 1
        if residence_type.lower() == "urban": fila["Residence_type_Urban"] = 1
        col_s = f"smoking_status_{smoking_status}"
        if col_s in fila: fila[col_s] = 1

        df_in = pd.DataFrame([fila])[features]
        scaler = pkg["scaler"]
        df_scaled = scaler.transform(df_in)

        pred = int(pkg["model"].predict(df_scaled)[0])
        prob = float(pkg["model"].predict_proba(df_scaled)[0][1])

        return {
            "success": True,
            "modelo": "Support Vector Machine (Kernel RBF - Clase 4)",
            "alerta_stroke": bool(pred == 1),
            "diagnostico": "ALTO RIESGO DE ACV / STROKE (Alerta Clínica)" if pred == 1 else "RIESGO BAJO / CONTROLADO",
            "probabilidad_evento_vascular": round(prob * 100, 2),
            "recomendacion": "Requiere evaluación neurológica y tomografía preventiva urgente." if pred == 1 else "Continuar chequeos médicos periódicos de rutina.",
            "metricas": pkg.get("metrics", {})
        }

ml_service = MLService()
