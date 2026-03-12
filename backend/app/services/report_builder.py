"""
Report builder service — compiles all data into a final credit report and generates PDF.
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SUMMARY_PROMPT = """You are a senior credit analyst. Write a concise executive summary (3-4 paragraphs) for a credit assessment report:

Company: {company_name}
Sector: {sector}
Loan Request: {loan_amount} Cr for {tenure} months
Decision: {decision}
Risk Score: {risk_score}/100

Key findings:
{key_reasoning}

Write a professional executive summary suitable for senior bank management. Be concise and factual."""


def generate_executive_summary(
    entity: Dict[str, Any],
    loan: Optional[Dict[str, Any]],
    recommendation: Optional[Dict[str, Any]]
) -> str:
    """Generate executive summary using Gemini AI."""
    if not GEMINI_API_KEY or not recommendation:
        return _get_mock_summary(entity, loan, recommendation)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        reasoning = recommendation.get("reasoning", [])
        prompt = SUMMARY_PROMPT.format(
            company_name=entity.get("company_name", ""),
            sector=entity.get("sector", ""),
            loan_amount=loan.get("loan_amount", "N/A") if loan else "N/A",
            tenure=loan.get("tenure_months", "N/A") if loan else "N/A",
            decision=recommendation.get("decision", "N/A"),
            risk_score=recommendation.get("risk_score", "N/A"),
            key_reasoning="\n".join(f"- {r}" for r in reasoning[:5])
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return _get_mock_summary(entity, loan, recommendation)


def _get_mock_summary(
    entity: Dict[str, Any],
    loan: Optional[Dict[str, Any]],
    recommendation: Optional[Dict[str, Any]]
) -> str:
    """Return a mock executive summary."""
    company = entity.get("company_name", "The Applicant")
    sector = entity.get("sector", "Financial Services")
    decision = recommendation.get("decision", "CONDITIONAL_APPROVE") if recommendation else "UNDER REVIEW"
    risk_score = recommendation.get("risk_score", 45) if recommendation else 45
    loan_amount = loan.get("loan_amount", "N/A") if loan else "N/A"

    return f"""This credit assessment report has been prepared by CreditLens AI-Powered Underwriting Platform for {company}, a {sector} sector entity seeking credit facilities.

Based on comprehensive analysis of financial statements, business operations, market position, and secondary research, the credit committee recommendation is: {decision}. The entity has been assigned a risk score of {risk_score}/100, indicating a {'LOW' if risk_score < 35 else 'MODERATE' if risk_score < 65 else 'HIGH'} risk profile.

The loan request for ₹{loan_amount} Cr has been evaluated against the company's repayment capacity, asset quality, and overall financial health. The analysis incorporates AI-driven insights from document extraction, market intelligence, and peer benchmarking.

This report should be read in conjunction with the detailed financial analysis, SWOT assessment, and risk matrices presented in subsequent sections. The final credit decision remains subject to credit committee review and approval per institutional guidelines."""


def build_report(
    entity: Dict[str, Any],
    loan: Optional[Dict[str, Any]],
    documents: list,
    secondary_research: Optional[Dict[str, Any]],
    recommendation: Optional[Dict[str, Any]],
    swot: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Compile all data into a structured report."""
    executive_summary = generate_executive_summary(entity, loan, recommendation)

    # Build financial analysis section from extracted document data
    financial_analysis = {}
    for doc in documents:
        if doc.get("extracted_data"):
            try:
                extracted = json.loads(doc["extracted_data"]) if isinstance(doc["extracted_data"], str) else doc["extracted_data"]
                category = doc.get("document_category", "Unknown")
                financial_analysis[category] = extracted
            except Exception:
                pass

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "executive_summary": executive_summary,
        "entity_overview": entity,
        "loan_details": loan or {},
        "financial_analysis": financial_analysis,
        "secondary_research": secondary_research or {},
        "swot_analysis": swot or {},
        "risk_assessment": recommendation or {},
        "recommendation": {
            "decision": recommendation.get("decision", "PENDING") if recommendation else "PENDING",
            "risk_score": recommendation.get("risk_score") if recommendation else None,
            "confidence": recommendation.get("confidence") if recommendation else None,
            "reasoning": recommendation.get("reasoning", []) if recommendation else [],
            "conditions": recommendation.get("conditions", []) if recommendation else []
        }
    }


def generate_pdf_report(report_data: Dict[str, Any], entity_id: int) -> str:
    """
    Generate a PDF report using fpdf2.
    Returns the path to the generated PDF file.
    """
    from fpdf import FPDF

    os.makedirs(REPORTS_DIR, exist_ok=True)
    pdf_path = os.path.join(REPORTS_DIR, f"credit_report_entity_{entity_id}.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(24, 144, 255)
    pdf.cell(0, 12, "CreditLens - Credit Assessment Report", ln=True, align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Generated: {report_data.get('generated_at', '')}", ln=True, align="C")
    pdf.ln(8)

    # Helper to write a section
    def write_section(title: str, content: str):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(24, 144, 255)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_draw_color(24, 144, 255)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        # Handle long text with multi_cell
        pdf.multi_cell(0, 5, content)
        pdf.ln(5)

    # 1. Executive Summary
    exec_summary = report_data.get("executive_summary", "")
    write_section("1. Executive Summary", exec_summary)

    # 2. Entity Overview
    entity = report_data.get("entity_overview", {})
    entity_text = (
        f"Company Name: {entity.get('company_name', 'N/A')}\n"
        f"CIN: {entity.get('cin', 'N/A')}\n"
        f"PAN: {entity.get('pan', 'N/A')}\n"
        f"Sector: {entity.get('sector', 'N/A')} | Sub-Sector: {entity.get('sub_sector', 'N/A')}\n"
        f"Date of Incorporation: {entity.get('date_of_incorporation', 'N/A')}\n"
        f"Annual Turnover: INR {entity.get('annual_turnover', 'N/A')} Cr\n"
        f"Net Worth: INR {entity.get('net_worth', 'N/A')} Cr\n"
        f"Credit Rating: {entity.get('credit_rating', 'N/A')} ({entity.get('rating_agency', 'N/A')})\n"
        f"Registered Address: {entity.get('registered_address', 'N/A')}"
    )
    write_section("2. Entity Overview", entity_text)

    # 3. Loan Details
    loan = report_data.get("loan_details", {})
    loan_text = (
        f"Loan Type: {loan.get('loan_type', 'N/A')}\n"
        f"Loan Amount: INR {loan.get('loan_amount', 'N/A')} Cr\n"
        f"Tenure: {loan.get('tenure_months', 'N/A')} months\n"
        f"Interest Rate: {loan.get('interest_rate', 'N/A')}%\n"
        f"Repayment Frequency: {loan.get('repayment_frequency', 'N/A')}\n"
        f"Purpose: {loan.get('purpose', 'N/A')}\n"
        f"Collateral: {loan.get('collateral_details', 'N/A')}"
    )
    write_section("3. Loan Details", loan_text)

    # 4. Risk Assessment & Recommendation
    rec = report_data.get("recommendation", {})
    decision = rec.get("decision", "PENDING")
    risk_score = rec.get("risk_score", "N/A")
    confidence = rec.get("confidence", "N/A")
    reasoning = rec.get("reasoning", [])
    conditions = rec.get("conditions", [])

    rec_text = (
        f"Decision: {decision}\n"
        f"Risk Score: {risk_score}/100\n"
        f"Confidence: {confidence}%\n\n"
        f"Key Reasoning:\n"
    )
    for i, r in enumerate(reasoning, 1):
        rec_text += f"  {i}. {r}\n"
    if conditions:
        rec_text += "\nConditions:\n"
        for i, c in enumerate(conditions, 1):
            rec_text += f"  {i}. {c}\n"
    write_section("4. Risk Assessment & Recommendation", rec_text)

    # 5. SWOT Analysis
    swot = report_data.get("swot_analysis", {})
    swot_text = ""
    for category in ["strengths", "weaknesses", "opportunities", "threats"]:
        items = swot.get(category, [])
        swot_text += f"{category.capitalize()}:\n"
        for item in items:
            swot_text += f"  + {item}\n"
        swot_text += "\n"
    write_section("5. SWOT Analysis", swot_text)

    # 6. Secondary Research Summary
    research = report_data.get("secondary_research", {})
    sentiment = research.get("market_sentiment", {})
    sector_analysis = research.get("sector_analysis", "N/A")
    key_risks = research.get("key_risks", [])
    research_text = (
        f"Market Sentiment Score: {sentiment.get('score', 'N/A')}/100\n"
        f"Summary: {sentiment.get('summary', 'N/A')}\n\n"
        f"Sector Analysis:\n{sector_analysis}\n\n"
        f"Key Risks Identified:\n"
    )
    for risk in key_risks:
        research_text += f"  - {risk}\n"
    write_section("6. Secondary Research Summary", research_text)

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "CreditLens AI-Powered Underwriting Platform | Confidential Credit Assessment Report", align="C")

    pdf.output(pdf_path)
    return pdf_path
