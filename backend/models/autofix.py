# backend/models/autofix.py
from typing import List, Tuple
from copy import deepcopy
from ..schemas import CreativeCanvas, ValidationResult
from ..rules.engine import run_rules
from .aesthetics import aesthetic_score

def _neighbour_canvases(canvas: CreativeCanvas) -> List[CreativeCanvas]:
    """Generate simple neighbouring layouts by nudging text blocks down
    and increasing font size a bit. This is a basic hill-climb neighbourhood.
    """
    neighbours: List[CreativeCanvas] = []
    for tb in canvas.text_blocks or []:
        for dy in (20, 40):
            c2 = deepcopy(canvas)
            for tb2 in c2.text_blocks:
                if tb2.id == tb.id:
                    tb2.y += dy
            neighbours.append(c2)
        for dfont in (2, 4):
            c2 = deepcopy(canvas)
            for tb2 in c2.text_blocks:
                if tb2.id == tb.id:
                    tb2.font_size += dfont
            neighbours.append(c2)
    return neighbours

def hill_climb_autofix(
    canvas: CreativeCanvas, max_iters: int = 20
) -> Tuple[CreativeCanvas, ValidationResult, List[str]]:
    """
    Run a simple hill-climb to try to satisfy rules and improve aesthetics.
    Returns: (best_canvas, validation_result, list_of_fix_descriptions)
    """
    current = deepcopy(canvas)
    current_val = run_rules(current)
    current_score = aesthetic_score(current) if current_val.passed else 0.0
    fixes: List[str] = []

    for _ in range(max_iters):
        neighbours = _neighbour_canvases(current)
        best_candidate = current
        best_val = current_val
        best_score = current_score
        best_fix_desc = None

        for nc in neighbours:
            val = run_rules(nc)
            score = aesthetic_score(nc) if val.passed else 0.0
            if val.passed and score > best_score:
                best_candidate = nc
                best_val = val
                best_score = score
                best_fix_desc = "Adjusted text positions/font for better compliance & aesthetics"

        if best_candidate is current:
            break  # no improvement

        current = best_candidate
        current_val = best_val
        current_score = best_score
        if best_fix_desc:
            fixes.append(best_fix_desc)

    return current, current_val, fixes
