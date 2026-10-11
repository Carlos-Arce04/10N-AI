import os
from pathlib import Path

# Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # carpeta backend/
PROJECT_ROOT = BASE_DIR.parent                          # raíz del repo 10N-AI/
MODELS_DIR = PROJECT_ROOT / "models"
VISION_MODELS_DIR = BASE_DIR / "app" / "models_vision"

# Configuración del servidor
API_TITLE = "10N-AI: Asistente Inteligente Backend"
API_VERSION = "1.0.0"
API_DESCRIPTION = "API RESTful para el Asistente 10N-AI: Visión por computadora, Percepción de Emociones y Modelos de Machine Learning."

# Orígenes permitidos para CORS (Frontend React + Vite)
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
