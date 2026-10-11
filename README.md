# 10N-AI (Ten AI) ⚽🤖

**Proyecto I - Inteligencia Artificial**  
**Instituto Tecnológico de Costa Rica (TEC) - Campus San Carlos**  
**Profesor:** Ing. Efrén Jiménez Delgado  
**Estudiantes:** Carlos Arce & Joshua Picado  

---

## 🌟 Descripción del Proyecto
**10N-AI** es un asistente inteligente multimodal inspirado en la arquitectura de JARVIS, con una interfaz interactiva de visualización de datos y partículas en tiempo real con selector de personalidades (**Core D10S / Core CR7**).

El sistema integra:
1. **Percepción de Audio:** Reconocimiento de comandos por voz mediante Speech-to-Text.
2. **Percepción Visual:** Análisis facial de emociones y sentimientos a través de captura en tiempo real.
3. **API RESTful:** Backend de alto rendimiento construido con FastAPI.
4. **10 Modelos de Machine Learning:** Arquitecturas predictivas y clasificatorias entrenadas para resolver problemas del mundo real.
5. **Frontend Futurista:** Interfaz interactiva desarrollada en React + Tailwind CSS con HUD cyberpunk y animación de partículas.

---

## 📊 Portafolio de los 10 Modelos de ML

| # | Problema | Tipo | Algoritmo Seleccionado | Métrica Principal |
|---|---|---|---|---|
| 01 | Predicción de Precio de Automóviles | Regresión | Random Forest Regressor | $R^2$, RMSE |
| 02 | Clasificación de Calidad del Vino | Clasificación | Random Forest Classifier | F1-Score, Accuracy |
| 03 | Predicción de Abandono de Clientes (Telco Churn) | Clasificación | Random Forest / Regresión Logística | ROC-AUC, Recall |
| 04 | Predicción del Precio del Aguacate | Regresión | Random Forest Regressor | $R^2$, MAE |
| 05 | Detección de Accidente Cerebrovascular (Stroke) | Clasificación | Random Forest (Balanced) | ROC-AUC, Recall |
| 06 | Predicción de Masa / Grasa Corporal | Regresión | Random Forest / Ridge | RMSE, $R^2$ |
| 07 | Clasificación de Hepatitis C | Clasificación | Random Forest / SVM | Accuracy, F1-Score |
| 08 | Diagnóstico y Clasificación de Cirrosis | Clasificación | Gradient Boosting / RF | Multi-class F1 |
| 09 | Predicción del Precio de Bitcoin | Regresión | Random Forest / Regresión Lineal | $R^2$, RMSE |
| 10 | Predicción de Acciones del S&P 500 | Regresión | Random Forest / Ridge | $R^2$, MAE |

---

## 🛠️ Estructura del Repositorio

```text
10N-AI/
├── backend/            # API REST en FastAPI
├── frontend/           # Interfaz interactiva en React + Tailwind CSS
├── models/             # Artefactos serializados (.joblib) para inferencia rápida
├── notebooks/          # Cuadernos Jupyter / Google Colab (Entrenamiento y EDA)
└── README.md
```
