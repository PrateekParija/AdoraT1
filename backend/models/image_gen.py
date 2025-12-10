# backend/models/image_gen.py
import os
import io
import importlib
import importlib.util
from typing import Optional, Tuple
from PIL import Image
import requests
import base64

ONNX_MODEL_PATH = os.getenv("ONNX_MODEL_PATH", "")
FASTSD_CLI_URL = os.getenv("FASTSD_CLI_URL", "")
DEFAULT_SIZE = (768, 512)

def _use_optimum_onnx(prompt: str, size: Tuple[int,int]) -> Optional[Image.Image]:
    if not ONNX_MODEL_PATH:
        return None
    if importlib.util.find_spec("optimum.onnxruntime") is None:
        return None
    try:
        from optimum.onnxruntime import ORTStableDiffusionPipeline
        pipe = ORTStableDiffusionPipeline.from_pretrained(
            ONNX_MODEL_PATH, provider="CPUExecutionProvider"
        )
        out = pipe(prompt, num_inference_steps=22, guidance_scale=7.5)
        img = out.images[0]
        if img.size != size:
            img = img.resize(size, Image.LANCZOS)
        return img.convert("RGBA")
    except Exception:
        return None


def _use_fastsd_service(prompt: str, size: Tuple[int,int]) -> Optional[Image.Image]:
    if not FASTSD_CLI_URL:
        return None
    try:
        payload = {"prompt": prompt, "width": size[0], "height": size[1]}
        r = requests.post(FASTSD_CLI_URL, json=payload, timeout=180)

        if not r.ok:
            return None

        if "json" in r.headers.get("content-type", ""):
            data = r.json()
            img_b64 = data.get("image") or data.get("image_base64")
            if img_b64:
                raw = base64.b64decode(img_b64)
                img = Image.open(io.BytesIO(raw)).convert("RGBA")
                if img.size != size:
                    img = img.resize(size, Image.LANCZOS)
                return img
            return None

        img = Image.open(io.BytesIO(r.content)).convert("RGBA")
        if img.size != size:
            img = img.resize(size, Image.LANCZOS)
        return img
    except Exception:
        return None


def generate_image(prompt: str, size: Tuple[int,int]=DEFAULT_SIZE) -> Optional[Image.Image]:
    img = _use_optimum_onnx(prompt, size)
    if img is not None:
        return img

    img = _use_fastsd_service(prompt, size)
    if img is not None:
        return img

    return None
