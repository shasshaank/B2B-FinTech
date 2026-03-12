"""Text processing utilities."""
import re
from typing import List


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might interfere
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()


def truncate_text(text: str, max_length: int = 10000) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "...[truncated]"


def split_into_chunks(text: str, chunk_size: int = 5000) -> List[str]:
    """Split text into chunks of specified size."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks


def extract_numbers_from_text(text: str) -> List[float]:
    """Extract all numbers from text."""
    pattern = r'-?\d+(?:,\d{3})*(?:\.\d+)?'
    matches = re.findall(pattern, text)
    numbers = []
    for match in matches:
        try:
            numbers.append(float(match.replace(',', '')))
        except ValueError:
            pass
    return numbers
