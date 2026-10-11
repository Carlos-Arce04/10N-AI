import base64
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.vision_service import vision_service

router = APIRouter(prefix="/api/vision", tags=["Percepción Visual"])

class Base64ImageRequest(BaseModel):
    image_base64: str

@router.post("/sentiment")
async def analyze_sentiment_upload(file: UploadFile = File(...)):
    """
    Recibe un archivo de imagen (PNG, JPG, WebP) desde la cámara web y
    detecta rostros y emociones con Google Cloud Vision API.
    """
    try:
        contents = await file.read()
        resultado = vision_service.analyze_face(contents)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

@router.post("/sentiment-base64")
async def analyze_sentiment_base64(payload: Base64ImageRequest):
    """
    Recibe un fotograma en formato Base64 directo del Canvas de React.
    Ideal para comunicación en tiempo real con la webcam.
    """
    try:
        image_str = payload.image_base64
        # Limpieza de encabezado data:image/...;base64,
        if "," in image_str:
            image_str = image_str.split(",")[1]

        image_bytes = base64.b64decode(image_str)
        resultado = vision_service.analyze_face(image_bytes)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decodificando Base64: {str(e)}")
