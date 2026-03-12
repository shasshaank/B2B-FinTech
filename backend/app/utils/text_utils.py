"""
Text utility functions for CreditLens document processing.
"""
import re
from typing import Optional


def truncate_text(text: str, max_chars: int = 8000) -> str:
    """Truncate text to a maximum number of characters."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "... [truncated]"


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\n\t₹]', '', text)
    return text.strip()


def validate_cin(cin: str) -> bool:
    """
    Validate Indian CIN (Corporate Identity Number) format.
    Format: U/L + 5 digits + 2 letters + 4 digits + 3 letters + 6 digits
    """
    pattern = r'^[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$'
    return bool(re.match(pattern, cin.upper()))


def validate_pan(pan: str) -> bool:
    """
    Validate Indian PAN (Permanent Account Number) format.
    Format: 5 letters + 4 digits + 1 letter
    """
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan.upper()))


def safe_json_parse(json_str: Optional[str]) -> Optional[dict]:
    """Safely parse a JSON string, returning None on failure."""
    if not json_str:
        return None
    try:
        import json
        return json.loads(json_str)
    except Exception:
        return None


def format_currency(amount: Optional[float]) -> str:
    """Format a number as Indian currency (₹ Cr)."""
    if amount is None:
        return "N/A"
    return f"₹{amount:,.2f} Cr"
