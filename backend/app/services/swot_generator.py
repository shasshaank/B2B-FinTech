"""SWOT analysis generator using Gemini AI."""
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def generate_swot(
    entity: Dict[str, Any],
    extracted_data: List[Dict[str, Any]] = None,
    secondary_research: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate SWOT analysis using Gemini AI."""
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if gemini_api_key:
        return _swot_with_gemini(entity, extracted_data, secondary_research, gemini_api_key)
    else:
        logger.info("No Gemini API key, using mock SWOT data")
        return _mock_swot(entity)


def _swot_with_gemini(
    entity: Dict,
    extracted_data: Optional[List[Dict]],
    secondary_research: Optional[Dict],
    api_key: str
) -> Dict[str, Any]:
    """Use Gemini to generate SWOT analysis."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        extraction_summary = json.dumps(extracted_data[:3], default=str) if extracted_data else "{}"
        research_summary = json.dumps({
            "sector_analysis": secondary_research.get("sector_analysis", "") if secondary_research else "",
            "key_risks": secondary_research.get("key_risks", []) if secondary_research else [],
            "sentiment": secondary_research.get("market_sentiment", {}) if secondary_research else {}
        }) if secondary_research else "{}"
        
        prompt = f"""Generate a comprehensive SWOT analysis for:
Company: {entity.get('company_name', 'Unknown')}
Sector: {entity.get('sector', 'Unknown')}
Credit Rating: {entity.get('credit_rating', 'Not Rated')}
Annual Turnover: \u20b9{entity.get('annual_turnover', 0)} Cr
Net Worth: \u20b9{entity.get('net_worth', 0)} Cr

Financial Data Summary: {extraction_summary}
Secondary Research: {research_summary}

Return ONLY valid JSON with this exact structure:
{{
  "strengths": ["strength 1", "strength 2", "strength 3", "strength 4", "strength 5"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3", "weakness 4"],
  "opportunities": ["opportunity 1", "opportunity 2", "opportunity 3", "opportunity 4", "opportunity 5"],
  "threats": ["threat 1", "threat 2", "threat 3", "threat 4"]
}}

Each item should be a concise, specific point relevant to the company's credit assessment. Include 4-6 items per quadrant."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed in Gemini SWOT response: {e}")
        return _mock_swot(entity)
    except Exception as e:
        logger.error(f"Gemini SWOT failed: {e}")
        return _mock_swot(entity)


def _mock_swot(entity: Dict) -> Dict[str, Any]:
    """Return mock SWOT data."""
    company = entity.get("company_name", "the company")
    sector = entity.get("sector", "Financial Services")
    credit_rating = entity.get("credit_rating", "Not Rated")
    turnover = entity.get("annual_turnover", 0) or 0
    
    return {
        "strengths": [
            f"Established market presence in the {sector} sector with proven track record",
            f"Credit rating of {credit_rating} indicates strong financial discipline" if credit_rating not in ["Not Rated", "Below BBB-"] else "Experienced management team with deep sector expertise",
            f"Annual turnover of \u20b9{turnover} Cr demonstrates significant operational scale" if turnover > 100 else "Lean operational structure with focused business model",
            "Diversified revenue streams reducing concentration risk",
            "Strong regulatory compliance record with no major violations"
        ],
        "weaknesses": [
            "Dependence on external borrowings may increase financial leverage",
            "Geographic concentration in specific markets limits growth potential",
            "Technology infrastructure may require significant upgrades",
            "Limited brand recognition compared to larger competitors in the sector"
        ],
        "opportunities": [
            f"Growing demand for {sector} services in underpenetrated markets",
            "Digital transformation initiatives could improve operational efficiency",
            "Government policy support for the sector through incentive schemes",
            "Potential for strategic partnerships or joint ventures",
            "Expansion into adjacent product lines to increase revenue per customer"
        ],
        "threats": [
            "Increasing regulatory scrutiny and compliance requirements",
            "Rising competition from digital-first companies and fintech disruptors",
            "Interest rate volatility affecting cost of funds and profitability",
            "Economic slowdown could impact asset quality and collections"
        ]
    }
