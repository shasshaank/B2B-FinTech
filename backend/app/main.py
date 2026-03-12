"""
CreditLens FastAPI Backend Application
AI-Powered Enterprise Credit Underwriting Platform
"""
import os
import json
import shutil
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db, init_db
from app import models
from app.schemas import (
    EntityCreate, EntityResponse,
    LoanDetailCreate, LoanDetailResponse,
    DocumentResponse, ClassifyConfirmRequest, ExtractionUpdateRequest,
    SchemaUpdateRequest, SchemaResponse,
    SecondaryResearchResponse, RecommendationResponse,
    SwotAnalysisResponse, ReportResponse
)

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

app = FastAPI(
    title="CreditLens API",
    description="AI-Powered Enterprise Credit Underwriting Platform",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CreditLens API", "version": "1.0.0"}


# ─── STAGE 1: Entity Onboarding ───────────────────────────────────────────────

@app.post("/entity", response_model=EntityResponse, tags=["Stage 1: Onboarding"])
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    """Create a new corporate entity record."""
    try:
        db_entity = models.Entity(**entity.dict())
        db.add(db_entity)
        db.commit()
        db.refresh(db_entity)
        return db_entity
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create entity: {str(e)}")


@app.get("/entity/{entity_id}", response_model=EntityResponse, tags=["Stage 1: Onboarding"])
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Retrieve entity details by ID."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@app.post("/entity/{entity_id}/loan", response_model=LoanDetailResponse, tags=["Stage 1: Onboarding"])
def create_loan_details(entity_id: int, loan: LoanDetailCreate, db: Session = Depends(get_db)):
    """Add loan details for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    try:
        db_loan = models.LoanDetail(entity_id=entity_id, **loan.dict())
        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        return db_loan
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create loan details: {str(e)}")


@app.get("/entity/{entity_id}/loan", response_model=List[LoanDetailResponse], tags=["Stage 1: Onboarding"])
def get_loan_details(entity_id: int, db: Session = Depends(get_db)):
    """Get all loan details for an entity."""
    loans = db.query(models.LoanDetail).filter(models.LoanDetail.entity_id == entity_id).all()
    return loans


# ─── STAGE 2: Document Ingestion ──────────────────────────────────────────────

@app.post("/entity/{entity_id}/documents", response_model=DocumentResponse, tags=["Stage 2: Ingestion"])
async def upload_document(
    entity_id: int,
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a document for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Determine file type
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        file_type = "pdf"
    elif ext in ("xlsx", "xls"):
        file_type = "excel"
    elif ext in ("png", "jpg", "jpeg"):
        file_type = "image"
    else:
        file_type = "other"

    # Create entity upload directory
    entity_upload_dir = os.path.join(UPLOAD_DIR, str(entity_id))
    os.makedirs(entity_upload_dir, exist_ok=True)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(entity_upload_dir, unique_filename)

    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        file_size = len(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create DB record
    try:
        db_doc = models.Document(
            entity_id=entity_id,
            filename=unique_filename,
            original_filename=filename,
            file_type=file_type,
            file_size=file_size,
            upload_path=file_path,
            document_category=category,
            classification_status="uploaded"
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        return db_doc
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save document record: {str(e)}")


@app.get("/entity/{entity_id}/documents", response_model=List[DocumentResponse], tags=["Stage 2: Ingestion"])
def get_entity_documents(entity_id: int, db: Session = Depends(get_db)):
    """Get all documents for an entity."""
    docs = db.query(models.Document).filter(models.Document.entity_id == entity_id).all()
    return docs


@app.delete("/documents/{doc_id}", tags=["Stage 2: Ingestion"])
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document and its file."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from disk
    if os.path.exists(doc.upload_path):
        try:
            os.remove(doc.upload_path)
        except Exception:
            pass  # File already deleted or permission issue

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}


# ─── STAGE 3: Extraction & Classification ─────────────────────────────────────

@app.post("/documents/{doc_id}/classify", tags=["Stage 3: Extraction"])
def classify_document(doc_id: int, db: Session = Depends(get_db)):
    """Classify a document using AI."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        from app.services.document_parser import get_document_preview
        from app.services.document_classifier import classify_document as ai_classify

        # Extract text preview for classification
        document_text = get_document_preview(doc.upload_path, doc.file_type)

        # Classify with AI
        result = ai_classify(document_text, doc.original_filename)

        # Update document record
        doc.document_category = result["category"]
        doc.classification_confidence = result["confidence"]
        doc.classification_reasoning = result.get("reasoning", "")
        doc.classification_status = "classified"
        db.commit()
        db.refresh(doc)

        return {
            "document_id": doc_id,
            "category": result["category"],
            "confidence": result["confidence"],
            "reasoning": result.get("reasoning", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.put("/documents/{doc_id}/classify/confirm", tags=["Stage 3: Extraction"])
def confirm_classification(doc_id: int, request: ClassifyConfirmRequest, db: Session = Depends(get_db)):
    """Confirm or reject the AI classification of a document."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.document_category = request.category
    doc.classification_status = request.status
    db.commit()
    db.refresh(doc)
    return {"document_id": doc_id, "category": request.category, "status": request.status}


@app.post("/documents/{doc_id}/extract", tags=["Stage 3: Extraction"])
def extract_document(doc_id: int, db: Session = Depends(get_db)):
    """Extract structured data from a classified document using AI."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        from app.services.document_parser import parse_document
        from app.services.schema_mapper import get_default_schema
        import google.generativeai as genai

        gemini_api_key = os.getenv("GEMINI_API_KEY")

        # Get schema for this document's category
        category = doc.document_category or "Unknown"
        schema = get_default_schema(category)

        # Parse the full document
        parsed = parse_document(doc.upload_path, doc.file_type)
        doc_content = parsed.get("text", "")[:8000]  # Limit context

        # Store the schema
        doc.extraction_schema = json.dumps(schema)

        if not gemini_api_key:
            # Return mock extracted data
            extracted = _get_mock_extraction(category, schema)
        else:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            extract_prompt = f"""You are a financial data extraction engine. Extract structured data from this document according to the following schema:
{json.dumps(schema, indent=2)}

Return the extracted data as a JSON array of objects matching the schema fields.
Be precise with numbers — preserve exact values from the document.
Return ONLY valid JSON array (no markdown).

Document content:
{doc_content}"""

            response = model.generate_content(extract_prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            extracted = json.loads(text)

        doc.extracted_data = json.dumps(extracted)
        db.commit()
        db.refresh(doc)

        return {
            "document_id": doc_id,
            "category": category,
            "schema": schema,
            "extracted_data": extracted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.get("/documents/{doc_id}/extraction", tags=["Stage 3: Extraction"])
def get_extraction(doc_id: int, db: Session = Depends(get_db)):
    """Get extracted data for a document."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    extracted = None
    schema = None
    if doc.extracted_data:
        try:
            extracted = json.loads(doc.extracted_data)
        except Exception:
            extracted = doc.extracted_data
    if doc.extraction_schema:
        try:
            schema = json.loads(doc.extraction_schema)
        except Exception:
            schema = doc.extraction_schema

    return {
        "document_id": doc_id,
        "category": doc.document_category,
        "schema": schema,
        "extracted_data": extracted
    }


@app.put("/documents/{doc_id}/extraction", tags=["Stage 3: Extraction"])
def update_extraction(doc_id: int, request: ExtractionUpdateRequest, db: Session = Depends(get_db)):
    """Update extracted data with human corrections."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.extracted_data = json.dumps(request.extracted_data)
    db.commit()
    return {"document_id": doc_id, "message": "Extraction data updated successfully"}


@app.get("/entity/{entity_id}/schema", tags=["Stage 3: Extraction"])
def get_schema(entity_id: int, db: Session = Depends(get_db)):
    """Get extraction schemas for an entity (custom or default)."""
    from app.services.schema_mapper import get_all_default_schemas

    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Check for custom schema
    schema_record = (
        db.query(models.EntitySchema)
        .filter(models.EntitySchema.entity_id == entity_id)
        .order_by(models.EntitySchema.id.desc())
        .first()
    )

    if schema_record:
        try:
            schema_data = json.loads(schema_record.schema_data)
        except Exception:
            schema_data = get_all_default_schemas()
    else:
        schema_data = get_all_default_schemas()

    return {"entity_id": entity_id, "schema_data": schema_data}


@app.put("/entity/{entity_id}/schema", tags=["Stage 3: Extraction"])
def update_schema(entity_id: int, request: SchemaUpdateRequest, db: Session = Depends(get_db)):
    """Save custom extraction schema for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    schema_record = (
        db.query(models.EntitySchema)
        .filter(models.EntitySchema.entity_id == entity_id)
        .first()
    )

    if schema_record:
        schema_record.schema_data = json.dumps(request.schema_data)
        schema_record.updated_at = datetime.utcnow()
    else:
        schema_record = models.EntitySchema(
            entity_id=entity_id,
            schema_data=json.dumps(request.schema_data)
        )
        db.add(schema_record)

    db.commit()
    return {"entity_id": entity_id, "message": "Schema updated successfully"}


# ─── STAGE 4: Analysis & Reporting ───────────────────────────────────────────

@app.post("/entity/{entity_id}/secondary-research", tags=["Stage 4: Analysis"])
def run_secondary_research(entity_id: int, db: Session = Depends(get_db)):
    """Run secondary research for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    try:
        from app.services.secondary_research import get_secondary_research

        result = get_secondary_research(
            company_name=entity.company_name,
            sector=entity.sector or "",
            cin=entity.cin
        )

        # Save to DB (upsert)
        research_record = (
            db.query(models.SecondaryResearch)
            .filter(models.SecondaryResearch.entity_id == entity_id)
            .first()
        )
        if research_record:
            research_record.news = json.dumps(result.get("news", []))
            research_record.legal = json.dumps(result.get("legal", []))
            research_record.market_sentiment = json.dumps(result.get("market_sentiment", {}))
            research_record.sector_analysis = result.get("sector_analysis", "")
            research_record.key_risks = json.dumps(result.get("key_risks", []))
        else:
            research_record = models.SecondaryResearch(
                entity_id=entity_id,
                news=json.dumps(result.get("news", [])),
                legal=json.dumps(result.get("legal", [])),
                market_sentiment=json.dumps(result.get("market_sentiment", {})),
                sector_analysis=result.get("sector_analysis", ""),
                key_risks=json.dumps(result.get("key_risks", []))
            )
            db.add(research_record)

        db.commit()
        db.refresh(research_record)

        # Return parsed data
        return {
            "id": research_record.id,
            "entity_id": entity_id,
            "news": result.get("news", []),
            "legal": result.get("legal", []),
            "market_sentiment": result.get("market_sentiment", {}),
            "sector_analysis": result.get("sector_analysis", ""),
            "key_risks": result.get("key_risks", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Secondary research failed: {str(e)}")


@app.get("/entity/{entity_id}/secondary-research", tags=["Stage 4: Analysis"])
def get_secondary_research(entity_id: int, db: Session = Depends(get_db)):
    """Get stored secondary research for an entity."""
    research = (
        db.query(models.SecondaryResearch)
        .filter(models.SecondaryResearch.entity_id == entity_id)
        .order_by(models.SecondaryResearch.id.desc())
        .first()
    )
    if not research:
        raise HTTPException(status_code=404, detail="No secondary research found. Run research first.")

    return {
        "id": research.id,
        "entity_id": entity_id,
        "news": json.loads(research.news) if research.news else [],
        "legal": json.loads(research.legal) if research.legal else [],
        "market_sentiment": json.loads(research.market_sentiment) if research.market_sentiment else {},
        "sector_analysis": research.sector_analysis or "",
        "key_risks": json.loads(research.key_risks) if research.key_risks else []
    }


@app.post("/entity/{entity_id}/recommendation", tags=["Stage 4: Analysis"])
def generate_recommendation(entity_id: int, db: Session = Depends(get_db)):
    """Generate an AI loan recommendation for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    try:
        from app.services.risk_engine import generate_recommendation as ai_recommend

        # Gather all data
        loan = db.query(models.LoanDetail).filter(models.LoanDetail.entity_id == entity_id).first()
        documents = db.query(models.Document).filter(models.Document.entity_id == entity_id).all()
        research = db.query(models.SecondaryResearch).filter(models.SecondaryResearch.entity_id == entity_id).first()

        entity_dict = {
            "company_name": entity.company_name,
            "cin": entity.cin,
            "sector": entity.sector,
            "annual_turnover": entity.annual_turnover,
            "net_worth": entity.net_worth,
            "credit_rating": entity.credit_rating
        }

        loan_dict = None
        if loan:
            loan_dict = {
                "loan_type": loan.loan_type,
                "loan_amount": loan.loan_amount,
                "tenure_months": loan.tenure_months,
                "interest_rate": loan.interest_rate,
                "purpose": loan.purpose
            }

        # Collect extraction data
        extraction_data = {}
        for doc in documents:
            if doc.extracted_data:
                try:
                    extraction_data[doc.document_category or f"doc_{doc.id}"] = json.loads(doc.extracted_data)
                except Exception:
                    pass

        # Parse secondary research
        research_dict = None
        if research:
            research_dict = {
                "market_sentiment": json.loads(research.market_sentiment) if research.market_sentiment else {},
                "key_risks": json.loads(research.key_risks) if research.key_risks else [],
                "sector_analysis": research.sector_analysis
            }

        result = ai_recommend(entity_dict, loan_dict, extraction_data, research_dict)

        # Save to DB
        rec_record = models.Recommendation(
            entity_id=entity_id,
            decision=result.get("decision", "CONDITIONAL_APPROVE"),
            risk_score=result.get("risk_score"),
            confidence=result.get("confidence"),
            key_metrics=json.dumps(result.get("key_metrics", {})),
            reasoning=json.dumps(result.get("reasoning", [])),
            conditions=json.dumps(result.get("conditions", []))
        )
        db.add(rec_record)
        db.commit()
        db.refresh(rec_record)

        return {
            "id": rec_record.id,
            "entity_id": entity_id,
            "decision": result.get("decision"),
            "risk_score": result.get("risk_score"),
            "confidence": result.get("confidence"),
            "key_metrics": result.get("key_metrics", {}),
            "reasoning": result.get("reasoning", []),
            "conditions": result.get("conditions", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")


@app.get("/entity/{entity_id}/recommendation", tags=["Stage 4: Analysis"])
def get_recommendation(entity_id: int, db: Session = Depends(get_db)):
    """Get the latest recommendation for an entity."""
    rec = (
        db.query(models.Recommendation)
        .filter(models.Recommendation.entity_id == entity_id)
        .order_by(models.Recommendation.id.desc())
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="No recommendation found. Run analysis first.")

    return {
        "id": rec.id,
        "entity_id": entity_id,
        "decision": rec.decision,
        "risk_score": rec.risk_score,
        "confidence": rec.confidence,
        "key_metrics": json.loads(rec.key_metrics) if rec.key_metrics else {},
        "reasoning": json.loads(rec.reasoning) if rec.reasoning else [],
        "conditions": json.loads(rec.conditions) if rec.conditions else []
    }


@app.post("/entity/{entity_id}/swot", tags=["Stage 4: Analysis"])
def generate_swot(entity_id: int, db: Session = Depends(get_db)):
    """Generate SWOT analysis for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    try:
        from app.services.swot_generator import generate_swot as ai_swot

        # Gather data
        documents = db.query(models.Document).filter(models.Document.entity_id == entity_id).all()
        research = db.query(models.SecondaryResearch).filter(models.SecondaryResearch.entity_id == entity_id).first()

        entity_dict = {
            "company_name": entity.company_name,
            "sector": entity.sector,
            "annual_turnover": entity.annual_turnover,
            "net_worth": entity.net_worth,
            "credit_rating": entity.credit_rating
        }

        extraction_data = {}
        for doc in documents:
            if doc.extracted_data:
                try:
                    extraction_data[doc.document_category or f"doc_{doc.id}"] = json.loads(doc.extracted_data)
                except Exception:
                    pass

        research_dict = None
        if research:
            research_dict = {
                "sector_analysis": research.sector_analysis,
                "key_risks": json.loads(research.key_risks) if research.key_risks else []
            }

        result = ai_swot(entity_dict, extraction_data, research_dict)

        # Save to DB
        swot_record = models.SwotAnalysis(
            entity_id=entity_id,
            strengths=json.dumps(result.get("strengths", [])),
            weaknesses=json.dumps(result.get("weaknesses", [])),
            opportunities=json.dumps(result.get("opportunities", [])),
            threats=json.dumps(result.get("threats", []))
        )
        db.add(swot_record)
        db.commit()
        db.refresh(swot_record)

        return {
            "id": swot_record.id,
            "entity_id": entity_id,
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "opportunities": result.get("opportunities", []),
            "threats": result.get("threats", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SWOT generation failed: {str(e)}")


@app.get("/entity/{entity_id}/swot", tags=["Stage 4: Analysis"])
def get_swot(entity_id: int, db: Session = Depends(get_db)):
    """Get the latest SWOT analysis for an entity."""
    swot = (
        db.query(models.SwotAnalysis)
        .filter(models.SwotAnalysis.entity_id == entity_id)
        .order_by(models.SwotAnalysis.id.desc())
        .first()
    )
    if not swot:
        raise HTTPException(status_code=404, detail="No SWOT analysis found. Run analysis first.")

    return {
        "id": swot.id,
        "entity_id": entity_id,
        "strengths": json.loads(swot.strengths) if swot.strengths else [],
        "weaknesses": json.loads(swot.weaknesses) if swot.weaknesses else [],
        "opportunities": json.loads(swot.opportunities) if swot.opportunities else [],
        "threats": json.loads(swot.threats) if swot.threats else []
    }


@app.post("/entity/{entity_id}/report", tags=["Stage 4: Analysis"])
def generate_report(entity_id: int, db: Session = Depends(get_db)):
    """Generate the final credit assessment report."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    try:
        from app.services.report_builder import build_report

        loan = db.query(models.LoanDetail).filter(models.LoanDetail.entity_id == entity_id).first()
        documents = db.query(models.Document).filter(models.Document.entity_id == entity_id).all()
        research = db.query(models.SecondaryResearch).filter(models.SecondaryResearch.entity_id == entity_id).first()
        rec = db.query(models.Recommendation).filter(models.Recommendation.entity_id == entity_id).order_by(models.Recommendation.id.desc()).first()
        swot = db.query(models.SwotAnalysis).filter(models.SwotAnalysis.entity_id == entity_id).order_by(models.SwotAnalysis.id.desc()).first()

        entity_dict = {c.name: getattr(entity, c.name) for c in entity.__table__.columns}
        entity_dict["created_at"] = str(entity_dict.get("created_at", ""))
        entity_dict["updated_at"] = str(entity_dict.get("updated_at", ""))

        loan_dict = None
        if loan:
            loan_dict = {c.name: getattr(loan, c.name) for c in loan.__table__.columns}
            loan_dict["created_at"] = str(loan_dict.get("created_at", ""))

        docs_list = []
        for doc in documents:
            docs_list.append({
                "id": doc.id,
                "document_category": doc.document_category,
                "original_filename": doc.original_filename,
                "extracted_data": doc.extracted_data,
                "classification_status": doc.classification_status
            })

        research_dict = None
        if research:
            research_dict = {
                "news": json.loads(research.news) if research.news else [],
                "legal": json.loads(research.legal) if research.legal else [],
                "market_sentiment": json.loads(research.market_sentiment) if research.market_sentiment else {},
                "sector_analysis": research.sector_analysis,
                "key_risks": json.loads(research.key_risks) if research.key_risks else []
            }

        rec_dict = None
        if rec:
            rec_dict = {
                "decision": rec.decision,
                "risk_score": rec.risk_score,
                "confidence": rec.confidence,
                "key_metrics": json.loads(rec.key_metrics) if rec.key_metrics else {},
                "reasoning": json.loads(rec.reasoning) if rec.reasoning else [],
                "conditions": json.loads(rec.conditions) if rec.conditions else []
            }

        swot_dict = None
        if swot:
            swot_dict = {
                "strengths": json.loads(swot.strengths) if swot.strengths else [],
                "weaknesses": json.loads(swot.weaknesses) if swot.weaknesses else [],
                "opportunities": json.loads(swot.opportunities) if swot.opportunities else [],
                "threats": json.loads(swot.threats) if swot.threats else []
            }

        report_data = build_report(entity_dict, loan_dict, docs_list, research_dict, rec_dict, swot_dict)

        # Save to DB
        report_record = models.Report(
            entity_id=entity_id,
            report_data=json.dumps(report_data)
        )
        db.add(report_record)
        db.commit()
        db.refresh(report_record)

        return {
            "id": report_record.id,
            "entity_id": entity_id,
            "report_data": report_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/entity/{entity_id}/report", tags=["Stage 4: Analysis"])
def get_report(entity_id: int, db: Session = Depends(get_db)):
    """Get the latest report for an entity."""
    report = (
        db.query(models.Report)
        .filter(models.Report.entity_id == entity_id)
        .order_by(models.Report.id.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="No report found. Generate a report first.")

    return {
        "id": report.id,
        "entity_id": entity_id,
        "report_data": json.loads(report.report_data) if report.report_data else {}
    }


@app.get("/entity/{entity_id}/report/download", tags=["Stage 4: Analysis"])
def download_report(entity_id: int, db: Session = Depends(get_db)):
    """Download the credit assessment report as a PDF."""
    report = (
        db.query(models.Report)
        .filter(models.Report.entity_id == entity_id)
        .order_by(models.Report.id.desc())
        .first()
    )
    if not report or not report.report_data:
        raise HTTPException(status_code=404, detail="No report found. Generate a report first.")

    try:
        from app.services.report_builder import generate_pdf_report

        report_data = json.loads(report.report_data)
        pdf_path = generate_pdf_report(report_data, entity_id)

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"credit_report_entity_{entity_id}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_mock_extraction(category: str, schema: list) -> list:
    """Return mock extraction data for demo purposes."""
    if "Balance Sheet" in category:
        return [
            {"line_item": "Total Assets", "fy_current": "12450.50", "fy_previous": "10820.30", "fy_two_years_ago": "9340.00"},
            {"line_item": "Total Equity", "fy_current": "3200.00", "fy_previous": "2850.00", "fy_two_years_ago": "2500.00"},
            {"line_item": "Total Borrowings", "fy_current": "7800.50", "fy_previous": "6900.00", "fy_two_years_ago": "5900.00"},
            {"line_item": "Current Assets", "fy_current": "4500.00", "fy_previous": "4100.00", "fy_two_years_ago": "3600.00"},
            {"line_item": "Current Liabilities", "fy_current": "3100.00", "fy_previous": "2800.00", "fy_two_years_ago": "2500.00"},
        ]
    elif "Profit" in category or "P&L" in category:
        return [
            {"line_item": "Total Revenue", "fy_current": "4250.00", "fy_previous": "3680.00", "fy_two_years_ago": "3100.00"},
            {"line_item": "Operating Expenses", "fy_current": "3100.00", "fy_previous": "2750.00", "fy_two_years_ago": "2300.00"},
            {"line_item": "EBITDA", "fy_current": "1150.00", "fy_previous": "930.00", "fy_two_years_ago": "800.00"},
            {"line_item": "Net Profit", "fy_current": "620.00", "fy_previous": "510.00", "fy_two_years_ago": "420.00"},
            {"line_item": "EPS", "fy_current": "12.40", "fy_previous": "10.20", "fy_two_years_ago": "8.40"},
        ]
    elif "ALM" in category:
        return [
            {"maturity_bucket": "1-7 days", "assets_amount": "1200.00", "liabilities_amount": "1500.00", "gap": "-300.00", "cumulative_gap": "-300.00"},
            {"maturity_bucket": "8-14 days", "assets_amount": "800.00", "liabilities_amount": "600.00", "gap": "200.00", "cumulative_gap": "-100.00"},
            {"maturity_bucket": "15-30 days", "assets_amount": "1500.00", "liabilities_amount": "1200.00", "gap": "300.00", "cumulative_gap": "200.00"},
        ]
    else:
        # Generic mock data
        return [{"field": f.get("field_name", "item"), "value": "Sample Value"} for f in schema[:5]]
