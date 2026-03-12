"""Pydantic schemas for request/response validation."""
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel


# Entity schemas
class EntityCreate(BaseModel):
    company_name: str
    cin: Optional[str] = None
    pan: Optional[str] = None
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
    cin: Optional[str] = None
    pan: Optional[str] = None
    sector: Optional[str] = None
    sub_sector: Optional[str] = None
    date_of_incorporation: Optional[str] = None
    registered_address: Optional[str] = None
    annual_turnover: Optional[float] = None
    net_worth: Optional[float] = None
    credit_rating: Optional[str] = None
    rating_agency: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Loan schemas
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


# Document schemas
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
    extracted_data: Optional[str] = None
    extraction_schema: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Classification schemas
class ClassifyConfirmRequest(BaseModel):
    category: Optional[str] = None
    status: str  # confirmed/rejected


class ClassifyConfirmResponse(BaseModel):
    document_id: int
    category: Optional[str] = None
    status: str
    message: str


# Extraction schemas
class ExtractionUpdateRequest(BaseModel):
    extracted_data: Any


# Schema management
class SchemaUpdateRequest(BaseModel):
    schemas: Dict[str, Any]


# Secondary research schemas
class NewsItem(BaseModel):
    headline: str
    source: str
    date: str
    sentiment: str


class LegalItem(BaseModel):
    description: str
    severity: str


class MarketSentiment(BaseModel):
    score: float
    summary: str


class SecondaryResearchResponse(BaseModel):
    id: int
    entity_id: int
    news: Optional[List[Dict]] = None
    legal: Optional[List[Dict]] = None
    market_sentiment: Optional[Dict] = None
    sector_analysis: Optional[str] = None
    key_risks: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Recommendation schemas
class RecommendationResponse(BaseModel):
    id: int
    entity_id: int
    decision: str
    risk_score: Optional[float] = None
    confidence: Optional[float] = None
    key_metrics: Optional[Dict] = None
    reasoning: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# SWOT schemas
class SwotResponse(BaseModel):
    id: int
    entity_id: int
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None
    threats: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Report schemas
class ReportResponse(BaseModel):
    id: int
    entity_id: int
    report_data: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
