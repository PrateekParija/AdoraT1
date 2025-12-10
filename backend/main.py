# backend/main.py

import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from PIL import Image, ImageDraw, ImageFont

from backend.schemas import CanvasSchema
from backend.db import save_asset_record, save_render_record
from backend.models import sd_client
from backend.utils.logging_utils import log_event
from backend.utils.images import load_image, save_image

# ------------------------------------------------------------------------------
# App Init
# ------------------------------------------------------------------------------

app = FastAPI(title="Adora Creative Engine", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
RENDER_DIR = os.path.join(DATA_DIR, "renders")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# Helper: load font safely
# ------------------------------------------------------------------------------

def load_font(size: int):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        # fallback to PIL default font
        return ImageFont.load_default()

# ------------------------------------------------------------------------------
# Endpoint: Upload Packshot
# ------------------------------------------------------------------------------

@app.post("/upload/packshot")
async def upload_packshot(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1]
    path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    save_asset_record(file_id=file_id, file_path=path, asset_type="packshot")
    log_event("upload_packshot", {"file": path})

    return {"status": "ok", "file_id": file_id, "path": path}

# ------------------------------------------------------------------------------
# Endpoint: Upload Background
# ------------------------------------------------------------------------------

@app.post("/upload/background")
async def upload_background(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1]
    path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    save_asset_record(file_id=file_id, file_path=path, asset_type="background")
    log_event("upload_background", {"file": path})

    return {"status": "ok", "file_id": file_id, "path": path}

# ------------------------------------------------------------------------------
# Helper: Compose final creative
# ------------------------------------------------------------------------------

def render_canvas_image(canvas: CanvasSchema) -> str:
    W = canvas.width
    H = canvas.height

    # 1) Create a blank base
    base = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    # 2) Background: uploaded OR AI-generated
    bg_img: Optional[Image.Image] = None

    # uploaded background takes priority
    if canvas.background_image_path:
        try:
            bg_img = load_image(canvas.background_image_path).convert("RGBA")
        except:
            bg_img = None

    # if no uploaded background, try AI
    if bg_img is None and canvas.extra and "background_prompt" in canvas.extra:
        prompt = canvas.extra["background_prompt"]
        bg_img = sd_client.generate_background(prompt, size=(W, H))

    # paste background
    if bg_img:
        bg_img = bg_img.resize((W, H), Image.LANCZOS)
        base.alpha_composite(bg_img, (0, 0))

    draw = ImageDraw.Draw(base)

    # 3) Packshots
    for p_path in canvas.packshot_paths:
        try:
            img = load_image(p_path).convert("RGBA")
            # Auto-scale packshots to fit nicely
            img = img.resize((int(W * 0.5), int(H * 0.5)), Image.LANCZOS)
            base.alpha_composite(img, (int(W * 0.25), int(H * 0.4)))
        except Exception as e:
            print("Packshot error:", e)

    # 4) Text blocks
    for block in canvas.text_blocks:
        font = load_font(block.font_size)
        draw.text(
            (block.x, block.y),
            block.text,
            fill=block.color,
            font=font,
        )

    # 5) Save output
    render_id = uuid.uuid4().hex
    out_path = os.path.join(RENDER_DIR, f"{render_id}_{canvas.format}.png")
    base.convert("RGB").save(out_path, "PNG")

    save_render_record(canvas_id=canvas.id, output_path=out_path)
    log_event("render_created", {"file": out_path})

    return out_path

# ------------------------------------------------------------------------------
# Endpoint: Render
# ------------------------------------------------------------------------------

@app.post("/render")
async def render_creative(canvas: CanvasSchema):
    try:
        path = render_canvas_image(canvas)
        return {"status": "ok", "path": path}
    except Exception as e:
        log_event("render_failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Render failed: {str(e)}")

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    import importlib.util
    
    components = {
        "optimum_onnx": bool(importlib.util.find_spec("optimum.onnxruntime")),
        "onnxruntime": bool(importlib.util.find_spec("onnxruntime")),
        "sd_client_ai": sd_client is not None,
        "uploads_dir": os.path.exists(UPLOAD_DIR),
        "renders_dir": os.path.exists(RENDER_DIR),
    }

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "components": components,
    }
