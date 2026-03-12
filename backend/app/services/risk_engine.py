"""
Risk assessment engine — generates AI-powered loan recommendations.
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

RECOMMENDATION_PROMPT = """You are a senior credit analyst at a leading Indian financial institution. 
Based on the following comprehensive data, provide a loan recommendation.

Entity Details: {entity_json}
Loan Request: {loan_json}
Financial Data Extracted from Documents: {extraction_json}
Secondary Research: {secondary_research_json}

Analyze the following key areas:
1. Financial health (profitability, leverage, liquidity)
2. Business stability and sector outlook
3. Management quality and governance
4. Collateral adequacy
5. Repayment capacity

Provide your recommendation as ONLY valid JSON (no markdown):
{{
  "decision": "APPROVE" | "CONDITIONAL_APPROVE" | "REJECT",
  "risk_score": 0-100,
  "confidence": 0-100,
  "key_metrics": {{
    "debt_to_equity": number_or_null,
    "interest_coverage_ratio": number_or_null,
    "current_ratio": number_or_null,
    "return_on_assets": number_or_null,
    "npa_percentage": number_or_null
  }},
  "reasoning": ["reason1", "reason2", "reason3", "reason4", "reason5"],
  "conditions": ["condition1", "condition2"]
}}"""


def generate_recommendation(
    entity: Dict[str, Any],
    loan: Optional[Dict[str, Any]],
    extraction_data: Dict[str, Any],
    secondary_research: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate a loan recommendation using Gemini AI.
    Falls back to mock data if API key is not configured.
    """
    if not GEMINI_API_KEY:
        return _get_mock_recommendation(entity, loan)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = RECOMMENDATION_PROMPT.format(
            entity_json=json.dumps(entity, indent=2)[:2000],
            loan_json=json.dumps(loan, indent=2)[:1000] if loan else "{}",
            extraction_json=json.dumps(extraction_data, indent=2)[:3000],
            secondary_research_json=json.dumps(secondary_research, indent=2)[:1500] if secondary_research else "{}"
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
        result = _get_mock_recommendation(entity, loan)
        result["_error"] = str(e)
        return result


def _get_mock_recommendation(
    entity: Dict[str, Any],
    loan: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Return a mock recommendation for demo purposes."""
    company_name = entity.get("company_name", "the company")
    sector = entity.get("sector", "")
    credit_rating = entity.get("credit_rating", "Not Rated")
    net_worth = entity.get("net_worth", 0) or 0
    loan_amount = loan.get("loan_amount", 0) if loan else 0

    # Simple heuristic for mock decision
    is_good_rating = credit_rating in ["AAA", "AA+", "AA", "AA-", "A+", "A"]
    is_sufficient_networth = net_worth > loan_amount * 0.3

    if is_good_rating and is_sufficient_networth:
        decision = "APPROVE"
        risk_score = 28.5
    elif is_good_rating or is_sufficient_networth:
        decision = "CONDITIONAL_APPROVE"
        risk_score = 45.0
    else:
        decision = "CONDITIONAL_APPROVE"
        risk_score = 58.0

    return {
        "decision": decision,
        "risk_score": risk_score,
        "confidence": 78.0,
        "key_metrics": {
            "debt_to_equity": 1.8,
            "interest_coverage_ratio": 3.2,
            "current_ratio": 1.45,
            "return_on_assets": 2.8,
            "npa_percentage": 2.4
        },
        "reasoning": [
            f"{company_name} demonstrates adequate financial stability with consistent revenue growth over the past 3 years.",
            f"Credit rating of {credit_rating} indicates acceptable credit quality from recognized rating agencies.",
            f"The {sector} sector shows positive outlook with improving macro indicators supporting business operations.",
            "Collateral coverage appears adequate relative to the loan amount requested.",
            "Management track record and corporate governance structure are satisfactory based on available information."
        ],
        "conditions": [
            "Submission of latest audited financial statements within 30 days",
            "Maintenance of Debt Service Coverage Ratio (DSCR) above 1.25x throughout loan tenure",
            "Quarterly reporting of financial performance and key business metrics"
        ]
    }
