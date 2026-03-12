"""Document parsing service for extracting text and tables from files."""
import os
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str, max_pages: int = None) -> Dict[str, Any]:
    """Extract text and tables from a PDF file."""
    result = {"text": "", "tables": [], "pages": 0}
    
    try:
        import pdfplumber
        
        with pdfplumber.open(file_path) as pdf:
            result["pages"] = len(pdf.pages)
            pages_to_read = pdf.pages if max_pages is None else pdf.pages[:max_pages]
            
            all_text = []
            all_tables = []
            
            for page in pages_to_read:
                # Extract text
                page_text = page.extract_text()
                if page_text:
                    all_text.append(page_text)
                
                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        all_tables.append(table)
            
            result["text"] = "\n\n".join(all_text)
            result["tables"] = all_tables
    
    except ImportError:
        logger.warning("pdfplumber not available")
    except Exception as e:
        logger.error(f"PDF parsing failed for {file_path}: {e}")
    
    return result


def parse_excel(file_path: str) -> Dict[str, Any]:
    """Extract data from Excel files."""
    result = {"text": "", "sheets": {}, "sheet_names": []}
    
    try:
        import pandas as pd
        
        xl = pd.ExcelFile(file_path)
        result["sheet_names"] = xl.sheet_names
        
        text_parts = []
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=100)
            result["sheets"][sheet_name] = df.to_dict(orient="records")
            
            # Convert to text representation
            text_parts.append(f"Sheet: {sheet_name}")
            text_parts.append(df.to_string())
        
        result["text"] = "\n\n".join(text_parts)
    
    except ImportError:
        logger.warning("pandas not available")
    except Exception as e:
        logger.error(f"Excel parsing failed for {file_path}: {e}")
    
    return result


def parse_image(file_path: str) -> Dict[str, Any]:
    """Extract text from an image file using OCR."""
    from app.utils.ocr import extract_text_from_image
    
    text = extract_text_from_image(file_path)
    return {"text": text, "type": "image"}


def parse_document(file_path: str, file_type: str, max_pages: int = None) -> Dict[str, Any]:
    """Parse a document based on its file type."""
    file_type = file_type.lower()
    
    if file_type == "pdf":
        return parse_pdf(file_path, max_pages=max_pages)
    elif file_type in ["xlsx", "xls", "excel"]:
        return parse_excel(file_path)
    elif file_type in ["png", "jpg", "jpeg", "image"]:
        return parse_image(file_path)
    else:
        logger.warning(f"Unknown file type: {file_type}")
        return {"text": "", "error": f"Unsupported file type: {file_type}"}


def get_document_preview_text(file_path: str, file_type: str) -> str:
    """Get a preview of the document text for classification."""
    result = parse_document(file_path, file_type, max_pages=2)
    
    text = result.get("text", "")
    
    # For Excel, add sheet name info
    if "sheet_names" in result:
        sheet_info = f"Sheet names: {', '.join(result['sheet_names'])}\n\n"
        text = sheet_info + text
    
    # Truncate for API calls
    if len(text) > 8000:
        text = text[:8000] + "...[truncated]"
    
    return text
