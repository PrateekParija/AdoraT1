# backend/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class TextBlock(BaseModel):
    id: str
    text: str
    font_size: int = 20
    color: str = "#000000"
    x: int = 0
    y: int = 0


class CreativeCanvas(BaseModel):
    id: str
    user_id: Optional[str]
    format: str = "story"
    width: int
    height: int
    background_image_id: Optional[str] = None
    packshot_ids: Optional[List[str]] = []
    text_blocks: Optional[List[TextBlock]] = []
    extra: Optional[dict] = Field(default_factory=dict)


class UploadedImage(BaseModel):
    image_id: str
    path: str
    width: Optional[int]
    height: Optional[int]
    mime_type: Optional[str]


class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: str  # "error" or "warning"


class ValidationResult(BaseModel):
    canvas_id: str
    issues: List[ValidationIssue] = []
    passed: bool = False


class AutoFixRequest(BaseModel):
    canvas: CreativeCanvas


class AutoFixResponse(BaseModel):
    canvas: CreativeCanvas
    validation: ValidationResult
    applied_fixes: List[str] = []


class RenderRequest(BaseModel):
    canvas: CreativeCanvas
    formats: Optional[List[str]] = None


class RenderItem(BaseModel):
    format: str
    path: str
    size_bytes: int


class RenderResponse(BaseModel):
    canvas_id: str
    creatives: List[RenderItem]
    audit_log_path: str
