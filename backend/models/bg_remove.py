# backend/models/bg_remove.py
from typing import Optional
from PIL import Image
import io
import importlib
import importlib.util

def remove_background(image: Image.Image) -> Optional[Image.Image]:
    """
    Remove background using rembg if available.
    Returns an RGBA PIL image. On failure returns the original image converted to RGBA.
    """
    try:
        # Lazy import to avoid static import-time errors if rembg isn't installed.
        if importlib.util.find_spec("rembg") is None:
            return image.convert("RGBA")
        rembg = importlib.import_module("rembg")
        remove = getattr(rembg, "remove", None)
        if remove is None:
            return image.convert("RGBA")
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        out = remove(buf.getvalue())
        return Image.open(io.BytesIO(out)).convert("RGBA")
    except Exception:
        # graceful fallback: return RGBA-converted original
        try:
            return image.convert("RGBA")
        except Exception:
            return None
