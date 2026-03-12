"""Document classification service using Gemini AI."""
import os
import json
import logging
from typing import Dict, Any, Optional

from app.services.document_parser import get_document_preview_text

logger = logging.getLogger(__name__)

DOCUMENT_CATEGORIES = [
    "ALM (Asset-Liability Management)",
    "Shareholding Pattern",
    "Borrowing Profile",
    "Annual Report - Profit & Loss",
    "Annual Report - Balance Sheet",
    "Annual Report - Cash Flow",
    "Portfolio Performance Data",
]

MOCK_CLASSIFICATIONS = {
    "alm": {"category": "ALM (Asset-Liability Management)", "confidence": 0.85, "reasoning": "Document contains maturity buckets and gap analysis typical of ALM reports."},
    "shareholding": {"category": "Shareholding Pattern", "confidence": 0.90, "reasoning": "Document shows shareholder names and percentage holdings."},
    "borrowing": {"category": "Borrowing Profile", "confidence": 0.88, "reasoning": "Document lists lenders, facilities, and outstanding amounts."},
    "annual_pl": {"category": "Annual Report - Profit & Loss", "confidence": 0.92, "reasoning": "Document contains revenue, expenses, and profit figures across financial years."},
    "annual_bs": {"category": "Annual Report - Balance Sheet", "confidence": 0.91, "reasoning": "Document shows assets, liabilities, and equity figures."},
    "annual_cf": {"category": "Annual Report - Cash Flow", "confidence": 0.87, "reasoning": "Document contains cash flow from operations, investing, and financing activities."},
    "portfolio": {"category": "Portfolio Performance Data", "confidence": 0.83, "reasoning": "Document shows portfolio segments with AUM and NPA data."},
}


def classify_document(file_path: str, file_type: str) -> Dict[str, Any]:
    """Classify a document using Gemini AI or return mock data."""
    try:
        # Extract preview text for classification
        preview_text = get_document_preview_text(file_path, file_type)
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_api_key:
            return _classify_with_gemini(preview_text, gemini_api_key)
        else:
            logger.info("No Gemini API key, using mock classification")
            return _mock_classify(file_path, preview_text)
    
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return {
            "category": "Annual Report - Balance Sheet",
            "confidence": 0.5,
            "reasoning": f"Classification failed due to error: {str(e)}. Using default category."
        }


def _classify_with_gemini(text: str, api_key: str) -> Dict[str, Any]:
    """Use Gemini API to classify the document."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        categories_list = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(DOCUMENT_CATEGORIES)])
        
        prompt = f"""You are a financial document classifier. Classify this document into exactly one of these categories:
{categories_list}

Return ONLY valid JSON in this exact format: {{"category": "exact category name from the list above", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}

Document text:
{text}"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean JSON response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        # Validate confidence
        if "confidence" in result:
            result["confidence"] = float(result["confidence"])
        
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed in Gemini response: {e}")
        return _mock_classify("", text)
    except Exception as e:
        logger.error(f"Gemini classification failed: {e}")
        return _mock_classify("", text)


def _mock_classify(file_path: str, text: str) -> Dict[str, Any]:
    """Provide mock classification based on filename or text hints."""
    file_path_lower = file_path.lower()
    text_lower = text.lower()
    
    # Check filename hints
    if "alm" in file_path_lower or "asset" in file_path_lower:
        return MOCK_CLASSIFICATIONS["alm"]
    elif "shareholding" in file_path_lower or "share" in file_path_lower:
        return MOCK_CLASSIFICATIONS["shareholding"]
    elif "borrowing" in file_path_lower or "debt" in file_path_lower:
        return MOCK_CLASSIFICATIONS["borrowing"]
    elif "cashflow" in file_path_lower or "cash_flow" in file_path_lower:
        return MOCK_CLASSIFICATIONS["annual_cf"]
    elif "balance" in file_path_lower or "bs" in file_path_lower:
        return MOCK_CLASSIFICATIONS["annual_bs"]
    elif "pl" in file_path_lower or "profit" in file_path_lower or "loss" in file_path_lower:
        return MOCK_CLASSIFICATIONS["annual_pl"]
    elif "portfolio" in file_path_lower:
        return MOCK_CLASSIFICATIONS["portfolio"]
    
    # Check text content hints
    if "maturity" in text_lower and "gap" in text_lower:
        return MOCK_CLASSIFICATIONS["alm"]
    elif "shareholder" in text_lower and "%" in text_lower:
        return MOCK_CLASSIFICATIONS["shareholding"]
    elif "outstanding" in text_lower and "lender" in text_lower:
        return MOCK_CLASSIFICATIONS["borrowing"]
    elif "cash flow" in text_lower or "operating activities" in text_lower:
        return MOCK_CLASSIFICATIONS["annual_cf"]
    elif "balance sheet" in text_lower or "total assets" in text_lower:
        return MOCK_CLASSIFICATIONS["annual_bs"]
    elif "revenue" in text_lower or "profit" in text_lower:
        return MOCK_CLASSIFICATIONS["annual_pl"]
    
    # Default
    return {
        "category": "Annual Report - Balance Sheet",
        "confidence": 0.6,
        "reasoning": "Unable to determine specific category from document content. Defaulting to Balance Sheet."
    }
