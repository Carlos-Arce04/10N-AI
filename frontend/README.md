# Frontend // 10N-AI Multimodal Assistant HUD 💻

Interfaz de usuario interactiva y HUD futurista (estilo Jarvis / Cyberpunk) desarrollado con **React + Vite + Tailwind CSS**.

### Módulos Implementados:
1. **Selector Dual-Core de Personalidad:**
   - 🇦🇷 **Core D10S (Messi):** Temática cyan/albiceleste, partículas y tono reflexivo/efectivo.
   - 🇵🇹 **Core CR7 (Cristiano):** Temática carmesí/dorada, alta energía y tono de máxima precisión.
2. **Percepción Visual en Tiempo Real:**
   - Captura de fotogramas de la webcam mediante HTML5 Canvas.
   - Recuadro holográfico sobre el rostro con esquinas Sci-Fi.
   - Clasificación de 8 emociones faciales en vivo (OpenCV DNN + CNN FER+).
3. **Comandos de Voz (Speech-to-Text & Text-to-Speech):**
   - Transcripción de voz en tiempo real con Google Chrome Web Speech API.
   - Procesamiento de intenciones e inferencia en los modelos de Machine Learning.
   - Respuesta auditiva hablada por el navegador con modulación de voz según la personalidad activa.
4. **Hub de Modelos de Machine Learning (10 Modelos):**
   - **Bloque A (Carlos Arce - Activos en producción):**
     - 01: Predicción de precio de automóviles (Random Forest Regressor, $R^2 = 0.88$).
     - 02: Clasificación de calidad del vino (Random Forest Classifier, Recall = 83.7%).
     - 03: Predicción de fuga de clientes Telco (Random Forest Balanced, Recall = 77.3%).
     - 04: Predicción de precio del aguacate (Duelo RF vs Red Neuronal MLP, $R^2 = 0.9089$).
     - 05: Detección clínica de ACV / Stroke (Support Vector Machine RBF, Recall = 80.0%).
   - **Bloque B (Joshua Picado - Próximamente):**
     - 06: Grasa Corporal (Body Fat).
     - 07: Hepatitis C.
     - 08: Cirrosis Hepática.
     - 09: Bitcoin.
     - 10: S&P 500.
5. **Consola de Telemetría:**
   - Registro en tiempo real de logs del sistema, ping de salud al backend y latencia.

### Ejecución en Desarrollo:
```bash
npm install
npm run dev
```
La aplicación correrá en `http://localhost:5173`.
