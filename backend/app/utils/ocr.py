"""
OCR utility for extracting text from image files using pytesseract.
"""
import os
from typing import Optional


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image file using pytesseract OCR.
    Falls back gracefully if tesseract is not installed.
    """
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except ImportError:
        return f"[OCR not available - pytesseract/PIL not installed] File: {os.path.basename(image_path)}"
    except Exception as e:
        return f"[OCR error: {str(e)}] File: {os.path.basename(image_path)}"


def extract_text_from_pdf_image(pdf_path: str, max_pages: int = 2) -> str:
    """
    Extract text from PDF pages rendered as images (fallback for scanned PDFs).
    """
    try:
        import pytesseract
        from PIL import Image
        import pdfplumber

        texts = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages[:max_pages]):
                # First try native text extraction
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    texts.append(text)
                else:
                    # Fall back to OCR
                    img = page.to_image(resolution=200).original
                    text = pytesseract.image_to_string(img)
                    texts.append(text)
        return "\n\n".join(texts).strip()
    except Exception as e:
        return f"[PDF OCR error: {str(e)}]"
