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
from app.api.routes_tts import router as tts_router

# Routers modulares dedicados por cada modelo de Machine Learning
from app.api.routes_car import router as car_router
from app.api.routes_wine import router as wine_router
from app.api.routes_churn import router as churn_router
from app.api.routes_avocado import router as avocado_router
from app.api.routes_stroke import router as stroke_router
from app.api.routes_bodyfat import router as bodyfat_router
from app.api.routes_hepatitis import router as hepatitis_router
from app.api.routes_cirrhosis import router as cirrhosis_router
from app.api.routes_bitcoin import router as bitcoin_router
from app.api.routes_sp500 import router as sp500_router

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

@app.on_event("startup")
def ensure_rvc_daemon():
    """Garantiza en segundo plano que el microservicio daemon RVC en RAM (Python 3.10) esté siempre activo."""
    import threading
    def _check_and_start():
        import urllib.request
        import os
        import subprocess
        try:
            with urllib.request.urlopen("http://127.0.0.1:8005/health", timeout=1) as res:
                if res.status == 200:
                    return
        except Exception:
            pass

        daemon_script = Path(__file__).resolve().parent / "services" / "rvc_daemon.py"
        root_dir = Path(__file__).resolve().parents[2]
        candidates = [
            os.environ.get("PYTHON_RVC_PATH", ""),
            r"C:\Users\carlo\AppData\Local\Programs\Python\Python310\python.exe",
            sys.executable,
            shutil.which("python3.10") or "",
            shutil.which("python") or ""
        ]
        python_exe = next((c for c in candidates if c and os.path.isfile(c)), sys.executable)

        if daemon_script.is_file():
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            log_path = root_dir / "backend" / "rvc_daemon.log"
            try:
                log_f = open(log_path, "a", encoding="utf-8")
                subprocess.Popen(
                    [python_exe, str(daemon_script)],
                    cwd=str(root_dir),
                    stdout=log_f,
                    stderr=log_f,
                    creationflags=creation_flags
                )
            except Exception as e:
                print(f"[Startup Warning] No se pudo lanzar el daemon RVC automáticamente: {e}")

    threading.Thread(target=_check_and_start, daemon=True).start()

# Inclusión de routers de visión y asistente conversacional
app.include_router(vision_router)
app.include_router(command_router)
app.include_router(tts_router)

# Inclusión de routers modulares por modelo (arquitectura REST limpia)
# 1. Rutas dedicadas por servicio: /api/aguacate, /api/vino, /api/auto, /api/churn, /api/stroke, /api/bodyfat, etc.
app.include_router(avocado_router, prefix="/api")
app.include_router(wine_router, prefix="/api")
app.include_router(car_router, prefix="/api")
app.include_router(churn_router, prefix="/api")
app.include_router(stroke_router, prefix="/api")
app.include_router(bodyfat_router, prefix="/api")
app.include_router(hepatitis_router, prefix="/api")
app.include_router(cirrhosis_router, prefix="/api")
app.include_router(bitcoin_router, prefix="/api")
app.include_router(sp500_router, prefix="/api")

# Alias en inglés para aguacate (/api/avocado)
app.include_router(avocado_router, prefix="/api", tags=["🥑 Avocado API (English Alias)"])

# 2. Rutas con prefijo /api/predict para compatibilidad con el frontend interactivo
app.include_router(avocado_router, prefix="/api/predict", include_in_schema=False)
app.include_router(wine_router, prefix="/api/predict", include_in_schema=False)
app.include_router(car_router, prefix="/api/predict", include_in_schema=False)
app.include_router(churn_router, prefix="/api/predict", include_in_schema=False)
app.include_router(stroke_router, prefix="/api/predict", include_in_schema=False)
app.include_router(bodyfat_router, prefix="/api/predict", include_in_schema=False)
app.include_router(hepatitis_router, prefix="/api/predict", include_in_schema=False)
app.include_router(cirrhosis_router, prefix="/api/predict", include_in_schema=False)
app.include_router(bitcoin_router, prefix="/api/predict", include_in_schema=False)
app.include_router(sp500_router, prefix="/api/predict", include_in_schema=False)


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
            },
            "grasa_corporal": {
                "predict": "/api/bodyfat/predict",
                "health": "/api/bodyfat/health"
            },
            "hepatitis": {
                "predict": "/api/hepatitis/predict",
                "health": "/api/hepatitis/health"
            },
            "cirrosis": {
                "predict": "/api/cirrosis/predict",
                "health": "/api/cirrosis/health"
            },
            "bitcoin": {
                "predict": "/api/bitcoin/predict",
                "health": "/api/bitcoin/health"
            },
            "sp500": {
                "predict": "/api/sp500/predict",
                "health": "/api/sp500/health"
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
