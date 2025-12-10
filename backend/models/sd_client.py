# backend/models/sd_client.py
from typing import Optional, Tuple
from PIL import Image
from .image_gen import generate_image

def generate_background(prompt: str, size: Tuple[int,int]=(1080,1920)) -> Optional[Image.Image]:
    try:
        return generate_image(prompt, size)
    except Exception:
        return None
