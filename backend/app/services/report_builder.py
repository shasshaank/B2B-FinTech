"""Report builder service for generating final credit reports."""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_executive_summary(
    entity: Dict[str, Any],
    loan: Dict[str, Any],
    recommendation: Dict[str, Any],
    swot: Dict[str, Any]
) -> str:
    """Generate executive summary using Gemini AI."""
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if gemini_api_key:
        return _summary_with_gemini(entity, loan, recommendation, swot, gemini_api_key)
    else:
        return _mock_executive_summary(entity, loan, recommendation)


def _summary_with_gemini(entity, loan, recommendation, swot, api_key: str) -> str:
    """Generate executive summary with Gemini."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = f"""Write a professional executive summary (3-4 paragraphs) for a credit assessment report.

Company: {entity.get('company_name')}
Sector: {entity.get('sector')}
Loan Amount: \u20b9{loan.get('loan_amount', 0) if loan else 0} Cr
Loan Type: {loan.get('loan_type', 'Unknown') if loan else 'Unknown'}
Decision: {recommendation.get('decision', 'PENDING')}
Risk Score: {recommendation.get('risk_score', 50)}/100

Write a formal, professional summary suitable for a bank's credit committee. Do not use markdown formatting."""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        logger.error(f"Gemini summary failed: {e}")
        return _mock_executive_summary(entity, loan, recommendation)


def _mock_executive_summary(entity: Dict, loan: Optional[Dict], recommendation: Dict) -> str:
    """Generate a mock executive summary."""
    company = entity.get("company_name", "the applicant")
    sector = entity.get("sector", "Financial Services")
    loan_amount = loan.get("loan_amount", 0) if loan else 0
    loan_type = loan.get("loan_type", "credit facility") if loan else "credit facility"
    decision = recommendation.get("decision", "CONDITIONAL_APPROVE")
    risk_score = recommendation.get("risk_score", 50)
    
    return f"""This credit assessment report has been prepared for {company}, a {sector} sector entity, pursuant to their application for a {loan_type} amounting to \u20b9{loan_amount} Crore.

The assessment is based on a comprehensive review of the entity's financial statements, operational data, market position, and secondary research conducted on the company. The analysis encompasses a four-stage evaluation process including entity onboarding, document analysis, financial data extraction, and AI-powered risk assessment.

Based on the comprehensive analysis, the Credit Committee's recommendation is {decision.replace('_', ' ')} with a risk score of {risk_score}/100 (where 0 represents minimal risk). The key factors driving this recommendation include the entity's financial performance metrics, credit rating, sector outlook, and overall market positioning.

This report should be reviewed in conjunction with the detailed financial analysis, SWOT assessment, and risk metrics presented in the subsequent sections. The final lending decision should incorporate the judgment of the credit committee and any additional due diligence requirements."""


def compile_report(
    entity: Dict[str, Any],
    loan: Optional[Dict[str, Any]],
    documents: list,
    secondary_research: Optional[Dict[str, Any]],
    recommendation: Optional[Dict[str, Any]],
    swot: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Compile all data into a final report structure."""
    
    rec = recommendation or {"decision": "PENDING", "risk_score": 50, "confidence": 0}
    sw = swot or {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}
    
    # Generate executive summary
    exec_summary = generate_executive_summary(entity, loan, rec, sw)
    
    # Compile financial analysis from documents
    financial_analysis = []
    for doc in documents:
        if doc.get("extracted_data"):
            try:
                data = json.loads(doc["extracted_data"]) if isinstance(doc["extracted_data"], str) else doc["extracted_data"]
                financial_analysis.append({
                    "document": doc.get("original_filename", doc.get("filename", "Unknown")),
                    "category": doc.get("document_category", "Unknown"),
                    "data": data
                })
            except (json.JSONDecodeError, TypeError):
                pass
    
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "executive_summary": exec_summary,
        "entity_overview": {
            "company_name": entity.get("company_name"),
            "cin": entity.get("cin"),
            "pan": entity.get("pan"),
            "sector": entity.get("sector"),
            "sub_sector": entity.get("sub_sector"),
            "date_of_incorporation": entity.get("date_of_incorporation"),
            "registered_address": entity.get("registered_address"),
            "annual_turnover": entity.get("annual_turnover"),
            "net_worth": entity.get("net_worth"),
            "credit_rating": entity.get("credit_rating"),
            "rating_agency": entity.get("rating_agency"),
        },
        "loan_details": loan,
        "financial_analysis": financial_analysis,
        "secondary_research": secondary_research,
        "swot_analysis": sw,
        "risk_assessment": {
            "decision": rec.get("decision", "PENDING"),
            "risk_score": rec.get("risk_score", 50),
            "confidence": rec.get("confidence", 0),
            "key_metrics": rec.get("key_metrics", {}),
            "reasoning": rec.get("reasoning", []),
            "conditions": rec.get("conditions", []),
        }
    }
    
    return report


def generate_pdf_report(report_data: Dict[str, Any], entity_name: str) -> bytes:
    """Generate a PDF from the report data using fpdf2."""
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Title
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, "CreditLens", fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(30, 58, 138)
        pdf.ln(5)
        pdf.cell(0, 10, "AI-Powered Credit Assessment Report", align="C", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Company: {entity_name}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Generated: {report_data.get('generated_at', 'N/A')[:10]}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)
        
        def add_section_header(title: str):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(30, 58, 138)
            pdf.set_fill_color(239, 246, 255)
            pdf.cell(0, 10, title, fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            pdf.set_text_color(0, 0, 0)
        
        def add_body_text(text: str):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 6, text)
            pdf.ln(3)
        
        def add_key_value(key: str, value: str):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(60, 7, f"{key}:", new_x="RIGHT", new_y="LAST")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")
        
        # 1. Executive Summary
        add_section_header("1. Executive Summary")
        exec_summary = report_data.get("executive_summary", "")
        add_body_text(exec_summary)
        
        # 2. Entity Overview
        add_section_header("2. Entity Overview")
        entity = report_data.get("entity_overview", {})
        add_key_value("Company Name", entity.get("company_name", "N/A"))
        add_key_value("CIN", entity.get("cin", "N/A"))
        add_key_value("PAN", entity.get("pan", "N/A"))
        add_key_value("Sector", entity.get("sector", "N/A"))
        add_key_value("Date of Incorporation", entity.get("date_of_incorporation", "N/A"))
        add_key_value("Annual Turnover", f"\u20b9{entity.get('annual_turnover', 'N/A')} Cr")
        add_key_value("Net Worth", f"\u20b9{entity.get('net_worth', 'N/A')} Cr")
        add_key_value("Credit Rating", entity.get("credit_rating", "N/A"))
        add_key_value("Rating Agency", entity.get("rating_agency", "N/A"))
        pdf.ln(5)
        
        # 3. Loan Details
        add_section_header("3. Loan Details")
        loan = report_data.get("loan_details") or {}
        add_key_value("Loan Type", loan.get("loan_type", "N/A"))
        add_key_value("Loan Amount", f"\u20b9{loan.get('loan_amount', 'N/A')} Cr")
        add_key_value("Tenure", f"{loan.get('tenure_months', 'N/A')} months")
        add_key_value("Interest Rate", f"{loan.get('interest_rate', 'N/A')}%")
        add_key_value("Repayment Frequency", loan.get("repayment_frequency", "N/A"))
        if loan.get("purpose"):
            add_body_text(f"Purpose: {loan['purpose']}")
        pdf.ln(5)
        
        # 4. Risk Assessment
        add_section_header("4. Risk Assessment & Recommendation")
        risk = report_data.get("risk_assessment", {})
        decision = risk.get("decision", "PENDING")
        
        pdf.set_font("Helvetica", "B", 14)
        color_map = {"APPROVE": (0, 150, 0), "CONDITIONAL_APPROVE": (200, 120, 0), "REJECT": (200, 0, 0)}
        color = color_map.get(decision, (100, 100, 100))
        pdf.set_text_color(*color)
        pdf.cell(0, 12, f"Decision: {decision.replace('_', ' ')}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font("Helvetica", "", 10)
        add_key_value("Risk Score", f"{risk.get('risk_score', 'N/A')}/100")
        add_key_value("Confidence", f"{risk.get('confidence', 'N/A')}%")
        
        metrics = risk.get("key_metrics", {})
        if metrics:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Key Financial Metrics:", new_x="LMARGIN", new_y="NEXT")
            for k, v in metrics.items():
                add_key_value(f"  {k.replace('_', ' ').title()}", str(v))
        
        reasoning = risk.get("reasoning", [])
        if reasoning:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Reasoning:", new_x="LMARGIN", new_y="NEXT")
            for i, r in enumerate(reasoning, 1):
                add_body_text(f"{i}. {r}")
        
        # 5. SWOT Analysis
        pdf.add_page()
        add_section_header("5. SWOT Analysis")
        swot = report_data.get("swot_analysis", {})
        
        for quadrant, color_r in [("strengths", (0, 120, 0)), ("weaknesses", (180, 0, 0)), ("opportunities", (0, 80, 180)), ("threats", (180, 100, 0))]:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*color_r)
            pdf.cell(0, 8, quadrant.upper(), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(50, 50, 50)
            pdf.set_font("Helvetica", "", 10)
            for item in swot.get(quadrant, []):
                pdf.multi_cell(0, 6, f"  \u2022 {item}")
            pdf.ln(4)
        
        # 6. Secondary Research
        add_section_header("6. Secondary Research")
        research = report_data.get("secondary_research") or {}
        
        sentiment = research.get("market_sentiment", {})
        if sentiment:
            add_key_value("Market Sentiment Score", f"{sentiment.get('score', 'N/A')}/100")
            if sentiment.get("summary"):
                add_body_text(sentiment["summary"])
        
        sector_analysis = research.get("sector_analysis", "")
        if sector_analysis:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Sector Analysis:", new_x="LMARGIN", new_y="NEXT")
            add_body_text(sector_analysis)
        
        key_risks = research.get("key_risks", [])
        if key_risks:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Key Risks Identified:", new_x="LMARGIN", new_y="NEXT")
            for risk_item in key_risks:
                add_body_text(f"  \u2022 {risk_item}")
        
        # Footer
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.ln(10)
        pdf.cell(0, 5, "This report was generated by CreditLens - AI-Powered Enterprise Credit Underwriting Platform", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 5, "For internal use only. Not for distribution.", align="C", new_x="LMARGIN", new_y="NEXT")
        
        return bytes(pdf.output())
    
    except ImportError:
        logger.error("fpdf2 not available")
        return b"PDF generation not available - fpdf2 not installed"
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return f"PDF generation failed: {str(e)}".encode()
