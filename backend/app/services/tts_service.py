import re
import hashlib
import logging
import asyncio
import os
import sys
import uuid
import shutil
import traceback
import json
import urllib.request
from pathlib import Path
import edge_tts

logger = logging.getLogger("10N-AI-TTS")

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parents[3]
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "audio_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MODELS_DIR = BASE_DIR / "models" / "rvc"
RVC_DAEMON_URL = "http://127.0.0.1:8005/convert"

class TTSService:
    def _clean_text_for_speech(self, text: str) -> str:
        """
        Limpia markdown, enlaces y signos para una lectura fluida y natural.
        Permite sintetizar la respuesta completa configurada por el asistente.
        """
        if not text:
            return ""
        t = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        t = re.sub(r'[\*_`#]', '', t)
        t = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', t)
        t = re.sub(r'\$([0-9,\.]+)', r'\1 dólares', t)
        t = re.sub(r'\s+', ' ', t).strip()

        # Si el texto es excesivamente largo (+600 caracteres), acotar al final de una oración
        if len(t) > 600:
            sentences = re.findall(r'[^.!?]+[.!?]+', t)
            accumulated = ""
            for s in sentences:
                if len(accumulated) + len(s) > 550:
                    break
                accumulated += " " + s
            if accumulated.strip():
                t = accumulated.strip()
            else:
                t = t[:550].rsplit(' ', 1)[0] + '...'

        return t

    def _get_cache_path(self, persona: str, text: str) -> Path:
        """Genera una ruta única en disco basada en el hash del texto y el personaje."""
        clean = self._clean_text_for_speech(text)
        key_str = f"{persona.lower()}_{clean}"
        h = hashlib.sha256(key_str.encode("utf-8")).hexdigest()[:24]
        return CACHE_DIR / f"{persona.lower()}_{h}.wav"

    async def synthesize(self, text: str, persona: str = "d10s") -> bytes:
        """
        Sintetiza audio con el timbre real de Messi (D10S) o Cristiano Ronaldo (CR7):
        1. Comprueba si el audio ya está generado y cacheado en disco (0ms, offline).
        2. Genera la voz base neural con Edge-TTS para el texto exacto.
        3. Convierte el timbre al instante mediante el microservicio daemon RVC en RAM.
        4. Guarda el audio final en audio_cache/ para reutilización instantánea.
        """
        clean_text = self._clean_text_for_speech(text)
        if not clean_text:
            clean_text = "¡Listo, predicción completada!"

        persona_key = "d10s" if persona.lower() == "d10s" else "cr7"
        cache_path = self._get_cache_path(persona_key, clean_text)

        # 1. Recuperación instantánea de caché local en disco (0.00 segundos)
        # Un audio real de RVC pesa > 150 KB (PCM 44.1kHz). Archivos menores son audios base no convertidos.
        if cache_path.exists() and cache_path.stat().st_size > 150000:
            try:
                logger.info(f"Audio servido desde caché local RVC: {cache_path.name} ({round(cache_path.stat().st_size / 1024, 1)} KB)")
                return cache_path.read_bytes()
            except Exception as e:
                logger.warning(f"Error leyendo archivo de cache existente: {e}")

        # Archivos temporales con UUID único
        unique_id = uuid.uuid4().hex[:10]
        temp_base_wav = CACHE_DIR / f"temp_base_{persona_key}_{unique_id}.wav"
        temp_rvc_out = CACHE_DIR / f"temp_rvc_{persona_key}_{unique_id}.wav"

        try:
            # 2. Generación rápida de audio base con el texto exacto
            if persona_key == "d10s":
                voice = "es-AR-TomasNeural"
                rate = "+3%"
                pitch = "-1Hz"
            else:
                voice = "es-ES-AlvaroNeural"
                rate = "+12%"
                pitch = "+3Hz"

            communicate = edge_tts.Communicate(clean_text, voice=voice, rate=rate, pitch=pitch)
            await communicate.save(str(temp_base_wav))

            # 3. Conversión de voz RVC (Vía Daemon en RAM o Direct Worker)
            rvc_success = False
            if temp_base_wav.exists() and temp_base_wav.stat().st_size > 500:
                # Intento A: Microservicio Daemon en RAM (puerto 8005, ~0.8s)
                try:
                    payload = json.dumps({
                        "input_path": str(temp_base_wav.resolve()),
                        "output_path": str(temp_rvc_out.resolve()),
                        "persona": persona_key
                    }).encode("utf-8")

                    req = urllib.request.Request(
                        RVC_DAEMON_URL,
                        data=payload,
                        headers={"Content-Type": "application/json"}
                    )

                    def _call_daemon():
                        with urllib.request.urlopen(req, timeout=15) as resp:
                            return resp.status == 200

                    loop = asyncio.get_event_loop()
                    rvc_success = await loop.run_in_executor(None, _call_daemon)
                except Exception as daemon_err:
                    logger.warning(f"RVC daemon en 8005 no disponible ({daemon_err}). Probando worker directo GPU...")

                # Intento B: Si el daemon no respondió, ejecutar worker directo RVC vía Python con GPU o CPU (~5s)
                if not rvc_success:
                    candidates = [
                        os.environ.get("PYTHON_RVC_PATH", ""),
                        r"C:\Users\carlo\AppData\Local\Programs\Python\Python310\python.exe",
                        sys.executable,
                        shutil.which("python3.10") or "",
                        shutil.which("python") or ""
                    ]
                    python_exe = next((c for c in candidates if c and os.path.isfile(c)), sys.executable)
                    bridge_script = Path(__file__).resolve().parent / "rvc_bridge.py"
                    if bridge_script.is_file():
                        try:
                            cmd = [
                                python_exe,
                                str(bridge_script),
                                "--input", str(temp_base_wav.resolve()),
                                "--output", str(temp_rvc_out.resolve()),
                                "--persona", persona_key,
                                "--models-dir", str(MODELS_DIR.resolve())
                            ]
                            proc = await asyncio.create_subprocess_exec(
                                *cmd,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                cwd=str(BASE_DIR)
                            )
                            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
                            if proc.returncode == 0 and temp_rvc_out.exists() and temp_rvc_out.stat().st_size > 150000:
                                rvc_success = True
                                logger.info(f"Conversión RVC directa exitosa para {persona_key}")
                            else:
                                logger.warning(f"RVC worker directo devolvió código {proc.returncode}: {stderr.decode('utf-8', errors='ignore')}")
                        except Exception as bridge_err:
                            logger.error(f"Fallo en ejecución de worker directo RVC: {bridge_err}")

                # Si la conversión RVC fue exitosa, guardar en caché permanente y retornar
                if rvc_success and temp_rvc_out.exists() and temp_rvc_out.stat().st_size > 150000:
                    logger.info(f"Guardando audio RVC auténtico en caché: {cache_path.name}")
                    shutil.copyfile(str(temp_rvc_out), str(cache_path))
                    return cache_path.read_bytes()

            # 4. Fallback de emergencia temporal:
            # SIEMPRE entrega el audio base generado para que el usuario escuche algo,
            # pero NUNCA lo guarda en cache_path para no contaminar la caché con voces genéricas.
            if temp_base_wav.exists() and temp_base_wav.stat().st_size > 500:
                logger.warning(f"RVC no pudo procesar {persona_key}. Entregando audio base temporal (sin guardar en caché).")
                return temp_base_wav.read_bytes()

        except Exception as e:
            logger.error(f"Error generando síntesis de voz [{type(e).__name__}]: {e}\n{traceback.format_exc()}")
        finally:
            if temp_base_wav.exists():
                try:
                    temp_base_wav.unlink(missing_ok=True)
                except Exception:
                    pass
            if temp_rvc_out.exists():
                try:
                    temp_rvc_out.unlink(missing_ok=True)
                except Exception:
                    pass

        return b""

tts_service = TTSService()
