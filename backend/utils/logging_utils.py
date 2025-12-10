# backend/utils/logging_utils.py
import csv
import json
from pathlib import Path
from typing import List, Any, Dict

from ..config import AUDIT_LOG_DIR
from ..schemas import ValidationIssue


def _normalize_issue(i: Any) -> Dict:
    """
    Normalize a single validation issue into a plain dict.
    Accepts:
      - Pydantic models (call .dict())
      - plain dicts (return as-is)
      - objects with attributes (use getattr)
    """
    # pydantic model or other objects exposing .dict()
    if hasattr(i, "dict") and callable(getattr(i, "dict")):
        try:
            return i.dict()
        except Exception:
            pass

    # if it's already a dict
    if isinstance(i, dict):
        return i

    # fallback: attempt to extract common attributes
    try:
        return {
            "code": getattr(i, "code", getattr(i, "name", "UNKNOWN")),
            "message": getattr(i, "message", str(i)),
            "severity": getattr(i, "severity", "warning"),
        }
    except Exception:
        # last resort: string representation
        return {"code": "UNKNOWN", "message": str(i), "severity": "warning"}


def write_audit_log(
    canvas_id: str,
    issues: List[Any],
    fixes: List[str],
) -> Path:
    """
    Write audit information (issues + applied fixes) for a canvas.

    - JSON file with full structured data
    - CSV file with a flat list of issues

    Returns the path to the JSON log file.
    """
    AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)

    json_path = AUDIT_LOG_DIR / f"{canvas_id}_audit.json"
    csv_path = AUDIT_LOG_DIR / f"{canvas_id}_audit.csv"

    # Normalize all issues to plain dicts
    normalized_issues = []
    for it in issues or []:
        try:
            normalized_issues.append(_normalize_issue(it))
        except Exception:
            # be defensive: ensure we never crash audit logging
            try:
                normalized_issues.append({"code": "NORMALIZE_ERROR", "message": str(it), "severity": "warning"})
            except Exception:
                normalized_issues.append({"code": "NORMALIZE_ERROR", "message": "<unserializable>", "severity": "warning"})

    data = {
        "canvas_id": canvas_id,
        "issues": normalized_issues,
        "applied_fixes": fixes,
        "generated_at": None,
    }

    try:
        from datetime import datetime
        data["generated_at"] = datetime.utcnow().isoformat()
    except Exception:
        pass

    # JSON log
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        # Don't let audit logging break the main pipeline
        pass

    # CSV log
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["code", "message", "severity"])
            for i in normalized_issues:
                writer.writerow([i.get("code", ""), i.get("message", ""), i.get("severity", "")])
    except Exception:
        pass

    return json_path
