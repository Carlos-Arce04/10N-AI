"""
Puente de inferencia RVC v2 ejecutado bajo el runtime de Python 3.10.
Convierte el audio base con las características vocales reales de Lionel Messi (D10S)
o Cristiano Ronaldo (CR7).
"""

import os
import sys
import argparse
import time
import torch

# Compatibilidad segura para PyTorch 2.6+ con checkpoints de RVC
_orig_torch_load = torch.load
def _safe_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = _safe_torch_load

from rvc_python.infer import RVCInference

def convert_voice(input_path: str, output_path: str, persona: str, models_dir: str):
    persona = persona.lower()
    model_name = "messi" if persona == "d10s" else "cr7"
    pth_file = os.path.join(models_dir, f"{model_name}.pth")
    index_file = os.path.join(models_dir, f"{model_name}.index")

    if not os.path.isfile(pth_file):
        raise FileNotFoundError(f"No se encontró el modelo RVC: {pth_file}")

    use_cuda = torch.cuda.is_available()
    device = "cuda:0" if use_cuda else "cpu:0"
    
    t0 = time.time()
    rvc = RVCInference(device=device)
    rvc.load_model(pth_file, version="v2", index_path=index_file if os.path.isfile(index_file) else "")

    # 'rmvpe' con GPU o 'pm' para máxima velocidad en CPU
    f0method = "rmvpe" if use_cuda else "pm"
    f0up_key = 0

    rvc.set_params(
        f0method=f0method,
        f0up_key=f0up_key,
        index_rate=0.75,
        filter_radius=3,
        rms_mix_rate=0.25,
        protect=0.33
    )

    t1 = time.time()
    rvc.infer_file(input_path, output_path)
    total_time = round(time.time() - t0, 2)
    print(f"[RVC] Inferencia completada para {persona} en {total_time}s ({f0method} en {device}) -> {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RVC Inference CLI Worker")
    parser.add_argument("--input", required=True, help="Ruta del audio de entrada (.wav)")
    parser.add_argument("--output", required=True, help="Ruta del audio de salida (.wav)")
    parser.add_argument("--persona", default="d10s", help="Personaje: d10s o cr7")
    parser.add_argument("--models-dir", required=True, help="Directorio con los archivos .pth y .index")
    args = parser.parse_args()

    try:
        convert_voice(args.input, args.output, args.persona, args.models_dir)
        sys.exit(0)
    except Exception as e:
        print(f"[RVC ERROR] Error en inferencia: {e}", file=sys.stderr)
        sys.exit(1)
