from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.services.ctc_service import audio_ctc_service

router = APIRouter(prefix="/api/audio", tags=["🎙️ Reconocimiento Acústico del Habla (ASR con CTC Loss)"])

class AudioBase64Request(BaseModel):
    audio_b64: str = Field(..., description="Audio codificado en Base64 (WAV 16 kHz)")

@router.get("/health", summary="Estado del servicio acústico CTC")
def audio_health():
    return {
        "status": "online",
        "service": "Audio-ASR-CTC-DeepSpeech2",
        "vocabulary_length": len(audio_ctc_service.vocab),
        "tf_native_loaded": audio_ctc_service._tf_available
    }

@router.get("/ctc-info", summary="Métricas de evaluación, arquitectura y corpus de audio")
def audio_ctc_info():
    return audio_ctc_service.get_ctc_benchmark_info()

@router.post("/transcribe-ctc", summary="Transcribe un archivo de audio WAV mediante el modelo acústico CTC")
async def transcribe_wav_file(
    file: UploadFile = File(..., description="Archivo de audio WAV mono a 16 kHz")
):
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo de audio está vacío."
            )
        result = audio_ctc_service.transcribe_audio(content)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el procesamiento acústico CTC: {str(e)}"
        )

@router.post("/transcribe-base64", summary="Transcribe audio transmitido en Base64 desde el navegador")
def transcribe_base64_endpoint(payload: AudioBase64Request):
    try:
        result = audio_ctc_service.transcribe_base64(payload.audio_b64)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al decodificar audio Base64: {str(e)}"
        )
