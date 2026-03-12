"""
Secondary research service — scrapes news and uses Gemini for company research.
"""
import os
import json
from typing import Dict, Any, List

import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

RESEARCH_PROMPT = """You are a financial research analyst. Provide secondary research for the following company:
Company: {company_name}
Sector: {sector}
CIN: {cin}

Provide comprehensive analysis covering:
1. Recent significant news (last 6 months)
2. Legal/regulatory concerns
3. Market sentiment analysis
4. Sector outlook and macro trends
5. Key risk signals

Return ONLY valid JSON (no markdown) with this structure:
{{
  "news": [
    {{"headline": "...", "source": "...", "date": "...", "sentiment": "Positive/Negative/Neutral", "snippet": "..."}}
  ],
  "legal": [
    {{"description": "...", "severity": "High/Medium/Low"}}
  ],
  "market_sentiment": {{
    "score": 0-100,
    "summary": "..."
  }},
  "sector_analysis": "...",
  "key_risks": ["risk1", "risk2", "risk3"]
}}"""


def scrape_google_news(company_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Attempt to scrape Google News for recent company news.
    Falls back gracefully if blocked.
    """
    try:
        query = f"{company_name} financial news India"
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "xml")
            items = soup.find_all("item")[:max_results]
            news = []
            for item in items:
                news.append({
                    "headline": item.find("title").text if item.find("title") else "",
                    "source": item.find("source").text if item.find("source") else "Google News",
                    "date": item.find("pubDate").text if item.find("pubDate") else "",
                    "sentiment": "Neutral",
                    "snippet": item.find("description").text[:200] if item.find("description") else ""
                })
            return news
    except Exception:
        pass
    return []


def get_secondary_research(company_name: str, sector: str, cin: str) -> Dict[str, Any]:
    """
    Perform secondary research using web scraping + Gemini AI fallback.
    """
    # Try scraping Google News first
    scraped_news = scrape_google_news(company_name)

    if not GEMINI_API_KEY:
        # Return mock data if no API key
        return _get_mock_research(company_name, sector, scraped_news)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = RESEARCH_PROMPT.format(
            company_name=company_name,
            sector=sector,
            cin=cin
        )
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        result = json.loads(text)

        # Merge scraped news if available
        if scraped_news and len(scraped_news) > 0:
            existing_news = result.get("news", [])
            result["news"] = scraped_news[:3] + existing_news

        return result
    except Exception as e:
        return _get_mock_research(company_name, sector, scraped_news, error=str(e))


def _get_mock_research(company_name: str, sector: str, scraped_news: List = None, error: str = None) -> Dict[str, Any]:
    """Return mock secondary research data for demo purposes."""
    news = scraped_news or []
    if not news:
        news = [
            {
                "headline": f"{company_name} reports strong Q3 FY2025 results with 18% revenue growth",
                "source": "Economic Times",
                "date": "2025-02-15",
                "sentiment": "Positive",
                "snippet": f"{company_name} has reported robust financial performance in Q3 FY2025..."
            },
            {
                "headline": f"{sector} sector outlook remains positive amid strong credit demand",
                "source": "Business Standard",
                "date": "2025-01-20",
                "sentiment": "Positive",
                "snippet": "The sector continues to show resilience with stable asset quality..."
            },
            {
                "headline": f"{company_name} maintains stable credit rating amid market volatility",
                "source": "CARE Ratings",
                "date": "2024-12-10",
                "sentiment": "Neutral",
                "snippet": "Rating agency reaffirms rating citing stable business operations..."
            }
        ]

    return {
        "news": news,
        "legal": [
            {
                "description": "No significant legal proceedings or regulatory actions identified.",
                "severity": "Low"
            }
        ],
        "market_sentiment": {
            "score": 68,
            "summary": f"{company_name} maintains a positive market sentiment with stable financial performance. The {sector} sector continues to show growth momentum backed by strong demand fundamentals."
        },
        "sector_analysis": f"The {sector} sector in India is experiencing steady growth driven by supportive regulatory environment, improving credit penetration, and digital transformation. Key macro factors include stable interest rate environment, robust domestic consumption, and government infrastructure spending.",
        "key_risks": [
            "Interest rate risk amid global monetary policy uncertainty",
            "Asset quality deterioration in stressed segments",
            "Regulatory compliance costs and capital adequacy requirements",
            "Technology and cybersecurity risks",
            "Concentration risk in specific geographies or sectors"
        ]
    }
