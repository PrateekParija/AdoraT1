# backend/models/detection.py
from typing import List, Dict
from PIL import Image
import importlib
import importlib.util

def detect_person_and_objects(image: Image.Image) -> List[Dict]:
    """
    Run YOLOv8 detection if ultralytics is installed and a model can be loaded.
    Returns list of {label, conf, box}. If not available, returns empty list.
    """
    # Try to import ultralytics/YOLO lazily
    try:
        if importlib.util.find_spec("ultralytics") is None:
            return []
        ultralytics = importlib.import_module("ultralytics")
        YOLO = getattr(ultralytics, "YOLO", None)
        if YOLO is None:
            return []
        # try to create/load a light model; if local weights missing, creation may raise
        try:
            model = YOLO("yolov8n.pt")
        except Exception:
            # if local weight not present, try default ctor (may download)
            try:
                model = YOLO()
            except Exception:
                return []
        results = model(image)
        out = []
        for r in results:
            boxes = getattr(r, "boxes", []) or []
            for box in boxes:
                cls = int(getattr(box, "cls", 0))
                # r.names may be dict-like; fallback to string
                label = r.names.get(cls, str(cls)) if hasattr(r, "names") else str(cls)
                conf = float(getattr(box, "conf", 0.0))
                coords = []
                if hasattr(box, "xyxy"):
                    xyxy = box.xyxy[0]
                    try:
                        coords = xyxy.tolist()
                    except Exception:
                        coords = [0, 0, 0, 0]
                out.append({"label": label, "conf": conf, "box": coords})
        return out
    except Exception:
        return []
