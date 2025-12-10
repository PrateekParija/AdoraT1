python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install --upgrade pip



pip install -r requirements.txt
pip install "optimum[onnxruntime]" onnxruntime onnx diffusers transformers accelerate


Export and quantize the ONNX model (one-time):
python backend/tools/export_to_onnx.py --model_id runwayml/stable-diffusion-v1-5 --out_dir ./onnx-sd --quantize
# set ONNX_MODEL_PATH=./onnx-sd in your .env


Start backend:
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

Start frontend:
streamlit run frontend/app.py
