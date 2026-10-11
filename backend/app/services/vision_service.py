import os
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Rutas de los modelos locales de visión (OpenCV DNN + Haar Cascade)
VISION_MODELS_DIR = Path(__file__).resolve().parent.parent / "models_vision"
HAAR_CASCADE_PATH = VISION_MODELS_DIR / "haarcascade_frontalface_default.xml"
EMOTION_MODEL_PATH = VISION_MODELS_DIR / "emotion-ferplus-8.onnx"

# Mapeo de clases del modelo FER+ (8 emociones)
EMOTION_CLASSES = [
    "neutral",      # 0
    "happiness",    # 1
    "surprise",     # 2
    "sadness",      # 3
    "anger",        # 4
    "disgust",      # 5
    "fear",         # 6
    "contempt"      # 7
]

EMOTION_DISPLAY_NAMES = {
    "neutral": "Neutral / Tranquilo",
    "happiness": "Alegría / Felicidad",
    "surprise": "Sorpresa",
    "sadness": "Tristeza",
    "anger": "Enojo / Ira",
    "disgust": "Disgusto / Desagrado",
    "fear": "Miedo / Temor",
    "contempt": "Desdén"
}

def score_to_likelihood(score: float) -> str:
    if score >= 0.75:
        return "VERY_LIKELY"
    elif score >= 0.50:
        return "LIKELY"
    elif score >= 0.25:
        return "POSSIBLE"
    elif score >= 0.10:
        return "UNLIKELY"
    else:
        return "VERY_UNLIKELY"

def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=-1, keepdims=True)

class VisionService:
    def __init__(self):
        self.face_cascade: Optional[cv2.CascadeClassifier] = None
        self.emotion_net: Optional[cv2.dnn.Net] = None
        self._init_models()

    def _init_models(self):
        try:
            if HAAR_CASCADE_PATH.exists():
                self.face_cascade = cv2.CascadeClassifier(str(HAAR_CASCADE_PATH))
                logger.info("Detector de rostros Haar Cascade cargado con éxito.")
            else:
                logger.warning(f"No se encontró Haar Cascade en {HAAR_CASCADE_PATH}")

            if EMOTION_MODEL_PATH.exists():
                self.emotion_net = cv2.dnn.readNetFromONNX(str(EMOTION_MODEL_PATH))
                logger.info("Modelo de Emociones FER+ cargado en OpenCV DNN con éxito.")
            else:
                logger.warning(f"No se encontró el modelo de emociones en {EMOTION_MODEL_PATH}")

        except Exception as e:
            logger.error(f"Error inicializando modelos locales de visión: {e}")

    def analyze_face(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analiza un fotograma de imagen de forma 100% local con OpenCV DNN y Haar Cascade.
        Detecta el rostro, recorta y preprocesa a 64x64, y clasifica las emociones en tiempo real.
        """
        if not self.face_cascade or not self.emotion_net:
            return {
                "success": False,
                "error": "Los modelos locales de visión (Haar / Emotion ONNX) no están disponibles.",
                "detected": False
            }

        try:
            # Decodificar imagen desde bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return {
                    "success": False,
                    "error": "No se pudo decodificar el formato de la imagen proporcionada.",
                    "detected": False
                }

            # Convertir a escala de grises para detección de rostros
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(60, 60)
            )

            if len(faces) == 0:
                return {
                    "success": True,
                    "detected": False,
                    "message": "No se detectó ningún rostro en el fotograma.",
                    "dominant_emotion": "Desconocido",
                    "confidence": 0.0,
                    "total_faces": 0,
                    "faces": []
                }

            # Tomar el rostro principal (el más grande por área)
            primary_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = primary_face

            # Recortar rostro y preprocesar para el modelo FER+ (requiere 1x1x64x64 float32)
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (64, 64), interpolation=cv2.INTER_AREA)
            face_blob = face_resized.astype(np.float32)
            face_blob = np.expand_dims(face_blob, axis=(0, 1))  # Forma: (1, 1, 64, 64)

            # Inferencia con OpenCV DNN
            self.emotion_net.setInput(face_blob)
            raw_scores = self.emotion_net.forward()
            probs = softmax(raw_scores[0])

            # Mapear probabilidades a las 8 emociones
            scores_dict = {
                EMOTION_CLASSES[i]: float(probs[i])
                for i in range(len(EMOTION_CLASSES))
            }

            # Identificar emoción dominante
            best_emotion_key = max(scores_dict, key=scores_dict.get)
            best_confidence = scores_dict[best_emotion_key]
            dominant_display = EMOTION_DISPLAY_NAMES.get(best_emotion_key, best_emotion_key.capitalize())

            # Bounding box en formato de 4 vértices para el HUD futurista
            bounding_box = [
                {"x": int(x), "y": int(y)},
                {"x": int(x + w), "y": int(y)},
                {"x": int(x + w), "y": int(y + h)},
                {"x": int(x), "y": int(y + h)}
            ]

            return {
                "success": True,
                "detected": True,
                "dominant_emotion": dominant_display,
                "detection_confidence": round(best_confidence, 4),
                "emotions": {
                    "joy": {
                        "likelihood": score_to_likelihood(scores_dict.get("happiness", 0.0)),
                        "score": round(scores_dict.get("happiness", 0.0), 4)
                    },
                    "sorrow": {
                        "likelihood": score_to_likelihood(scores_dict.get("sadness", 0.0)),
                        "score": round(scores_dict.get("sadness", 0.0), 4)
                    },
                    "anger": {
                        "likelihood": score_to_likelihood(scores_dict.get("anger", 0.0)),
                        "score": round(scores_dict.get("anger", 0.0), 4)
                    },
                    "surprise": {
                        "likelihood": score_to_likelihood(scores_dict.get("surprise", 0.0)),
                        "score": round(scores_dict.get("surprise", 0.0), 4)
                    },
                    "neutral": {
                        "likelihood": score_to_likelihood(scores_dict.get("neutral", 0.0)),
                        "score": round(scores_dict.get("neutral", 0.0), 4)
                    },
                    "fear": {
                        "likelihood": score_to_likelihood(scores_dict.get("fear", 0.0)),
                        "score": round(scores_dict.get("fear", 0.0), 4)
                    },
                    "disgust": {
                        "likelihood": score_to_likelihood(scores_dict.get("disgust", 0.0)),
                        "score": round(scores_dict.get("disgust", 0.0), 4)
                    }
                },
                "bounding_box": bounding_box,
                "face_rect": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
                "total_faces": len(faces),
                "engine": "Local OpenCV DNN (FER+ ONNX CNN Model)"
            }

        except Exception as e:
            logger.error(f"Error procesando imagen en VisionService local: {e}")
            return {
                "success": False,
                "error": str(e),
                "detected": False
            }

# Instancia singleton del servicio
vision_service = VisionService()
