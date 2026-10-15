from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field
from app.services.tts_service import tts_service, CACHE_DIR, MODELS_DIR

router = APIRouter(prefix="/api/tts", tags=["Síntesis de Voz Neuronal"])

class SynthesizeRequest(BaseModel):
    text: str = Field(..., description="Texto a sintetizar en audio", example="¡Siuuu! Comandante listo para ganar.")
    persona: str = Field("d10s", description="Personalidad de voz: 'd10s' o 'cr7'", example="cr7")

@router.post("/synthesize")
async def synthesize_speech(payload: SynthesizeRequest):
    """
    Sintetiza la voz del Core seleccionado (D10S o CR7) mediante RVC v2
    para el texto exacto solicitado por el usuario o generado por el modelo.
    """
    persona_key = "d10s" if payload.persona.lower() == "d10s" else "cr7"
    raw_text = payload.text if payload.text and payload.text.strip() else "¡Listo para ganar!"

    audio_bytes = await tts_service.synthesize(raw_text, persona_key)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="No se pudo generar el audio para el texto especificado.")

    media_type = "audio/wav" if audio_bytes.startswith(b"RIFF") else "audio/mpeg"
    return Response(content=audio_bytes, media_type=media_type)

@router.get("/status")
def get_tts_status():
    """Consulta el estado del motor TTS RVC v2 y estadísticas de la caché en disco."""
    cache_files = list(CACHE_DIR.glob("*.wav")) + list(CACHE_DIR.glob("*.mp3"))
    total_size_kb = sum(f.stat().st_size for f in cache_files) / 1024

    messi_model_ok = (MODELS_DIR / "messi.pth").is_file()
    cr7_model_ok = (MODELS_DIR / "cr7.pth").is_file()

    return {
        "status": "online",
        "engine": "In-Memory Daemon RVC v2 (Retrieval-based Voice Conversion) + Neural Baseline",
        "rvc_models": {
            "d10s": "Lionel Messi (messi.pth)" if messi_model_ok else "missing",
            "cr7": "Cristiano Ronaldo (cr7.pth)" if cr7_model_ok else "missing"
        },
        "cached_audios_count": len(cache_files),
        "cache_disk_size_kb": round(total_size_kb, 2)
    }
