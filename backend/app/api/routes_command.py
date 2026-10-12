import re
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/command", tags=["Comandos de Voz del Asistente"])

def normalize_spoken_spanish(text: str) -> str:
    """Normaliza variaciones fonéticas comunes de voz y convierte números hablados en dígitos."""
    t = text.lower().strip()
    
    # 1. Normalización de términos clave de ML mal transcriptos fonéticamente
    t = re.sub(r'\b(bit\s*coin|bicoin|bitcoins|bitcon)\b', 'bitcoin', t)
    t = re.sub(r'\b(ese\s*y\s*pe|s\s*y\s*p|s\s*&\s*p|sp\s*500|s\s*y\s*p\s*500|ese\s*y\s*pe\s*quinientos)\b', 'sp500', t)
    t = re.sub(r'\b(a\.?\s*c\.?\s*v\.?|derrame\s*cerebral|infarto\s*cerebral|accidente\s*cerebrovascular)\b', 'stroke', t)
    t = re.sub(r'\b(grasa\s*corpolar|porcentaje\s*grasa|grasa\s*corporal|composicion\s*corporal)\b', 'grasa', t)
    t = re.sub(r'\b(hepatitis\s*c|hepatitis|patologia\s*hepatica)\b', 'hepatitis', t)
    t = re.sub(r'\b(cirrosis\s*hepatica|cirrosis|estadio\s*de\s*cirrosis)\b', 'cirrosis', t)
    t = re.sub(r'\b(abandono|cancelacion|retencion|fuga\s*de\s*clientes?)\b', 'churn', t)
    t = re.sub(r'\b(palta|aguacates?|avocado)\b', 'aguacate', t)
    t = re.sub(r'\b(autos?|carros?|vehiculos?|vehículos?|coches?)\b', 'auto', t)
    t = re.sub(r'\b(vinos?|enologia|enológico|enologico)\b', 'vino', t)
    
    # 2. Conversión de números hablados comunes en español a dígitos numéricos
    words_to_num = {
        'dos mil veintiséis': '2026', 'dos mil veinticinco': '2025', 'dos mil veinticuatro': '2024',
        'dos mil veintitrés': '2023', 'dos mil veintidós': '2022', 'dos mil veintiuno': '2021',
        'dos mil veinte': '2020', 'dos mil diecinueve': '2019', 'dos mil dieciocho': '2018',
        'dos mil diecisiete': '2017', 'dos mil dieciséis': '2016', 'dos mil quince': '2015',
        'dos mil': '2000', 'mil': '1000',
        'veintinueve': '29', 'veintiocho': '28', 'veintisiete': '27', 'veintiséis': '26',
        'veinticinco': '25', 'veinticuatro': '24', 'veintitrés': '23', 'veintidós': '22',
        'veintiuno': '21', 'veinte': '20',
        'diecinueve': '19', 'dieciocho': '18', 'diecisiete': '17', 'dieciséis': '16',
        'quince': '15', 'catorce': '14', 'trece': '13', 'doce': '12', 'once': '11', 'diez': '10',
        'nueve': '9', 'ocho': '8', 'siete': '7', 'seis': '6', 'cinco': '5', 'cuatro': '4',
        'tres': '3', 'dos': '2', 'uno': '1', 'cero': '0',
        'noventa': '90', 'ochenta': '80', 'setenta': '70', 'sesenta': '60',
        'cincuenta': '50', 'cuarenta': '40', 'treinta': '30',
        'doscientos': '200', 'ciento': '100', 'cien': '100', 'quinientos': '500'
    }
    for word, num in words_to_num.items():
        t = re.sub(rf'\b{word}\b', num, t)
        
    return t

class CommandRequest(BaseModel):
    transcript: str = Field(..., description="Texto reconocido por voz o chat", example="10N-AI cotizar precio de aguacate")
    personality: str = Field("d10s", description="Personalidad del asistente: 'd10s' (Messi) o 'cr7' (Cristiano)", example="d10s")
    history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Historial de mensajes previos para memoria contextual estilo Gemini")

@router.post("/process")
def process_voice_command(payload: CommandRequest):
    """
    Interpreta el comando de voz o texto del usuario con normalización fonética y memoria de contexto.
    """
    raw_texto = payload.transcript.strip()
    texto = normalize_spoken_spanish(raw_texto)
    modo = payload.personality.lower()
    es_d10s = (modo == "d10s")


    prefijo = "Che, mirá:" if es_d10s else "¡Siuuu, Comandante!"
    sufijo = "Todo listo, hermano." if es_d10s else "¡Objetivo cumplido con máxima precisión!"

    # =========================================================================
    # 1. VINO (Calidad enológica)
    # =========================================================================
    if any(k in texto for k in ["vino", "enológico", "enologico", "copa", "bodega"]) or \
       ("calidad" in texto and not any(k in texto for k in ["auto", "carro", "aguacate", "cliente"])):

        alcohol_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|grados|alcohol)', texto) or re.search(r'alcohol\s*(?:de|:|=|del)?\s*(\d+(?:\.\d+)?)', texto)
        acidez_match = re.search(r'acidez\s*(?:de|:|=|del)?\s*(\d+(?:\.\d+)?)', texto)
        azucar_match = re.search(r'az[uú]car\s*(?:de|:|=|del)?\s*(\d+(?:\.\d+)?)', texto)
        ph_match = re.search(r'ph\s*(?:de|:|=|del)?\s*(\d+(?:\.\d+)?)', texto)
        es_tinto = 1 if ("tinto" in texto or "red" in texto) else 0

        user_provided_params = bool(alcohol_match or acidez_match or azucar_match or ph_match)

        params = {
            "fixed_acidity": 7.2,
            "volatile_acidity": float(acidez_match.group(1)) if acidez_match else 0.27,
            "citric_acid": 0.36,
            "residual_sugar": float(azucar_match.group(1)) if azucar_match else 6.0,
            "chlorides": 0.045,
            "free_sulfur_dioxide": 35.0,
            "total_sulfur_dioxide": 120.0,
            "density": 0.994,
            "ph": float(ph_match.group(1)) if ph_match else 3.20,
            "sulphates": 0.45,
            "alcohol": float(alcohol_match.group(1)) if alcohol_match else 11.5,
            "is_red": es_tinto
        }

        if user_provided_params:
            res = ml_service.predict_vino(**params)
            prob = res["probabilidad_alta_calidad"]
            diag = res["diagnostico"]
            tipo_txt = "tinto" if es_tinto else "blanco"
            mensaje = f"{prefijo} Evalué tu vino {tipo_txt} con esos datos: el resultado es **{diag}** ({prob}% de probabilidad). Podés seguir probando con otros valores en el panel. {sufijo}"
            return {
                "success": True,
                "intencion": "clasificacion_vino",
                "interactive_model": "vino",
                "params": params,
                "has_prediction": True,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": res
            }
        else:
            if es_d10s:
                mensaje = "¡De una, hermano! Para clasificar la calidad de tu vino, necesitamos configurar parámetros como el alcohol, acidez, azúcar y si es tinto o blanco. Te abrí el panel abajo para que elijas los valores o me los digas por chat:"
            else:
                mensaje = "¡Afirmativo, Comandante! Listo para evaluar la calidad del vino. Ajusta los parámetros en el panel interactivo a continuación y calculamos el resultado:"

            return {
                "success": True,
                "intencion": "clasificacion_vino",
                "interactive_model": "vino",
                "params": params,
                "has_prediction": False,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": None
            }

    # =========================================================================
    # 2. AUTOS (Tasación de vehículos)
    # =========================================================================
    elif any(k in texto for k in ["auto", "carro", "vehículo", "vehiculo", "coche", "vender"]):
        anio_match = re.search(r'(?:a[ñn]o|modelo)\s*(\d{4})', texto) or re.search(r'\b(20\d{2})\b', texto)
        kms_match = re.search(r'(\d+(?:[,\.]\d+)?)\s*(?:km|kms|kilometros|kilómetros)', texto)
        precio_match = re.search(r'(?:precio|agencia|valor)\s*(?:de)?\s*(\d+(?:\.\d+)?)', texto)
        diesel = 1 if "diesel" in texto else 0

        anio_val = int(anio_match.group(1)) if anio_match else 2018
        kms_val = int(kms_match.group(1).replace(",", "").replace(".", "")) if kms_match else 43000
        precio_val = float(precio_match.group(1)) if precio_match else 9.54
        combustible = "Diesel" if diesel else "Petrol"

        user_provided_params = bool(anio_match or kms_match or precio_match)

        params = {
            "present_price": precio_val,
            "kms_driven": kms_val,
            "anio": anio_val,
            "fuel_type": combustible,
            "seller_type": "Dealer",
            "transmission": "Manual",
            "owner": 0
        }

        if user_provided_params:
            res = ml_service.predict_auto(**params)
            precio_usd = res["precio_estimado_usd"]
            lakhs = res["precio_estimado_lakhs"]
            mensaje = f"{prefijo} Para un auto año {anio_val} con {kms_val:,} km, el valor estimado de mercado es de **${precio_usd:,.2f} USD** ({lakhs} lakhs). {sufijo}"
            return {
                "success": True,
                "intencion": "prediccion_auto",
                "interactive_model": "auto",
                "params": params,
                "has_prediction": True,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": res
            }
        else:
            if es_d10s:
                mensaje = "¡Claro che! Para cotizar el valor de tu auto, configurá el año, kilometraje acumulado, precio de agencia y combustible en el panel de abajo:"
            else:
                mensaje = "¡Entendido! Listo para cotizar el vehículo. Configura el año, kilometraje y características en el panel interactivo para obtener la tasación:"

            return {
                "success": True,
                "intencion": "prediccion_auto",
                "interactive_model": "auto",
                "params": params,
                "has_prediction": False,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": None
            }

    # =========================================================================
    # 3. CHURN / FUGA DE CLIENTES
    # =========================================================================
    elif any(k in texto for k in ["churn", "fuga", "cancelar", "cancelación", "cancelacion", "cliente", "abandono", "deserción", "desercion"]):
        tenure_match = re.search(r'(\d+)\s*(?:mes|meses|antigüedad|permanencia)', texto)
        mensual_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:dolares|dólares|\$|usd|mensual)', texto)

        tenure_val = int(tenure_match.group(1)) if tenure_match else 3
        mensual_val = float(mensual_match.group(1)) if mensual_match else 85.50
        total_val = round(tenure_val * mensual_val, 2)

        user_provided_params = bool(tenure_match or mensual_match)

        params = {
            "tenure": tenure_val,
            "monthly_charges": mensual_val,
            "total_charges": total_val,
            "contract": "Month-to-month",
            "internet_service": "Fiber optic",
            "tech_support": "No",
            "online_security": "No",
            "paperless_billing": "Yes",
            "payment_method": "Electronic check",
            "senior": 0,
            "partner": "No"
        }

        if user_provided_params:
            res = ml_service.predict_churn(**params)
            prob = res["probabilidad_cancelacion"]
            diag = res["diagnostico"]
            mensaje = f"{prefijo} Análisis completado: **{diag}** con {prob}% de probabilidad de cancelación. {res['recomendacion']} {sufijo}"
            return {
                "success": True,
                "intencion": "prediccion_churn",
                "interactive_model": "churn",
                "params": params,
                "has_prediction": True,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": res
            }
        else:
            if es_d10s:
                mensaje = "¡Dale! Para estimar si un cliente podría cancelar el servicio, ajustá los meses de permanencia, cobro mensual y tipo de contrato en el panel:"
            else:
                mensaje = "¡Análisis de clientes iniciado! Configura la permanencia, cobro mensual y tipo de contrato en el panel para evaluar el riesgo de cancelación:"

            return {
                "success": True,
                "intencion": "prediccion_churn",
                "interactive_model": "churn",
                "params": params,
                "has_prediction": False,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": None
            }

    # =========================================================================
    # 4. AGUACATE (Precio agrícola)
    # =========================================================================
    elif any(k in texto for k in ["aguacate", "palta", "avocado", "cosecha", "cultivo"]):
        organico = 1 if ("orgánico" in texto or "organico" in texto or "organic" in texto) else 0
        if "convencional" in texto:
            organico = 0

        region = "California"
        for r in ["Chicago", "GreatLakes", "LosAngeles", "NewYork", "TotalUS", "West", "MiamiFtLauderdale"]:
            if r.lower() in texto:
                region = r
                break

        params = {
            "total_volume": 75000.0,
            "plu_4046": 15000.0,
            "plu_4225": 20000.0,
            "plu_4770": 1000.0,
            "total_bags": 14000.0,
            "small_bags": 10000.0,
            "large_bags": 3800.0,
            "xlarge_bags": 200.0,
            "year": 2026,
            "month": 9,
            "is_organic": organico,
            "region": region
        }

        user_provided = any(k in texto for k in ["california", "chicago", "organico", "orgánico", "convencional", "septiembre", "mes"])

        if user_provided:
            res = ml_service.predict_aguacate(**params)
            precio = res["precio_unitario_usd"]
            tipo_str = "orgánico" if organico else "convencional"
            mensaje = f"{prefijo} Para aguacate {tipo_str} en la región {region}, el precio proyectado es de **${precio:.2f} USD** por unidad. {sufijo}"
            return {
                "success": True,
                "intencion": "prediccion_aguacate",
                "interactive_model": "aguacate",
                "params": params,
                "has_prediction": True,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": res
            }
        else:
            if es_d10s:
                mensaje = "¡Listo hermano! Para proyectar el precio del aguacate, seleccioná la región, tipo de cultivo, mes y volumen en el panel:"
            else:
                mensaje = "¡Proyección lista! Selecciona la región, tipo de cultivo, mes y volumen en el panel interactivo para calcular la cotización:"

            return {
                "success": True,
                "intencion": "prediccion_aguacate",
                "interactive_model": "aguacate",
                "params": params,
                "has_prediction": False,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": None
            }

    # =========================================================================
    # 5. STROKE / RIESGO DE ACV
    # =========================================================================
    elif any(k in texto for k in ["stroke", "acv", "infarto", "cerebro", "médico", "medico", "salud", "clínico", "clinico"]):
        edad_match = re.search(r'(\d+)\s*(?:a[ñn]os|edad)', texto)
        glucosa_match = re.search(r'glucosa\s*(?:de)?\s*(\d+(?:\.\d+)?)', texto)
        hipertension = 1 if "hipertensi" in texto else 0
        corazon = 1 if ("cardiaca" in texto or "cardíaca" in texto or "corazon" in texto or "corazón" in texto) else 0

        edad_val = float(edad_match.group(1)) if edad_match else 67.0
        glucosa_val = float(glucosa_match.group(1)) if glucosa_match else 180.0

        user_provided = bool(edad_match or glucosa_match or hipertension or corazon)

        params = {
            "age": edad_val,
            "hypertension": hipertension,
            "heart_disease": corazon,
            "avg_glucose_level": glucosa_val,
            "bmi": 29.5,
            "gender": "Male",
            "ever_married": "Yes",
            "work_type": "Private",
            "residence_type": "Urban",
            "smoking_status": "smokes"
        }

        if user_provided:
            res = ml_service.predict_stroke(**params)
            prob = res["probabilidad_evento_vascular"]
            diag = res["diagnostico"]
            mensaje = f"{prefijo} Evaluación completada: **{diag}** ({prob}% de probabilidad). {res['recomendacion']} {sufijo}"
            return {
                "success": True,
                "intencion": "triaje_stroke",
                "interactive_model": "stroke",
                "params": params,
                "has_prediction": True,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": res
            }
        else:
            if es_d10s:
                mensaje = "¡Atendido! Para evaluar factores de riesgo de accidente cerebrovascular, configurá edad, glucosa, antecedentes de salud e IMC en el panel:"
            else:
                mensaje = "¡Evaluación médica iniciada! Configura edad, glucosa, presión arterial e IMC en el panel interactivo para calcular el nivel de riesgo:"

            return {
                "success": True,
                "intencion": "triaje_stroke",
                "interactive_model": "stroke",
                "params": params,
                "has_prediction": False,
                "comando_original": payload.transcript,
                "respuesta_texto": mensaje,
                "datos": None
            }

    # =========================================================================
    # 6. GRASA CORPORAL / COMPOSICIÓN ANTROPOMÉTRICA
    # =========================================================================
    elif any(k in texto for k in ["grasa", "bodyfat", "corporal", "pliegue", "antropom"]):
        params = {
            "age": 29.0, "weight": 154.25, "height": 67.75, "neck": 36.2,
            "chest": 93.1, "abdomen": 85.2, "hip": 94.5, "thigh": 59.0,
            "knee": 37.3, "ankle": 21.9, "biceps": 32.0, "forearm": 27.4,
            "wrist": 17.1
        }
        res = ml_service.predict_bodyfat(**params)
        if es_d10s:
            mensaje = "¡Ajustemos la condición física! Modificá las medidas antropométricas en el panel interactivo para calcular tu porcentaje de grasa corporal:"
        else:
            mensaje = "¡Rendimiento físico de élite! Configura tus medidas en el panel para estimar tu porcentaje exacto de grasa corporal:"

        return {
            "success": True,
            "intencion": "estimacion_grasa_corporal",
            "interactive_model": "bodyfat",
            "params": params,
            "has_prediction": False,
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": None
        }

    # =========================================================================
    # 7. HEPATITIS C / PERFIL BIOQUÍMICO
    # =========================================================================
    elif any(k in texto for k in ["hepatitis", "hígado", "higado", "hepátic", "hepatic", "transaminasa", "alt", "ast"]):
        params = {
            "age": 35.0, "sex": "m", "alb": 38.5, "alp": 52.5, "alt": 7.7,
            "ast": 22.1, "bil": 7.5, "che": 6.93, "chol": 3.23, "crea": 106.0,
            "ggt": 12.1, "prot": 69.0
        }
        if es_d10s:
            mensaje = "¡Chequeo hepático iniciado! Modificá los biomarcadores séricos en el panel para evaluar si hay indicios de patología hepática:"
        else:
            mensaje = "¡Diagnóstico bioquímico de Hepatitis C activado! Ingresa los valores de laboratorio en el panel para evaluar el estado hepático:"

        return {
            "success": True,
            "intencion": "diagnostico_hepatitis",
            "interactive_model": "hepatitis",
            "params": params,
            "has_prediction": False,
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": None
        }

    # =========================================================================
    # 8. CIRROSIS HEPÁTICA / ESTADIFICACIÓN HISTOLÓGICA
    # =========================================================================
    elif any(k in texto for k in ["cirrosis", "estadio", "fibrosis", "ascitis", "hepatomegalia"]):
        params = {
            "n_days": 1000.0, "age_years": 50.0, "sex": "F", "bilirubin": 1.5,
            "cholesterol": 260.0, "albumin": 3.4, "copper": 70.0, "alk_phos": 1200.0,
            "sgot": 110.0, "tryglicerides": 115.0, "platelets": 250.0, "prothrombin": 10.6,
            "drug": "D-penicillamine", "ascites": "N", "hepatomegaly": "N",
            "spiders": "N", "edema": "N", "status": "C"
        }
        if es_d10s:
            mensaje = "¡Estadificación de cirrosis lista! Ajustá los indicadores clínicos en el panel para clasificar el estadio histológico (1 al 4):"
        else:
            mensaje = "¡Protocolo clínico de cirrosis en línea! Configura los biomarcadores en el panel para estadificar el avance de la afección:"

        return {
            "success": True,
            "intencion": "estadificacion_cirrosis",
            "interactive_model": "cirrosis",
            "params": params,
            "has_prediction": False,
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": None
        }

    # =========================================================================
    # 9. BITCOIN / PROYECCIÓN FINANCIERA CRIPTO
    # =========================================================================
    elif any(k in texto for k in ["bitcoin", "btc", "cripto", "crypto", "blockchain"]):
        params = {
            "open": 2500.0, "high": 2580.0, "low": 2470.0,
            "volume": 1500000000.0, "market_cap": 41000000000.0
        }
        if es_d10s:
            mensaje = "¡Mercado cripto listo! Ajustá los precios de apertura, máximos y volumen en el panel para proyectar el precio de cierre de Bitcoin:"
        else:
            mensaje = "¡Trading inteligente activado! Configura las variables del mercado en el panel para predecir el valor de cierre de Bitcoin:"

        return {
            "success": True,
            "intencion": "prediccion_bitcoin",
            "interactive_model": "bitcoin",
            "params": params,
            "has_prediction": False,
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": None
        }

    # =========================================================================
    # 10. S&P 500 / ACCIONES BURSÁTILES
    # =========================================================================
    elif any(k in texto for k in ["sp500", "s&p", "acciones", "bolsa", "wall street", "accion", "stock"]):
        params = {
            "open": 150.0, "high": 152.5, "low": 149.0, "volume": 1200000.0
        }
        if es_d10s:
            mensaje = "¡Panel bursátil abierto! Configurá los precios del S&P 500 para estimar la cotización de cierre de la acción:"
        else:
            mensaje = "¡Mercados financieros internacionales! Ajusta los valores de cotización en el panel para predecir el cierre del S&P 500:"

        return {
            "success": True,
            "intencion": "prediccion_sp500",
            "interactive_model": "sp500",
            "params": params,
            "has_prediction": False,
            "comando_original": payload.transcript,
            "respuesta_texto": mensaje,
            "datos": None
        }

    # =========================================================================
    # 11. MEMORIA CONVERSACIONAL (Continuación de turno previo estilo Gemini)
    # =========================================================================
    last_model = None
    last_params = {}
    if payload.history:
        for turn in reversed(payload.history):
            if isinstance(turn, dict) and turn.get("interactive_model"):
                last_model = turn.get("interactive_model")
                last_params = turn.get("params") or {}
                break

    if last_model and any(w in texto for w in ["ahora", "cambia", "pon", "ponele", "ajusta", "con", "y si", "valor"]):
        num_matches = re.findall(r'(\d+(?:\.\d+)?)', texto)
        msg = f"{prefijo} Recordando nuestro contexto previo de **{last_model.upper()}**, ajusté el panel con los parámetros actualizados. {sufijo}"
        return {
            "success": True,
            "intencion": f"continuacion_{last_model}",
            "interactive_model": last_model,
            "params": last_params,
            "has_prediction": False,
            "comando_original": payload.transcript,
            "respuesta_texto": msg,
            "datos": None
        }

    # =========================================================================
    # Saludo General / Consulta libre
    # =========================================================================
    else:
        if es_d10s:
            saludo = "¡Hola che! Soy el Core D10S de 10N-AI. Preguntame lo que necesites sobre cualquiera de los 10 modelos de IA: calidad de vino, tasación de autos, fuga de clientes, precio de aguacates, riesgo de infarto cerebral, grasa corporal, diagnóstico de hepatitis, cirrosis, cotización de Bitcoin o acciones del S&P 500. También podés encender tu cámara para analizar emociones. ¿Qué querés consultar?"
        else:
            saludo = "¡Siuuu! Core CR7 en línea. Máxima precisión y potencia para tus consultas con los 10 modelos de Inteligencia Artificial (autos, vino, clientes, aguacate, salud ACV, grasa corporal, hepatitis, cirrosis, Bitcoin y S&P 500) y visión artificial. Dime en qué te puedo ayudar:"

        return {
            "success": True,
            "intencion": "saludo_general",
            "interactive_model": None,
            "params": None,
            "has_prediction": False,
            "comando_original": payload.transcript,
            "respuesta_texto": saludo,
            "datos": None
        }

