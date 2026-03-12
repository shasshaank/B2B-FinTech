"""
SWOT analysis generator — produces AI-powered SWOT for credit assessment.
"""
import os
import json
from typing import Dict, Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SWOT_PROMPT = """Generate a comprehensive SWOT analysis for credit assessment purposes:
Company: {company_name}
Sector: {sector}
Financial Data Summary: {financial_summary}
Secondary Research Summary: {research_summary}

Return ONLY valid JSON (no markdown):
{{
  "strengths": ["strength1", "strength2", "strength3", "strength4", "strength5"],
  "weaknesses": ["weakness1", "weakness2", "weakness3", "weakness4"],
  "opportunities": ["opportunity1", "opportunity2", "opportunity3", "opportunity4"],
  "threats": ["threat1", "threat2", "threat3", "threat4"]
}}

Each array should have 4-6 detailed bullet points relevant to credit risk assessment."""


def generate_swot(
    entity: Dict[str, Any],
    extraction_data: Dict[str, Any],
    secondary_research: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate SWOT analysis using Gemini AI.
    Falls back to mock data if API key is not configured.
    """
    if not GEMINI_API_KEY:
        return _get_mock_swot(entity)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Build summaries
        financial_summary = json.dumps(extraction_data, indent=2)[:2000]
        research_summary = json.dumps(secondary_research, indent=2)[:1000] if secondary_research else "{}"

        prompt = SWOT_PROMPT.format(
            company_name=entity.get("company_name", ""),
            sector=entity.get("sector", ""),
            financial_summary=financial_summary,
            research_summary=research_summary
        )
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        result = json.loads(text)
        return result
    except Exception as e:
        result = _get_mock_swot(entity)
        result["_error"] = str(e)
        return result


def _get_mock_swot(entity: Dict[str, Any]) -> Dict[str, Any]:
    """Return mock SWOT analysis for demo purposes."""
    company = entity.get("company_name", "The Company")
    sector = entity.get("sector", "Financial Services")

    return {
        "strengths": [
            f"Established market presence and brand recognition in the {sector} sector",
            "Strong and experienced management team with proven track record",
            "Diversified revenue streams reducing concentration risk",
            "Adequate capitalization and healthy net worth position",
            "Robust risk management framework and compliance culture"
        ],
        "weaknesses": [
            "Moderate leverage ratio with potential refinancing risk",
            "Geographic concentration in certain markets",
            "Dependency on external funding for growth capital requirements",
            "Limited digital infrastructure compared to leading competitors"
        ],
        "opportunities": [
            f"Growing demand in the {sector} sector driven by India's economic expansion",
            "Digital transformation initiatives can improve operational efficiency by 20-30%",
            "Untapped rural and semi-urban market segments offering significant growth potential",
            "Strategic partnerships and alliances to expand product offerings and distribution",
            "Favorable regulatory environment supporting sector growth"
        ],
        "threats": [
            "Increasing competition from both traditional and new-age fintech players",
            "Interest rate volatility impacting net interest margins and profitability",
            "Potential asset quality deterioration in stressed economic conditions",
            "Evolving regulatory requirements increasing compliance costs"
        ]
    }
