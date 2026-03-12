"""Secondary research service using web scraping and Gemini AI."""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def perform_secondary_research(company_name: str, sector: str, cin: str = None) -> Dict[str, Any]:
    """Perform secondary research for a company."""
    # Try web scraping first, fall back to Gemini
    scraped_data = _scrape_news(company_name)
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if gemini_api_key:
        return _research_with_gemini(company_name, sector, cin, gemini_api_key, scraped_data)
    else:
        logger.info("No Gemini API key, using mock research data")
        return _mock_research(company_name, sector)


def _scrape_news(company_name: str) -> list:
    """Scrape news from Google News RSS."""
    news_items = []
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Google News RSS feed
        url = f"https://news.google.com/rss/search?q={company_name}+financial&hl=en-IN&gl=IN&ceid=IN:en"
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:10]
            
            for item in items:
                news_items.append({
                    "headline": item.find('title').text if item.find('title') else "No title",
                    "source": item.find('source').text if item.find('source') else "Google News",
                    "date": item.find('pubDate').text if item.find('pubDate') else "Unknown",
                    "sentiment": "Neutral",
                    "snippet": ""
                })
    
    except Exception as e:
        logger.warning(f"News scraping failed: {e}")
    
    return news_items


def _research_with_gemini(company_name: str, sector: str, cin: str, api_key: str, scraped_news: list = None) -> Dict[str, Any]:
    """Use Gemini to generate secondary research."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        scraped_info = ""
        if scraped_news:
            scraped_info = f"\n\nScraped news headlines: {json.dumps(scraped_news[:5])}"
        
        prompt = f"""You are a financial research analyst. Provide secondary research for the following company:
Company: {company_name}
Sector: {sector}
CIN: {cin or 'Not available'}
{scraped_info}

Provide comprehensive research and return ONLY valid JSON with this exact structure:
{{
  "news": [
    {{"headline": "...", "source": "...", "date": "...", "sentiment": "Positive/Negative/Neutral"}}
  ],
  "legal": [
    {{"description": "...", "severity": "High/Medium/Low"}}
  ],
  "market_sentiment": {{
    "score": 0-100,
    "summary": "..."
  }},
  "sector_analysis": "Brief analysis of sector trends...",
  "key_risks": ["risk 1", "risk 2", "risk 3"]
}}

Include 5-7 news items, 2-3 legal items, and 4-5 key risks. Make the data realistic and relevant to the company's sector."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean JSON response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        # Merge scraped news if Gemini didn't provide enough
        if scraped_news and len(result.get("news", [])) < 3:
            result["news"] = scraped_news[:7] + result.get("news", [])[:3]
        
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed in Gemini response: {e}")
        return _mock_research(company_name, sector)
    except Exception as e:
        logger.error(f"Gemini research failed: {e}")
        return _mock_research(company_name, sector)


def _mock_research(company_name: str, sector: str) -> Dict[str, Any]:
    """Return mock research data for demonstration."""
    return {
        "news": [
            {
                "headline": f"{company_name} Reports Strong Q3 Performance Amid Market Challenges",
                "source": "Economic Times",
                "date": "2024-12-15",
                "sentiment": "Positive"
            },
            {
                "headline": f"{sector} Sector Shows Resilience as {company_name} Expands Operations",
                "source": "Business Standard",
                "date": "2024-11-28",
                "sentiment": "Positive"
            },
            {
                "headline": f"RBI Tightens Norms for {sector} Companies Including {company_name}",
                "source": "Mint",
                "date": "2024-11-10",
                "sentiment": "Negative"
            },
            {
                "headline": f"{company_name} Secures New Credit Facility Worth \u20b9500 Cr",
                "source": "Financial Express",
                "date": "2024-10-22",
                "sentiment": "Positive"
            },
            {
                "headline": f"Rating Agency Maintains Stable Outlook for {company_name}",
                "source": "CRISIL",
                "date": "2024-10-05",
                "sentiment": "Neutral"
            }
        ],
        "legal": [
            {
                "description": "No major pending litigation cases found in public records",
                "severity": "Low"
            },
            {
                "description": "Routine compliance notices from SEBI regarding disclosure norms",
                "severity": "Low"
            }
        ],
        "market_sentiment": {
            "score": 65,
            "summary": f"Market sentiment for {company_name} is moderately positive. The company has demonstrated steady performance in the {sector} sector with consistent revenue growth. Investor confidence remains stable despite broader market headwinds."
        },
        "sector_analysis": f"The {sector} sector in India continues to show resilience with steady growth projections. Key macroeconomic factors including stable interest rates and government policy support are expected to drive sector performance. However, global uncertainty and regulatory changes present ongoing challenges.",
        "key_risks": [
            "Interest rate volatility may impact borrowing costs and net interest margins",
            "Regulatory changes in the sector could affect business operations",
            "Asset quality concerns if economic conditions deteriorate",
            "Competition from new-age fintech players and digital lenders",
            "Geopolitical and global macroeconomic uncertainties"
        ]
    }
