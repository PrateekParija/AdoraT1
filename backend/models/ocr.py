# backend/models/ocr.py
from typing import List
from PIL import Image
import pytesseract

def extract_text(image: Image.Image) -> List[str]:
    """Simple OCR wrapper returning lines of text (non-empty)."""
    try:
        text = pytesseract.image_to_string(image)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        return lines
    except Exception:
        return []
