# backend/rules/engine.py
from typing import List
from ..schemas import CreativeCanvas, ValidationIssue, ValidationResult
from .presets import DEFAULT_CONFIGS


def _check_safe_zone(canvas: CreativeCanvas, cfg) -> List[ValidationIssue]:
    """
    Ensure text is not inside the top safe zone.
    """
    issues: List[ValidationIssue] = []
    top_zone = cfg.top_safe_zone_px
    for tb in canvas.text_blocks or []:
        if tb.y < top_zone:
            issues.append(
                ValidationIssue(
                    code="SAFE_ZONE_TOP",
                    message=f"Text '{tb.text[:15]}...' is in top safe zone (<{top_zone}px).",
                    severity="error",
                )
            )
    return issues


def _check_font_sizes(canvas: CreativeCanvas, cfg) -> List[ValidationIssue]:
    """
    Enforce minimum readable font size in pixels.
    """
    issues: List[ValidationIssue] = []
    min_font = cfg.min_font_px
    for tb in canvas.text_blocks or []:
        if tb.font_size < min_font:
            issues.append(
                ValidationIssue(
                    code="FONT_TOO_SMALL",
                    message=f"Text '{tb.text[:15]}...' font {tb.font_size}px < {min_font}px.",
                    severity="error",
                )
            )
    return issues


def _check_packshot_count(canvas: CreativeCanvas, cfg) -> List[ValidationIssue]:
    """
    Limit the number of packshots for a given format.
    """
    issues: List[ValidationIssue] = []
    max_ps = cfg.max_packshots
    num_ps = len(canvas.packshot_ids or [])
    if num_ps > max_ps:
        issues.append(
            ValidationIssue(
                code="TOO_MANY_PACKSHOTS",
                message=f"{num_ps} packshots > allowed {max_ps}.",
                severity="error",
            )
        )
    return issues


def run_rules(canvas: CreativeCanvas) -> ValidationResult:
    """
    Run all rule checks for a given canvas using the correct preset.
    Returns a ValidationResult with aggregated issues and 'passed' flag.
    """
    cfg = DEFAULT_CONFIGS.get(canvas.format, DEFAULT_CONFIGS["story"])

    issues: List[ValidationIssue] = []
    issues.extend(_check_safe_zone(canvas, cfg))
    issues.extend(_check_font_sizes(canvas, cfg))
    issues.extend(_check_packshot_count(canvas, cfg))

    passed = not any(i.severity == "error" for i in issues)
    return ValidationResult(canvas_id=canvas.id, issues=issues, passed=passed)
