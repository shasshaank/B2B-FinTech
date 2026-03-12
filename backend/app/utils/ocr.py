"""OCR utilities for image text extraction."""
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image file using pytesseract."""
    try:
        from PIL import Image
        import pytesseract
        
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except ImportError:
        logger.warning("pytesseract or Pillow not available, returning empty text")
        return ""
    except Exception as e:
        logger.error(f"OCR failed for {image_path}: {e}")
        return ""


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """Extract text from image bytes using pytesseract."""
    try:
        from PIL import Image
        import pytesseract
        
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        return text.strip()
    except ImportError:
        logger.warning("pytesseract or Pillow not available")
        return ""
    except Exception as e:
        logger.error(f"OCR from bytes failed: {e}")
        return ""
