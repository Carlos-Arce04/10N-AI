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
from app.api.routes_predict import router as predict_router
from app.api.routes_command import router as command_router

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

# Inclusión de routers modulares
app.include_router(vision_router)
app.include_router(predict_router)
app.include_router(command_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "10N-AI Cognitive & Vision Engine",
        "version": API_VERSION,
        "docs_url": "/docs",
        "endpoints": [
            "/api/vision/sentiment",
            "/api/vision/sentiment-base64",
            "/api/command/process",
            "/api/predict/auto",
            "/api/predict/vino",
            "/api/predict/churn",
            "/api/predict/aguacate",
            "/api/predict/stroke"
        ]
    }

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "10N-AI-Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
