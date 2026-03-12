"""
SQLAlchemy ORM models for CreditLens platform.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


class Entity(Base):
    """Represents a corporate entity seeking credit."""
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    company_name = Column(String(255), nullable=False)
    cin = Column(String(21), nullable=False, unique=True)
    pan = Column(String(10), nullable=False)
    sector = Column(String(100), nullable=True)
    sub_sector = Column(String(100), nullable=True)
    date_of_incorporation = Column(String(20), nullable=True)
    registered_address = Column(Text, nullable=True)
    annual_turnover = Column(Float, nullable=True)
    net_worth = Column(Float, nullable=True)
    credit_rating = Column(String(20), nullable=True)
    rating_agency = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loan_details = relationship("LoanDetail", back_populates="entity", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="entity", cascade="all, delete-orphan")
    secondary_research = relationship("SecondaryResearch", back_populates="entity", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="entity", cascade="all, delete-orphan")
    swot_analyses = relationship("SwotAnalysis", back_populates="entity", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="entity", cascade="all, delete-orphan")
    schemas = relationship("EntitySchema", back_populates="entity", cascade="all, delete-orphan")


class LoanDetail(Base):
    """Loan details linked to an entity."""
    __tablename__ = "loan_details"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    loan_type = Column(String(100), nullable=True)
    loan_amount = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=True)
    purpose = Column(Text, nullable=True)
    collateral_details = Column(Text, nullable=True)
    repayment_frequency = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    entity = relationship("Entity", back_populates="loan_details")


class Document(Base):
    """Uploaded document with classification and extraction data."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf/excel/image
    file_size = Column(Integer, nullable=True)
    upload_path = Column(Text, nullable=False)
    document_category = Column(String(100), nullable=True)
    classification_confidence = Column(Float, nullable=True)
    classification_status = Column(String(50), default="uploaded")  # uploaded/classified/confirmed/rejected
    classification_reasoning = Column(Text, nullable=True)
    extracted_data = Column(Text, nullable=True)  # JSON
    extraction_schema = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    entity = relationship("Entity", back_populates="documents")


class EntitySchema(Base):
    """Custom extraction schema for an entity."""
    __tablename__ = "entity_schemas"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    schema_data = Column(Text, nullable=False)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    entity = relationship("Entity", back_populates="schemas")


class SecondaryResearch(Base):
    """Secondary research results for an entity."""
    __tablename__ = "secondary_research"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    news = Column(Text, nullable=True)  # JSON
    legal = Column(Text, nullable=True)  # JSON
    market_sentiment = Column(Text, nullable=True)  # JSON
    sector_analysis = Column(Text, nullable=True)
    key_risks = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    entity = relationship("Entity", back_populates="secondary_research")


class Recommendation(Base):
    """AI loan recommendation for an entity."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    decision = Column(String(30), nullable=False)  # APPROVE/CONDITIONAL_APPROVE/REJECT
    risk_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    key_metrics = Column(Text, nullable=True)  # JSON
    reasoning = Column(Text, nullable=True)  # JSON
    conditions = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    entity = relationship("Entity", back_populates="recommendations")


class SwotAnalysis(Base):
    """SWOT analysis for an entity."""
    __tablename__ = "swot_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    strengths = Column(Text, nullable=True)  # JSON
    weaknesses = Column(Text, nullable=True)  # JSON
    opportunities = Column(Text, nullable=True)  # JSON
    threats = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    entity = relationship("Entity", back_populates="swot_analyses")


class Report(Base):
    """Final compiled report for an entity."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    report_data = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    entity = relationship("Entity", back_populates="reports")
