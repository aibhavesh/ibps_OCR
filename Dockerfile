FROM python:3.11-slim

# Prevent Python from writing pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required system dependencies: Tesseract, language packs, and Poppler (for PDFs)
# Added hin and mar language packs as per your IBPS spec
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    tesseract-ocr-mar \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main.py .

# Expose a default port (Render will override this via $PORT, Hugging Face uses 7860)
ENV PORT=8000
EXPOSE $PORT

# Start the FastAPI server using the dynamically assigned port
CMD uvicorn main:app --host 0.0.0.0 --port $PORT