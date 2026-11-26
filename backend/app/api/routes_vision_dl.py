from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.services.vision_dl_service import vision_dl_service

router = APIRouter(prefix="/api/vision", tags=["👁️ Visión por Computadora (Transfer Learning & Real-time Video)"])

class FrameClassificationRequest(BaseModel):
    frame_b64: str = Field(..., description="Imagen del frame en formato Base64 (data:image/jpeg;base64,... o raw)")
    architecture: Optional[str] = Field("mobilenet", description="Arquitectura a utilizar: 'mobilenet' o 'resnet'")

@router.get("/health", summary="Estado del servicio de visión Deep Learning")
def vision_health():
    return {
        "status": "online",
        "service": "Vision-Transfer-Learning-MobileNet-ResNet",
        "classes": vision_dl_service.class_names,
        "tf_native_loaded": vision_dl_service._tf_available
    }

@router.get("/benchmark-info", summary="Métricas formales de evaluación del entrenamiento (MobileNetV2 vs ResNet50)")
def vision_benchmark():
    return vision_dl_service.get_models_benchmark_info()

@router.post("/classify-image", summary="Clasifica una imagen subida mediante MobileNetV2 o ResNet50")
async def classify_image_endpoint(
    file: UploadFile = File(..., description="Archivo de imagen (JPEG, PNG, WebP)"),
    architecture: str = Form("mobilenet", description="Arquitectura de red: 'mobilenet' o 'resnet'")
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo enviado debe ser una imagen válida (JPEG, PNG, WebP)."
        )

    try:
        content = await file.read()
        result = vision_dl_service.classify_image(content, architecture=architecture)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la inferencia visual: {str(e)}"
        )

@router.post("/classify-frame", summary="Clasifica un frame continuo de video/webcam en tiempo real (FPS >= 5)")
def classify_frame_endpoint(payload: FrameClassificationRequest):
    try:
        result = vision_dl_service.classify_frame(payload.frame_b64, architecture=payload.architecture or "mobilenet")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al decodificar o clasificar el frame de video: {str(e)}"
        )
