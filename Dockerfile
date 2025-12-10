# ==========================================
# Base image
# ==========================================
FROM python:3.10-slim

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt /app/

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . /app/

# Expose port
EXPOSE 8000

# Run backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
