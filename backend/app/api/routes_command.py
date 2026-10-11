import re
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/command", tags=["Comandos de Voz del Asistente"])

class CommandRequest(BaseModel):
    transcript: str = Field(..., description="Texto reconocido por voz", example="10N-AI cotizar precio de aguacate")
    personality: str = Field("d10s", description="Personalidad del asistente: 'd10s' (Messi) o 'cr7' (Cristiano)", example="d10s")

@router.post("/process")
def process_voice_command(payload: CommandRequest):
    """
    Interpreta el comando de voz del usuario (ejecutado desde Chrome Web Speech API),
    clasifica la intención hacia el modelo correspondiente y genera una respuesta
    con la personalidad seleccionada (Core D10S / Core CR7).
    """
    texto = payload.transcript.lower().strip()
    modo = payload.personality.lower()

    # Prefijos de personalidad para las respuestas conversacionales
    es_d10s = (modo == "d10s")
    prefijo = "Che, mirá:" if es_d10s else "¡Siuuu, Comandante!"
    sufijo = "Todo listo, hermano." if es_d10s else "¡Objetivo cumplido con máxima precisión!"

    # --- 1. Detección de Comando: Autos ---
    if any(k in texto for k in ["auto", "carro", "vehículo", "vehiculo", "coche", "vender"]):
        res = ml_service.predict_auto(present_price=9.54, kms_driven=43000, anio=2018)
        precio = res["precio_estimado_lakhs"]
        mensaje = f"{prefijo} Para un auto 2018 con 43,000 km, el Random Forest calcula un valor de mercado de ${precio} lakhs. {sufijo}"
        return {
            "success": True,
            "intencion": "prediccion_auto",
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": res
        }

    # --- 2. Detección de Comando: Vino ---
    elif any(k in texto for k in ["vino", "calidad", "enológico", "copa", "bodega"]):
        res = ml_service.predict_vino(
            fixed_acidity=7.2, volatile_acidity=0.25, citric_acid=0.38,
            residual_sugar=2.0, chlorides=0.04, free_sulfur_dioxide=30.0,
            total_sulfur_dioxide=110.0, density=0.992, ph=3.25, sulphates=0.55,
            alcohol=12.2, is_red=0
        )
        diag = res["diagnostico"]
        prob = res["probabilidad_alta_calidad"]
        mensaje = f"{prefijo} Analicé los parámetros del vino: {diag} con una probabilidad del {prob}%. {sufijo}"
        return {
            "success": True,
            "intencion": "clasificacion_vino",
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": res
        }

    # --- 3. Detección de Comando: Churn / Fuga de Clientes ---
    elif any(k in texto for k in ["churn", "fuga", "cancelar", "cancelación", "cliente", "abandono"]):
        res = ml_service.predict_churn(tenure=3, monthly_charges=85.5, total_charges=256.5)
        prob = res["probabilidad_cancelacion"]
        mensaje = f"{prefijo} Detecté {res['diagnostico']} ({prob}% de probabilidad de fuga). Te recomiendo {res['recomendacion'].lower()} {sufijo}"
        return {
            "success": True,
            "intencion": "prediccion_churn",
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": res
        }

    # --- 4. Detección de Comando: Aguacate ---
    elif any(k in texto for k in ["aguacate", "palta", "avocado", "cosecha", "cultivo"]):
        res = ml_service.predict_aguacate(total_volume=75000, month=9, is_organic=1, region="California")
        precio = res["precio_unitario_usd"]
        mensaje = f"{prefijo} Para aguacate orgánico en California en el mes de septiembre, el precio proyectado es de ${precio} USD por unidad. {sufijo}"
        return {
            "success": True,
            "intencion": "prediccion_aguacate",
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": res
        }

    # --- 5. Detección de Comando: Stroke / ACV / Salud ---
    elif any(k in texto for k in ["stroke", "acv", "infarto", "cerebro", "médico", "salud", "clínico"]):
        res = ml_service.predict_stroke(age=67.0, hypertension=1, heart_disease=1, avg_glucose_level=210.0, bmi=32.0)
        prob = res["probabilidad_evento_vascular"]
        mensaje = f"{prefijo} Triaje de Support Vector Machine completado: {res['diagnostico']} ({prob}% de riesgo). {res['recomendacion']} {sufijo}"
        return {
            "success": True,
            "intencion": "triaje_stroke",
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": res
        }

    # --- 6. Comando General / Saludo ---
    else:
        saludo = "Hola che, soy el Core D10S de 10N-AI. Podés pedirme cotizaciones de autos, aguacates, calidad de vino, análisis de churn o triaje de stroke." if es_d10s else "¡Siuuu! Soy el Core CR7 de 10N-AI. Sistema listo para procesar tus comandos tácticos de Machine Learning."
        return {
            "success": True,
            "intencion": "saludo_general",
            "comando_original": payload.transcript,
            "respuesta_texto": saludo,
            "datos": None
        }
