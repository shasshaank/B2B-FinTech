"""
Pydantic schemas for request/response validation in CreditLens API.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel


# ─── Entity Schemas ──────────────────────────────────────────────────────────

class EntityCreate(BaseModel):
    company_name: str
    cin: str
    pan: str
    sector: Optional[str] = None
    sub_sector: Optional[str] = None
    date_of_incorporation: Optional[str] = None
    registered_address: Optional[str] = None
    annual_turnover: Optional[float] = None
    net_worth: Optional[float] = None
    credit_rating: Optional[str] = None
    rating_agency: Optional[str] = None


class EntityResponse(BaseModel):
    id: int
    company_name: str
    cin: str
    pan: str
    sector: Optional[str] = None
    sub_sector: Optional[str] = None
    date_of_incorporation: Optional[str] = None
    registered_address: Optional[str] = None
    annual_turnover: Optional[float] = None
    net_worth: Optional[float] = None
    credit_rating: Optional[str] = None
    rating_agency: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Loan Detail Schemas ──────────────────────────────────────────────────────

class LoanDetailCreate(BaseModel):
    loan_type: Optional[str] = None
    loan_amount: float
    tenure_months: int
    interest_rate: Optional[float] = None
    purpose: Optional[str] = None
    collateral_details: Optional[str] = None
    repayment_frequency: Optional[str] = None


class LoanDetailResponse(BaseModel):
    id: int
    entity_id: int
    loan_type: Optional[str] = None
    loan_amount: float
    tenure_months: int
    interest_rate: Optional[float] = None
    purpose: Optional[str] = None
    collateral_details: Optional[str] = None
    repayment_frequency: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Document Schemas ─────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    id: int
    entity_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: Optional[int] = None
    upload_path: str
    document_category: Optional[str] = None
    classification_confidence: Optional[float] = None
    classification_status: str
    classification_reasoning: Optional[str] = None
    extracted_data: Optional[str] = None
    extraction_schema: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClassifyConfirmRequest(BaseModel):
    category: str
    status: str  # "confirmed" or "rejected"


class ExtractionUpdateRequest(BaseModel):
    extracted_data: Any


# ─── Schema Schemas ───────────────────────────────────────────────────────────

class SchemaUpdateRequest(BaseModel):
    schema_data: Any


class SchemaResponse(BaseModel):
    entity_id: int
    schema_data: Any


# ─── Secondary Research ───────────────────────────────────────────────────────

class SecondaryResearchResponse(BaseModel):
    id: int
    entity_id: int
    news: Optional[Any] = None
    legal: Optional[Any] = None
    market_sentiment: Optional[Any] = None
    sector_analysis: Optional[str] = None
    key_risks: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Recommendation ───────────────────────────────────────────────────────────

class RecommendationResponse(BaseModel):
    id: int
    entity_id: int
    decision: str
    risk_score: Optional[float] = None
    confidence: Optional[float] = None
    key_metrics: Optional[Any] = None
    reasoning: Optional[Any] = None
    conditions: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── SWOT Analysis ───────────────────────────────────────────────────────────

class SwotAnalysisResponse(BaseModel):
    id: int
    entity_id: int
    strengths: Optional[Any] = None
    weaknesses: Optional[Any] = None
    opportunities: Optional[Any] = None
    threats: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Report ──────────────────────────────────────────────────────────────────

class ReportResponse(BaseModel):
    id: int
    entity_id: int
    report_data: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True
