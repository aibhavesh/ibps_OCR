import io
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="IBPS Tesseract OCR API")

def process_cv_image(img_cv):
    """Applies Grayscale and Otsu binarization for clean OCR extraction."""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(thresh).strip()

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    
    try:
        # Handle PDF Documents
        if file.filename.lower().endswith(".pdf"):
            pdf_images = convert_from_bytes(contents)
            full_text = []
            for i, page_img in enumerate(pdf_images):
                img_cv = cv2.cvtColor(np.array(page_img), cv2.COLOR_RGB2BGR)
                page_text = process_cv_image(img_cv)
                full_text.append(f"--- Page {i+1} ---\n{page_text}")
            return {"filename": file.filename, "text": "\n\n".join(full_text)}
            
        # Handle Image Documents (PNG, JPG, JPEG)
        else:
            img_pil = Image.open(io.BytesIO(contents))
            # Convert PIL to OpenCV format
            img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            text = process_cv_image(img_cv)
            return {"filename": file.filename, "text": text}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Processing Error: {str(e)}")

@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "ocr_api"}