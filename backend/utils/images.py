# backend/utils/images.py
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import io
import math

from ..config import MAX_FILE_SIZE_BYTES, UPLOAD_DIR


def load_image(path: Path) -> Image.Image:
    """
    Load an image file and convert to RGBA (suitable for compositing).
    """
    return Image.open(path).convert("RGBA")


def resize_to_fit(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
    """
    Resize using high-quality Lanczos resampling.
    """
    return img.resize(size, Image.LANCZOS)


def find_uploaded_file(file_id: str, base_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Try to find an uploaded file in UPLOAD_DIR with the given id (without ext).
    Looks for common extensions (.png, .jpg, .jpeg, .webp).
    Returns Path or None.
    """
    base_dir = base_dir or Path(UPLOAD_DIR)
    if not file_id:
        return None

    candidates = [
        f"{file_id}.png",
        f"{file_id}.jpg",
        f"{file_id}.jpeg",
        f"{file_id}.webp",
    ]
    for fn in candidates:
        p = base_dir / fn
        if p.exists():
            return p

    # Fallback: any file that starts with file_id
    for p in base_dir.glob(f"{file_id}*"):
        if p.is_file():
            return p

    return None


def save_with_size_limit(
    img: Image.Image,
    dest: Path,
    max_bytes: int = MAX_FILE_SIZE_BYTES,
) -> int:
    """
    Save image to dest trying to keep file size <= max_bytes.

    Strategy:
      1. If dest is JPEG, try reducing quality from 95 down to 30.
      2. If still too large, downscale by 10% increments and retry.
      3. For PNG, try PNG once, then convert to JPEG and apply same logic.
      4. If all else fails, save the last attempt even if still too large.

    Returns the final size in bytes.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    fmt = "JPEG" if dest.suffix.lower() in [".jpg", ".jpeg"] else "PNG"

    # local image copy so we don't mutate caller's object
    attempt_img = img.copy()
    quality = 95

    while True:
        buf = io.BytesIO()

        if fmt == "JPEG":
            attempt_img.convert("RGB").save(
                buf,
                format="JPEG",
                quality=quality,
                optimize=True,
            )
        else:
            # PNG attempt
            attempt_img.save(buf, format="PNG", optimize=True)

        size = buf.tell()

        # success or we've hit our limits
        if size <= max_bytes or (fmt == "JPEG" and quality <= 30):
            with open(dest, "wb") as f:
                f.write(buf.getvalue())
            return size

        # If we are on JPEG and can still reduce quality, do so
        if fmt == "JPEG" and quality > 30:
            quality -= 10
            continue

        # If still too big and we were PNG, switch to JPEG and try again
        if fmt != "JPEG":
            fmt = "JPEG"
            quality = 90
            continue

        # Last resort: downscale the image by 10% and try again
        w, h = attempt_img.size
        new_w = max(1, math.floor(w * 0.9))
        new_h = max(1, math.floor(h * 0.9))
        if (new_w, new_h) == (w, h):
            # We can't shrink further; save what we have and exit.
            with open(dest, "wb") as f:
                f.write(buf.getvalue())
            return size
        attempt_img = attempt_img.resize((new_w, new_h), Image.LANCZOS)
