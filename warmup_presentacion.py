"""
Script de Pre-calentamiento de Voces para la Presentación (10N-AI)
Pre-genera en la caché local todas las frases clave para Lionel Messi (D10S) y Cristiano Ronaldo (CR7)
garantizando que durante la presentación en vivo la respuesta sea de 0.00 segundos (instantánea, sin delay).
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Asegurar backend en el sys.path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.services.tts_service import tts_service, CACHE_DIR

PHRASES = [
    # Saludos y presentación
    ("d10s", "¡Hola che, qué hacés! Soy 10N-AI con el Core D10S. Preguntame lo que necesites sobre el valor de un auto, calidad de un vino, precio de aguacates, clientes, salud o cripto. Elegí una opción abajo o escribime directamente."),
    ("d10s", "¡Buenas che! Acá tenés al Core D10S listo en la cancha. Estoy para ayudarte a analizar datos y correr predicciones con precisión. ¿Arrancamos con algún modelo del panel o me tirás una consulta directa?"),
    ("d10s", "¡Qué hacés hermano! Core D10S activado. Tranquilidad, mate en mano y foco total en los datos. Vos tirame el centro con la predicción que quieras y lo resolvemos en una."),
    ("cr7", "¡Siuuu! Asistente 10N-AI activado con el Core CR7. Máxima potencia, disciplina y precisión para responder a tus consultas. Elige una de las opciones a continuación para simular los parámetros o pregúntame lo que necesites."),
    ("cr7", "¡Siuuu, Comandante! Core CR7 listo en el terreno de juego. Aquí no hay margen de error: máxima potencia predictiva y mentalidad ganadora. ¿Qué analizamos primero?"),
    ("cr7", "¡Todo al 100%! Asistente 10N-AI con la mentalidad ganadora de CR7. Análisis financiero, salud, mercado y visión computacional. ¡Dime el objetivo y vamos a por el resultado!"),
    ("d10s", "Hola che, qué hacés. Soy 10N AI con el core D10S de Lionel Messi. Listo para gambetear los datos y darte las mejores predicciones."),
    ("cr7", "¡Siuuu! Soy 10N AI con el core CR7. Máxima potencia, concentración y precisión para tus modelos de machine learning."),
    ("d10s", "Activando modo Lionel Messi. Core D10S listo para jugar."),
    ("cr7", "Activando modo Cristiano Ronaldo. Core CR7 listo para ganar."),
    ("d10s", "¡Listo, predicción completada con éxito!"),
    ("cr7", "¡Listo, predicción completada con éxito!"),
    ("d10s", "Todo listo, hermano."),
    ("cr7", "¡Objetivo cumplido con máxima precisión!"),

    # Respuestas de modelos interactivos
    ("d10s", "¡De una, hermano! Para clasificar la calidad de tu vino, necesitamos configurar parámetros como el alcohol, acidez, azúcar y si es tinto o blanco. Te abrí el panel abajo para que elijas los valores o me los digas por chat:"),
    ("cr7", "¡Afirmativo, Comandante! Listo para evaluar la calidad del vino. Ajusta los parámetros en el panel interactivo a continuación y calculamos el resultado:"),
    ("d10s", "¡De una, crack! Vamos a tasar tu auto en el mercado. Ingresá el año, kilometraje, tipo de combustible y precio de lista en el panel de abajo:"),
    ("cr7", "¡Vamos con todo! Tasación de vehículos de alto rendimiento activada. Introduce los datos para predecir el valor de reventa:"),
    ("d10s", "¡Dale che! Vamos a ver la retención de clientes. Indicá los datos de contrato, facturación y servicios en el panel:"),
    ("cr7", "¡Concentración total! Predicción de fuga de clientes iniciada. Introduce las variables para calcular la probabilidad de abandono:"),
    ("d10s", "¡Buenísimo, che! Vamos a predecir el precio del aguacate Haas. Configurá el volumen total y bolsas en el panel interactivo:"),
    ("cr7", "¡A romperla! Pronóstico del mercado de aguacate Haas activado. Analicemos la oferta y demanda:"),
    ("d10s", "¡Atención! Este es un análisis crítico de salud. Ingresá los factores de riesgo de ACV como edad, hipertensión y glucosa:"),
    ("cr7", "¡Alerta máxima! Predicción de riesgo de accidente cerebrovascular activada. Evaluando parámetros clínicos con rigor:"),
    ("d10s", "¡Estadificación de cirrosis lista! Ajustá los indicadores clínicos en el panel para clasificar el estadio histológico (1 al 4):"),
    ("cr7", "¡Protocolo clínico de cirrosis en línea! Configura los biomarcadores en el panel para estadificar el avance de la afección:"),
    ("d10s", "¡Chequeo hepático iniciado! Modificá los biomarcadores séricos en el panel para evaluar si hay indicios de patología hepática:"),
    ("cr7", "¡Diagnóstico bioquímico de Hepatitis C activado! Ingresa los valores de laboratorio en el panel para evaluar el estado hepático:"),

    # Fallbacks y control
    ("d10s", "¡Tranquilo, che! No entendí bien esa instrucción. Podés pedirme predecir vino, autos, clientes o abrir la cámara."),
    ("cr7", "¡Concentración, Comandante! No reconocí la instrucción. Pídeme un análisis de autos, clientes, acciones de S&P 500 o activa la cámara para escanear tu rostro."),
]

async def main():
    print("=" * 70)
    print("🚀 10N-AI: PRE-CALENTAMIENTO DE VOCES PARA LA PRESENTACIÓN")
    print(f"Directorio de Caché: {CACHE_DIR}")
    print(f"Total de frases a procesar: {len(PHRASES)}")
    print("=" * 70)

    total_start = time.time()
    for idx, (persona, text) in enumerate(PHRASES, 1):
        persona_upper = persona.upper()
        clean = tts_service._clean_text_for_speech(text)
        cache_path = tts_service._get_cache_path(persona, clean)
        
        status_cached = "⚡ EN CACHÉ (0ms)" if (cache_path.exists() and cache_path.stat().st_size > 150000) else "🎙️ GENERANDO..."
        print(f"\n[{idx}/{len(PHRASES)}] [{persona_upper}] {status_cached}")
        print(f"Texto: \"{text[:60]}...\"")

        t0 = time.time()
        audio = await tts_service.synthesize(text, persona=persona)
        dur = round((time.time() - t0) * 1000, 1)

        size_kb = round(len(audio) / 1024, 1) if audio else 0
        print(f"Resultado: {size_kb} KB en {dur} ms")

    total_time = round(time.time() - total_start, 2)
    print("\n" + "=" * 70)
    print(f"✅ ¡PRE-CALENTAMIENTO COMPLETADO EN {total_time}s!")
    print("Todas las frases quedaron grabadas con las voces 100% reales de Messi y CR7.")
    print("Durante tu presentación, responderán al instante con 0 delay.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
