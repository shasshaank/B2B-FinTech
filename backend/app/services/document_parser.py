"""
Document parser service — extracts text and tables from PDF, Excel, and image files.
"""
import os
from typing import Dict, Any, List


def parse_pdf(file_path: str, max_pages: int = None) -> Dict[str, Any]:
    """
    Extract text and tables from a PDF file using pdfplumber.
    Returns dict with 'text' and 'tables' keys.
    """
    try:
        import pdfplumber
        texts = []
        all_tables = []

        with pdfplumber.open(file_path) as pdf:
            pages = pdf.pages if max_pages is None else pdf.pages[:max_pages]
            for page_num, page in enumerate(pages):
                # Extract text
                text = page.extract_text() or ""
                if text.strip():
                    texts.append(f"[Page {page_num + 1}]\n{text}")

                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        all_tables.append({
                            "page": page_num + 1,
                            "data": table
                        })

        return {
            "text": "\n\n".join(texts),
            "tables": all_tables,
            "pages": len(pdf.pages) if 'pdf' in dir() else 0
        }
    except Exception as e:
        # Fallback to OCR if pdfplumber fails
        from app.utils.ocr import extract_text_from_image
        return {
            "text": f"[PDF parse error: {str(e)}]\nFile: {os.path.basename(file_path)}",
            "tables": [],
            "pages": 0
        }


def parse_excel(file_path: str) -> Dict[str, Any]:
    """
    Extract data from an Excel file using pandas.
    Returns dict with 'sheets' (list of sheet data as records).
    """
    try:
        import pandas as pd

        xl = pd.ExcelFile(file_path)
        sheets = {}

        for sheet_name in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
            # Convert to list of dicts, handling NaN
            records = df.fillna("").astype(str).to_dict(orient="records")
            headers = list(df.columns)
            sheets[sheet_name] = {
                "headers": headers,
                "records": records[:100],  # Limit to 100 rows for AI context
                "total_rows": len(df)
            }

        # Also create a text representation
        text_parts = []
        for sheet_name, data in sheets.items():
            text_parts.append(f"Sheet: {sheet_name}")
            text_parts.append(f"Headers: {', '.join(str(h) for h in data['headers'])}")
            for rec in data['records'][:20]:  # First 20 rows in text
                text_parts.append(str(rec))
            text_parts.append("")

        return {
            "text": "\n".join(text_parts),
            "sheets": sheets
        }
    except Exception as e:
        return {
            "text": f"[Excel parse error: {str(e)}]\nFile: {os.path.basename(file_path)}",
            "sheets": {}
        }


def parse_image(file_path: str) -> Dict[str, Any]:
    """
    Extract text from an image file using OCR.
    """
    from app.utils.ocr import extract_text_from_image
    text = extract_text_from_image(file_path)
    return {
        "text": text,
        "tables": []
    }


def parse_document(file_path: str, file_type: str, max_pages: int = None) -> Dict[str, Any]:
    """
    Parse a document based on its file type.
    Returns a dict with at minimum a 'text' key.
    """
    if file_type == "pdf":
        return parse_pdf(file_path, max_pages=max_pages)
    elif file_type in ("excel", "xlsx", "xls"):
        return parse_excel(file_path)
    elif file_type in ("image", "png", "jpg", "jpeg"):
        return parse_image(file_path)
    else:
        return {"text": f"[Unsupported file type: {file_type}]", "tables": []}


def get_document_preview(file_path: str, file_type: str) -> str:
    """
    Get a short text preview of a document (first 2 pages / sheet headers).
    """
    result = parse_document(file_path, file_type, max_pages=2)
    from app.utils.text_utils import truncate_text
    return truncate_text(result.get("text", ""), max_chars=4000)
