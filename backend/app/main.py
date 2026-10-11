import sys
from pathlib import Path

# Garantizar que la carpeta backend esté en sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import API_TITLE, API_VERSION, API_DESCRIPTION, ALLOWED_ORIGINS
from app.api.routes_vision import router as vision_router
from app.api.routes_command import router as command_router

# Routers modulares dedicados por cada modelo de Machine Learning
from app.api.routes_car import router as car_router
from app.api.routes_wine import router as wine_router
from app.api.routes_churn import router as churn_router
from app.api.routes_avocado import router as avocado_router
from app.api.routes_stroke import router as stroke_router

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Configuración de CORS para permitir peticiones desde React + Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers de visión y asistente conversacional
app.include_router(vision_router)
app.include_router(command_router)

# Inclusión de routers modulares por modelo (arquitectura REST limpia)
# 1. Rutas dedicadas por servicio: /api/aguacate, /api/vino, /api/auto, /api/churn, /api/stroke
app.include_router(avocado_router, prefix="/api")
app.include_router(wine_router, prefix="/api")
app.include_router(car_router, prefix="/api")
app.include_router(churn_router, prefix="/api")
app.include_router(stroke_router, prefix="/api")

# Alias en inglés para aguacate (/api/avocado)
app.include_router(avocado_router, prefix="/api", tags=["🥑 Avocado API (English Alias)"])

# 2. Rutas con prefijo /api/predict para compatibilidad con el frontend interactivo
app.include_router(avocado_router, prefix="/api/predict", include_in_schema=False)
app.include_router(wine_router, prefix="/api/predict", include_in_schema=False)
app.include_router(car_router, prefix="/api/predict", include_in_schema=False)
app.include_router(churn_router, prefix="/api/predict", include_in_schema=False)
app.include_router(stroke_router, prefix="/api/predict", include_in_schema=False)

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "10N-AI Modular Architecture & Cognitive Engine",
        "version": API_VERSION,
        "docs_url": "/docs",
        "apis_modulares": {
            "aguacate": {
                "predict": "/api/aguacate/predict",
                "health": "/api/aguacate/health",
                "regions": "/api/aguacate/regions",
                "types": "/api/aguacate/types"
            },
            "vino": {
                "predict": "/api/vino/predict",
                "health": "/api/vino/health"
            },
            "autos": {
                "predict": "/api/auto/predict",
                "health": "/api/auto/health",
                "options": "/api/auto/options"
            },
            "churn": {
                "predict": "/api/churn/predict",
                "health": "/api/churn/health",
                "options": "/api/churn/options"
            },
            "stroke": {
                "predict": "/api/stroke/predict",
                "health": "/api/stroke/health",
                "options": "/api/stroke/options"
            }
        },
        "asistente_voz": "/api/command/process",
        "vision_computacional": "/api/vision/sentiment"
    }

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "10N-AI-Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
