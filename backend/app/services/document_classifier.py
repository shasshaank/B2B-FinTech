"""
Document classifier service — uses Gemini AI to classify financial documents.
"""
import os
import json
from typing import Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini if API key is available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

CLASSIFICATION_PROMPT = """You are a financial document classifier. Classify this document into exactly one of these categories:
1. ALM (Asset-Liability Management)
2. Shareholding Pattern
3. Borrowing Profile
4. Annual Report - Profit & Loss
5. Annual Report - Balance Sheet
6. Annual Report - Cash Flow
7. Portfolio Performance Data

Return ONLY valid JSON with no markdown formatting:
{{"category": "...", "confidence": 0.0-1.0, "reasoning": "..."}}

Document text:
{extracted_text}"""

MOCK_CLASSIFICATIONS = [
    {"category": "Annual Report - Balance Sheet", "confidence": 0.87, "reasoning": "Document contains typical balance sheet items including assets, liabilities, and equity."},
    {"category": "Annual Report - Profit & Loss", "confidence": 0.91, "reasoning": "Document shows revenue, expenses, and profit/loss figures across financial years."},
    {"category": "ALM (Asset-Liability Management)", "confidence": 0.78, "reasoning": "Document shows maturity buckets for assets and liabilities."},
    {"category": "Borrowing Profile", "confidence": 0.85, "reasoning": "Document lists lenders, facility types, sanctioned and outstanding amounts."},
    {"category": "Shareholding Pattern", "confidence": 0.82, "reasoning": "Document shows shareholder names, holding percentages, and share counts."},
    {"category": "Portfolio Performance Data", "confidence": 0.76, "reasoning": "Document includes segment-wise AUM, NPA, and yield data."},
    {"category": "Annual Report - Cash Flow", "confidence": 0.88, "reasoning": "Document shows cash flows from operating, investing, and financing activities."},
]

_mock_idx = 0


def classify_document(document_text: str, filename: str = "") -> Dict[str, Any]:
    """
    Classify a financial document using Gemini AI.
    Falls back to mock data if API key is not configured.
    """
    global _mock_idx

    if not GEMINI_API_KEY:
        # Return mock classification for demo purposes
        result = MOCK_CLASSIFICATIONS[_mock_idx % len(MOCK_CLASSIFICATIONS)]
        _mock_idx += 1
        return result

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = CLASSIFICATION_PROMPT.format(
            extracted_text=document_text[:6000]  # Limit context length
        )
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        result = json.loads(text)
        return {
            "category": result.get("category", "Unknown"),
            "confidence": float(result.get("confidence", 0.5)),
            "reasoning": result.get("reasoning", "")
        }
    except Exception as e:
        # Fallback to mock on error
        result = MOCK_CLASSIFICATIONS[_mock_idx % len(MOCK_CLASSIFICATIONS)]
        _mock_idx += 1
        result["error"] = str(e)
        return result
