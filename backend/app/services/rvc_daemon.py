"""
Microservicio daemon de RVC v2 en memoria (Python 3.10).
Mantiene en memoria RAM los modelos de Lionel Messi y Cristiano Ronaldo
para conversiones instantáneas sin tiempo de arranque.
"""

import os
import sys
import torch
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Compatibilidad segura para PyTorch 2.6+ con checkpoints de RVC
_orig_torch_load = torch.load
def _safe_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = _safe_torch_load

from rvc_python.infer import RVCInference

app = FastAPI(title="10N-AI RVC Worker Daemon")

MODELS_DIR = Path(__file__).resolve().parents[3] / "models" / "rvc"

# Modelos en memoria persistente
rvc_instances = {}

@app.on_event("startup")
def load_all_models():
    use_cuda = torch.cuda.is_available()
    device = "cuda:0" if use_cuda else "cpu:0"
    f0method = "rmvpe" if use_cuda else "pm"
    print(f"[RVC Daemon] Inicializando modelos en memoria en {device} con f0method={f0method}...")

    # 1. Cargar Lionel Messi (D10S)
    messi_pth = MODELS_DIR / "messi.pth"
    messi_index = MODELS_DIR / "messi.index"
    if messi_pth.is_file():
        rvc_d10s = RVCInference(device=device)
        rvc_d10s.load_model(str(messi_pth), version="v2", index_path=str(messi_index) if messi_index.is_file() else "")
        rvc_d10s.set_params(f0method=f0method, index_rate=0.75, filter_radius=3, rms_mix_rate=0.25, protect=0.33)
        rvc_instances["d10s"] = rvc_d10s
        print("[RVC Daemon] Modelo de Lionel Messi (D10S) cargado y residente en RAM.")

    # 2. Cargar Cristiano Ronaldo (CR7)
    cr7_pth = MODELS_DIR / "cr7.pth"
    cr7_index = MODELS_DIR / "cr7.index"
    if cr7_pth.is_file():
        rvc_cr7 = RVCInference(device=device)
        rvc_cr7.load_model(str(cr7_pth), version="v2", index_path=str(cr7_index) if cr7_index.is_file() else "")
        rvc_cr7.set_params(f0method=f0method, index_rate=0.75, filter_radius=3, rms_mix_rate=0.25, protect=0.33)
        rvc_instances["cr7"] = rvc_cr7
        print("[RVC Daemon] Modelo de Cristiano Ronaldo (CR7) cargado y residente en RAM.")

class ConvertRequest(BaseModel):
    input_path: str
    output_path: str
    persona: str = "d10s"

@app.get("/health")
def health():
    return {
        "status": "online",
        "models_loaded": list(rvc_instances.keys()),
        "cuda": torch.cuda.is_available()
    }

@app.post("/convert")
def convert_audio(req: ConvertRequest):
    persona_key = req.persona.lower()
    rvc = rvc_instances.get(persona_key)
    if not rvc:
        raise HTTPException(status_code=400, detail=f"Modelo no disponible para {req.persona}")

    if not os.path.isfile(req.input_path):
        raise HTTPException(status_code=404, detail=f"Audio de entrada no existe: {req.input_path}")

    try:
        rvc.infer_file(req.input_path, req.output_path)
        if not os.path.isfile(req.output_path):
            raise HTTPException(status_code=500, detail="Inferencia no produjo archivo de salida")
        return {"status": "success", "output_path": req.output_path}
    except Exception as e:
        print(f"[RVC Daemon Error] {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")
