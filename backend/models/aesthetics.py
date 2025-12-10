# backend/models/aesthetics.py
from ..schemas import CreativeCanvas

def aesthetic_score(canvas: CreativeCanvas) -> float:
    """
    Very simple heuristic aesthetic scorer stub.
    Replace with a CNN/MobileNet-based scorer later.
    Returns a float in [0, 1].
    """
    score = 0.5
    try:
        num_text = len(canvas.text_blocks) if canvas.text_blocks else 0
        score += max(0, 0.3 - 0.05 * num_text)
        if getattr(canvas, "packshot_ids", None) and len(canvas.packshot_ids) == 1:
            score += 0.1
    except Exception:
        # be defensive — never crash the pipeline for scoring
        pass
    return max(0.0, min(1.0, score))
