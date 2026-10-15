# 10N-AI (Ten AI)

**Proyecto I - Inteligencia Artificial**  
**Instituto Tecnológico de Costa Rica (TEC) - Campus San Carlos**  
**Profesor:** Ing. Efrén Jiménez Delgado  
**Estudiantes:** Carlos Arce & Joshua Picado  

---

## Descripción del Proyecto

10N-AI es un sistema interactivo y multimodal de inteligencia artificial diseñado como centro de comando y asistencia clínica, financiera y analítica. El proyecto integra percepción de voz, visión por computadora, síntesis vocal de alta fidelidad y un motor predictivo basado en 10 modelos de Machine Learning entrenados sobre problemas del mundo real.

El asistente dispone de una interfaz visual tipo HUD que permite alternar entre dos núcleos de procesamiento con identidades personalizadas:
- **Core D10S:** Personalidad inspirada en Lionel Messi (prosodia argentina, visualización celeste y blanca).
- **Core CR7:** Personalidad inspirada en Cristiano Ronaldo (prosodia peninsular, visualización roja y dorada).

---

## Pilares Funcionales del Sistema

1. **Percepción Auditiva y Procesamiento de Lenguaje Natural:**
   Reconocimiento de comandos de voz mediante Web Speech API / Speech-to-Text y un procesador semántico de intenciones capaz de derivar consultas clínicas, financieras y operativas hacia los modelos correspondientes.

2. **Síntesis Vocal Multimodal (RVC v2 + Edge-TTS):**
   Arquitectura de clonación vocal en dos fases. Genera una base fonética neuronal que luego es transformada tímbricamente mediante modelos convolucionales entrenados con grabaciones reales de Lionel Messi y Cristiano Ronaldo.

3. **Percepción Visual y Análisis Emocional:**
   Módulo de visión por computadora capaz de capturar el rostro del usuario en tiempo real y clasificar estados emocionales para adaptar el comportamiento del asistente.

4. **Motor Predictivo de 10 Modelos de Machine Learning:**
   Conjunto de modelos supervisados (clasificación y regresión) serializados en formato Joblib, optimizados para inferencia en tiempo real a través de endpoints REST.

5. **Avatares de Partículas Estilo Drone Show:**
   Representación visual de los núcleos mediante una malla facial de 392 partículas con cinemática mandibular en tiempo real sincronizada con la amplitud del audio reproducido.

---

## Arquitectura de Síntesis de Voz

El subsistema de audio resuelve el desafío de generar respuestas habladas con timbre de voz personalizado y latencia imperceptible durante la interacción en vivo.

```
[Texto de Respuesta]
         │
         ▼
[Fase 1: Generación Base Neuronal - Edge-TTS]
  ├── Core D10S: es-AR-TomasNeural (prosodia y cadencia rioplatense)
  └── Core CR7:  es-ES-AlvaroNeural (entonación peninsular)
         │  (Genera audio base .wav en ~300 ms)
         ▼
[Fase 2: Conversión Tímbrica - RVC v2 (Retrieval-based Voice Conversion)]
  ├── Extracción de Frecuencia Fundamental: Algoritmo RMVPE (Robust Pitch Estimation)
  ├── Mapeo de Huella Vocal: Modelos convolucionales entrenados con cuerdas vocales reales
  ├── Alineación de Armónicos: Índices FAISS (.index) para preservación tímbrica
  └── Aceleración por Hardware: PyTorch con soporte CUDA (GPU) y fallback adaptativo en CPU
         │  (Inferencia en memoria caliente: ~800 ms)
         ▼
[Fase 3: Servicio Daemon en Memoria + Caché SHA-256]
  ├── Microservicio `rvc_daemon.py` residente en memoria (puerto 8005)
  ├── Indexación por hash SHA-256: sha256(persona + texto) en `backend/audio_cache/`
  └── Reproducción en Demostración: 0.00 ms (Lectura directa de archivo precalculado)
```

### Componentes de Audio Implementados

- **`backend/app/services/tts_service.py`:** Orquestador principal de síntesis. Controla la consulta de caché, invocación al daemon, fallback a CLI worker y políticas de integridad de archivos.
- **`backend/app/services/rvc_daemon.py`:** Servidor FastAPI en segundo plano que mantiene los pesos de los modelos cargados en VRAM, eliminando el tiempo de inicialización de PyTorch en cada consulta.
- **`backend/app/services/rvc_bridge.py`:** Worker directo de respaldo por línea de comandos con soporte de deserialización segura de checkpoints.
- **`warmup_presentacion.py`:** Script de precalentamiento que genera y valida previamente 30 frases críticas para ambos personajes, asegurando ejecución inmediata durante presentaciones.
- **Protección de Caché:** Validación estricta del tamaño de archivo generado (> 150 KB). Si la conversión de voz falla, se reproduce un audio de respaldo pero nunca se guarda en disco para evitar corromper la caché.

---

## Avatares de Partículas y Cinemática Facial

El componente `ParticleAvatar.jsx` implementa una simulación en Canvas 2D:

- **Topología Balanceada:** Ambos modelos faciales (Messi y Cristiano) fueron optimizados para compartir una topología idéntica de exactamente **392 partículas**, lo que permite transiciones de morfología facial continuas sin saltos geométricos.
- **Cinemática Mandibular:** Las partículas correspondientes al maxilar inferior se desplazan verticalmente de acuerdo con el nivel RMS del audio en reproducción, mientras que la estructura craneal y el maxilar superior permanecen estables.
- **Gestión de Políticas de Autoplay:** Los navegadores modernos bloquean la reproducción de audio no iniciada por el usuario. La interfaz registra listeners de interacción inicial (`pointerdown`, `click`, `keydown`) para desbloquear el contexto de audio y reproducir el saludo inicial de manera fluida sin errores de ejecución.

---

## Portafolio de los 10 Modelos de Machine Learning

| # | Problema Clínico / Técnico | Tipo de Tarea | Algoritmo Seleccionado | Variables de Entrada Principales | Métricas de Rendimiento |
|---|---|---|---|---|---|
| 01 | Predicción de Precio de Automóviles | Regresión | Random Forest Regressor | Cilindrada, caballos de fuerza, peso vehicular, consumo en carretera y ciudad | R2: 0.92, RMSE |
| 02 | Clasificación de Calidad del Vino | Clasificación | Random Forest Classifier | Acidez fija, acidez volátil, ácido cítrico, azúcar residual, cloruros, pH, alcohol | F1-Score: 0.81, Accuracy |
| 03 | Predicción de Abandono de Clientes (Telco Churn) | Clasificación | Random Forest / Regresión Logística | Antigüedad (tenure), tipo de contrato, cargos mensuales, cargos totales, soporte técnico | ROC-AUC: 0.85, Recall: 0.79 |
| 04 | Predicción del Precio del Aguacate | Regresión | Random Forest Regressor | Volumen total vendido, bolsas pequeñas/grandes, tipo (convencional/orgánico), región, año | R2: 0.89, MAE |
| 05 | Detección de Riesgo de Accidente Cerebrovascular (Stroke) | Clasificación | Balanced Random Forest Classifier | Edad, hipertensión, cardiopatía, nivel promedio de glucosa, índice de masa corporal (IMC), tabaquismo | ROC-AUC: 0.84, Recall: 0.82 |
| 06 | Estimación de Porcentaje de Grasa Corporal | Regresión | Random Forest / Ridge Regressor | Edad, peso, estatura, circunferencias corporales (cuello, tórax, abdomen, cadera, muslo) | RMSE: 4.12, R2: 0.74 |
| 07 | Clasificación y Tamizaje de Hepatitis C | Clasificación | Random Forest / Support Vector Machine | Biomarcadores séricos: AST, ALT, ALP, bilirrubina, albúmina, colinesterasa, colesterol | Accuracy: 0.94, F1-Score: 0.91 |
| 08 | Diagnóstico y Estadificación de Cirrosis Hepática | Clasificación Multiclase | Gradient Boosting / Random Forest | Estadio histológico (1 a 4), albúmina, bilirrubina, tiempo de protrombina, plaquetas, cobre, ascitis | Multiclass F1-Score: 0.83 |
| 09 | Predicción de Tendencia de Precio de Bitcoin | Regresión | Random Forest / Regresión Lineal | Precios de apertura, máximos, mínimos, volumen transaccional y retardos históricos | R2: 0.95, RMSE |
| 10 | Valoración de Acciones del Índice S&P 500 | Regresión | Random Forest / Ridge Regressor | Capitalización bursátil, ratio precio/beneficio (P/E), rendimiento de dividendos, beta | R2: 0.88, MAE |

---

## Estructura del Repositorio

```text
10N-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_avocado.py      # Endpoints para predicción de aguacate
│   │   │   ├── routes_bitcoin.py      # Endpoints para predicción de bitcoin
│   │   │   ├── routes_bodyfat.py      # Endpoints para estimación de grasa corporal
│   │   │   ├── routes_car.py          # Endpoints para precio de autos
│   │   │   ├── routes_churn.py        # Endpoints para retención de clientes
│   │   │   ├── routes_cirrhosis.py    # Endpoints para estadificación de cirrosis
│   │   │   ├── routes_command.py      # Procesador de lenguaje natural y comandos de voz
│   │   │   ├── routes_hepatitis.py    # Endpoints para clasificación de hepatitis C
│   │   │   ├── routes_sp500.py        # Endpoints para valoración del S&P 500
│   │   │   ├── routes_stroke.py       # Endpoints para detección de ACV
│   │   │   ├── routes_tts.py          # Endpoints de síntesis de voz
│   │   │   ├── routes_vision.py       # Endpoints para análisis facial
│   │   │   └── routes_wine.py         # Endpoints para calidad de vino
│   │   ├── core/                      # Configuraciones globales y constantes
│   │   ├── models/                    # Clases de validación Pydantic
│   │   ├── services/
│   │   │   ├── rvc_bridge.py          # Worker CLI de inferencia RVC
│   │   │   ├── rvc_daemon.py          # Microservicio daemon de inferencia en memoria
│   │   │   └── tts_service.py         # Orquestador del pipeline de síntesis vocal
│   │   └── main.py                    # Punto de entrada de la aplicación FastAPI
│   ├── audio_cache/                   # Caché persistente de audios precalculados (.wav)
│   └── requirements.txt               # Dependencias Python del backend
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatHistorySidebar.jsx # Historial de conversaciones
│   │   │   ├── ChatInterface.jsx      # Interfaz conversacional, voz y comandos
│   │   │   ├── ModelSimulatorCard.jsx # Formularios interactivos para los 10 modelos
│   │   │   ├── Navbar.jsx             # Selector de Core (D10S / CR7) y estado del sistema
│   │   │   └── ParticleAvatar.jsx     # Renderizado de avatar de partículas en canvas
│   │   ├── data/
│   │   │   └── facePoints.json        # Mallas de partículas sincronizadas (392 puntos)
│   │   ├── App.jsx                    # Contenedor principal de la aplicación
│   │   └── main.jsx                   # Montaje de la aplicación React
│   ├── package.json                   # Dependencias y scripts de Node.js
│   └── vite.config.js                 # Configuración de empaquetado Vite
├── models/
│   ├── rvc/                           # Pesos de clonación vocal (.pth, .index)
│   ├── modelo_01_autos.joblib
│   ├── modelo_02_vino.joblib
│   ├── modelo_03_churn.joblib
│   ├── modelo_04_aguacate.joblib
│   ├── modelo_05_stroke.joblib
│   ├── modelo_06_bodyfat.joblib
│   ├── modelo_07_hepatitis.joblib
│   ├── modelo_08_cirrosis.joblib
│   ├── modelo_09_bitcoin.joblib
│   └── modelo_10_sp500.joblib
├── notebooks/                         # Cuadernos Jupyter con EDA, entrenamiento y métricas
├── warmup_presentacion.py             # Script de precálculo de audios para demostración
└── README.md                          # Documentación del proyecto
```

---

## Guía de Instalación y Ejecución Local

### Requisitos Previos

- Python 3.10 o superior.
- Node.js 18 o superior con npm.
- Opcional para inferencia en tiempo real de voz: Tarjeta gráfica NVIDIA con CUDA 11.8+ y cuDNN.
- Si no se dispone de tarjeta gráfica dedicada, el sistema puede operar mediante la caché precalculada o síntesis base de Edge-TTS sin interrupciones.

---

### Paso 1: Configuración del Backend

1. Crear y activar un entorno virtual de Python:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux / macOS:
   source .venv/bin/activate
   ```

2. Instalar las dependencias del backend:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Asegurar la presencia de los modelos serializados:
   Verificar que la carpeta `models/` contenga los 10 archivos `.joblib`. Los pesos pesados de clonación de voz (`models/rvc/`) y los audios en caché (`backend/audio_cache/`) se distribuyen mediante el almacenamiento compartido del equipo.

---

### Paso 2: Precarga de Voces (Demostración)

Para asegurar respuesta instantánea durante la presentación sin consumir recursos de procesamiento en vivo, ejecutar el script de precarga:

```bash
python warmup_presentacion.py
```

---

### Paso 3: Ejecución de Servidores

1. **Iniciar el Backend (FastAPI):**
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   El backend iniciará automáticamente el microservicio de inferencia de voz en segundo plano.

2. **Iniciar el Frontend (React + Vite):**
   En una terminal separada:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   La aplicación estará disponible en `http://localhost:5173`.

---

## Principales Endpoints de la API REST

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/health` | Estado del servicio y disponibilidad del backend |
| `POST` | `/api/command/process` | Procesamiento de comandos de lenguaje natural por voz o texto |
| `POST` | `/api/tts/synthesize` | Síntesis vocal mediante pipeline híbrido RVC v2 + Edge-TTS |
| `GET` | `/api/tts/status` | Estado operativo del daemon de voz y modo de inferencia |
| `POST` | `/api/vision/analyze` | Análisis facial en tiempo real para detección de emociones |
| `POST` | `/api/predict/auto` | Inferencia del modelo de precio de automóviles |
| `POST` | `/api/predict/wine` | Inferencia del modelo de calidad de vino |
| `POST` | `/api/predict/churn` | Inferencia del modelo de abandono de clientes |
| `POST` | `/api/predict/avocado` | Inferencia del modelo de precio de aguacate |
| `POST` | `/api/predict/stroke` | Inferencia del modelo de riesgo de accidente cerebrovascular |
| `POST` | `/api/predict/bodyfat` | Inferencia del modelo de porcentaje de grasa corporal |
| `POST` | `/api/predict/hepatitis` | Inferencia del modelo de clasificación de hepatitis C |
| `POST` | `/api/predict/cirrhosis` | Inferencia del modelo de estadificación de cirrosis |
| `POST` | `/api/predict/bitcoin` | Inferencia del modelo de precio de Bitcoin |
| `POST` | `/api/predict/sp500` | Inferencia del modelo de valoración del S&P 500 |

---

## Licencia y Créditos Académicos

Este proyecto ha sido desarrollado como trabajo académico para el curso de **Inteligencia Artificial** de la carrera de Ingeniería en Computación del **Instituto Tecnológico de Costa Rica (TEC)**, Campus San Carlos.
