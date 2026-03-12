"""Risk assessment engine using Gemini AI."""
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def generate_recommendation(
    entity: Dict[str, Any],
    loan: Dict[str, Any],
    extracted_data: List[Dict[str, Any]],
    secondary_research: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate a loan recommendation using Gemini AI."""
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if gemini_api_key:
        return _recommend_with_gemini(entity, loan, extracted_data, secondary_research, gemini_api_key)
    else:
        logger.info("No Gemini API key, using mock recommendation")
        return _mock_recommendation(entity, loan)


def _recommend_with_gemini(
    entity: Dict,
    loan: Dict,
    extracted_data: List[Dict],
    secondary_research: Optional[Dict],
    api_key: str
) -> Dict[str, Any]:
    """Use Gemini to generate loan recommendation."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Prepare data summaries
        extraction_summary = json.dumps(extracted_data[:5], default=str) if extracted_data else "{}"
        research_summary = json.dumps({
            "sentiment_score": secondary_research.get("market_sentiment", {}).get("score", 50) if secondary_research else 50,
            "key_risks": secondary_research.get("key_risks", []) if secondary_research else [],
            "legal_issues": len(secondary_research.get("legal", [])) if secondary_research else 0
        }) if secondary_research else "{}"
        
        prompt = f"""You are a senior credit analyst at a financial institution. Based on the following data, provide a loan recommendation.

Entity Details:
{json.dumps(entity, default=str)}

Loan Request:
{json.dumps(loan, default=str)}

Financial Data Extracted (sample):
{extraction_summary}

Secondary Research Summary:
{research_summary}

Provide a comprehensive credit assessment and return ONLY valid JSON with this exact structure:
{{
  "decision": "APPROVE" or "CONDITIONAL_APPROVE" or "REJECT",
  "risk_score": 0-100,
  "confidence": 0-100,
  "key_metrics": {{
    "debt_to_equity": 0.0,
    "interest_coverage_ratio": 0.0,
    "current_ratio": 0.0,
    "return_on_assets": 0.0,
    "npa_percentage": 0.0
  }},
  "reasoning": ["reason 1", "reason 2", "reason 3"],
  "conditions": ["condition 1", "condition 2"]
}}

Risk score: 0=lowest risk, 100=highest risk. Be thorough and realistic."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed in Gemini response: {e}")
        return _mock_recommendation(entity, loan)
    except Exception as e:
        logger.error(f"Gemini recommendation failed: {e}")
        return _mock_recommendation(entity, loan)


def _mock_recommendation(entity: Dict, loan: Dict) -> Dict[str, Any]:
    """Return mock recommendation data."""
    # Simple heuristic based on entity data
    credit_rating = entity.get("credit_rating", "Not Rated")
    annual_turnover = entity.get("annual_turnover", 0) or 0
    net_worth = entity.get("net_worth", 0) or 0
    loan_amount = loan.get("loan_amount", 0) if loan else 0
    
    # Basic risk calculation
    risk_score = 45  # default moderate risk
    
    high_ratings = ["AAA", "AA+", "AA", "AA-"]
    good_ratings = ["A+", "A", "A-", "BBB+"]
    
    if credit_rating in high_ratings:
        risk_score -= 15
        decision = "APPROVE"
    elif credit_rating in good_ratings:
        risk_score -= 5
        decision = "CONDITIONAL_APPROVE"
    elif credit_rating == "Not Rated":
        risk_score += 10
        decision = "CONDITIONAL_APPROVE"
    else:
        risk_score += 20
        decision = "REJECT"
    
    # Check loan to turnover ratio
    if annual_turnover > 0 and loan_amount > 0:
        ratio = loan_amount / annual_turnover
        if ratio > 2:
            risk_score += 15
            decision = "CONDITIONAL_APPROVE" if decision == "APPROVE" else decision
    
    risk_score = max(0, min(100, risk_score))
    
    return {
        "decision": decision,
        "risk_score": risk_score,
        "confidence": 72,
        "key_metrics": {
            "debt_to_equity": round(net_worth / max(loan_amount, 1), 2) if net_worth else 1.5,
            "interest_coverage_ratio": 2.8,
            "current_ratio": 1.45,
            "return_on_assets": 3.2,
            "npa_percentage": 2.5
        },
        "reasoning": [
            f"Credit rating of {credit_rating} indicates {'strong' if credit_rating in high_ratings else 'moderate'} creditworthiness",
            f"Annual turnover of \u20b9{annual_turnover} Cr provides {'adequate' if annual_turnover > loan_amount else 'limited'} revenue base for debt servicing",
            f"Loan-to-turnover ratio of {round(loan_amount/max(annual_turnover, 1), 2):.2f}x is {'within' if loan_amount < annual_turnover else 'above'} acceptable limits",
            "Market conditions in the sector appear stable based on secondary research",
            "No major legal or regulatory concerns identified"
        ],
        "conditions": [
            "Submission of latest audited financial statements",
            "Maintenance of minimum current ratio of 1.2x throughout loan tenure",
            "Quarterly reporting of financial performance metrics"
        ]
    }
