"""CreditLens - AI-Powered Enterprise Credit Underwriting Platform
Main FastAPI application with all API endpoints for 4 stages.
"""
import os
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db, create_tables
from app import models
from app.schemas import (
    EntityCreate, EntityResponse,
    LoanDetailCreate, LoanDetailResponse,
    DocumentResponse,
    ClassifyConfirmRequest,
    ExtractionUpdateRequest,
    SchemaUpdateRequest,
)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CreditLens API",
    description="AI-Powered Enterprise Credit Underwriting Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")


@app.on_event("startup")
async def startup_event():
    """Initialize database and directories on startup."""
    create_tables()
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    logger.info("CreditLens API started successfully")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CreditLens API", "version": "1.0.0"}


# ============================================================
# STAGE 1: Entity Onboarding
# ============================================================

@app.post("/entity", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(entity_data: EntityCreate, db: Session = Depends(get_db)):
    """Create a new entity record."""
    try:
        entity = models.Entity(**entity_data.model_dump())
        db.add(entity)
        db.commit()
        db.refresh(entity)
        logger.info(f"Created entity: {entity.id} - {entity.company_name}")
        return entity
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create entity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create entity: {str(e)}")


@app.get("/entity/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Retrieve entity details by ID."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return entity


@app.put("/entity/{entity_id}", response_model=EntityResponse)
def update_entity(entity_id: int, entity_data: EntityCreate, db: Session = Depends(get_db)):
    """Update entity details."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    for key, value in entity_data.model_dump().items():
        setattr(entity, key, value)
    entity.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(entity)
    return entity


@app.post("/entity/{entity_id}/loan", response_model=LoanDetailResponse, status_code=status.HTTP_201_CREATED)
def create_loan(entity_id: int, loan_data: LoanDetailCreate, db: Session = Depends(get_db)):
    """Add loan details linked to an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    try:
        loan = models.LoanDetail(entity_id=entity_id, **loan_data.model_dump())
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create loan details: {str(e)}")


@app.get("/entity/{entity_id}/loan", response_model=List[LoanDetailResponse])
def get_loans(entity_id: int, db: Session = Depends(get_db)):
    """Get all loan details for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return entity.loan_details


# ============================================================
# STAGE 2: Document Ingestion
# ============================================================

def get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext == 'pdf':
        return 'pdf'
    elif ext in ['xlsx', 'xls']:
        return 'excel'
    elif ext in ['png', 'jpg', 'jpeg']:
        return 'image'
    else:
        return 'unknown'


@app.post("/entity/{entity_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    entity_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    try:
        # Create upload directory for entity
        entity_upload_dir = Path(UPLOAD_DIR) / str(entity_id)
        entity_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = entity_upload_dir / safe_filename
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        file_size = file_path.stat().st_size
        file_type = get_file_type(file.filename)
        
        # Create document record
        document = models.Document(
            entity_id=entity_id,
            filename=safe_filename,
            original_filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            upload_path=str(file_path),
            classification_status="uploaded"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Uploaded document: {document.id} for entity {entity_id}")
        return document
    
    except Exception as e:
        db.rollback()
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")


@app.get("/entity/{entity_id}/documents", response_model=List[DocumentResponse])
def get_documents(entity_id: int, db: Session = Depends(get_db)):
    """Get all documents for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return entity.documents


@app.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and its file."""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    try:
        # Delete file from disk
        if document.upload_path and Path(document.upload_path).exists():
            Path(document.upload_path).unlink()
        
        db.delete(document)
        db.commit()
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


# ============================================================
# STAGE 3: Automated Extraction & Schema Mapping
# ============================================================

@app.post("/documents/{document_id}/classify")
def classify_document(document_id: int, db: Session = Depends(get_db)):
    """Classify a document using AI."""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    try:
        from app.services.document_classifier import classify_document as classify
        
        result = classify(document.upload_path, document.file_type)
        
        # Update document record
        document.document_category = result.get("category")
        document.classification_confidence = result.get("confidence")
        document.classification_status = "classified"
        db.commit()
        db.refresh(document)
        
        return {
            "document_id": document_id,
            "category": result.get("category"),
            "confidence": result.get("confidence"),
            "reasoning": result.get("reasoning", "")
        }
    except Exception as e:
        logger.error(f"Classification failed for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.post("/entity/{entity_id}/classify-all")
def classify_all_documents(entity_id: int, db: Session = Depends(get_db)):
    """Classify all unclassified documents for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    from app.services.document_classifier import classify_document as classify
    
    results = []
    for document in entity.documents:
        if document.classification_status == "uploaded":
            try:
                result = classify(document.upload_path, document.file_type)
                document.document_category = result.get("category")
                document.classification_confidence = result.get("confidence")
                document.classification_status = "classified"
                results.append({
                    "document_id": document.id,
                    "filename": document.original_filename,
                    "category": result.get("category"),
                    "confidence": result.get("confidence"),
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "document_id": document.id,
                    "filename": document.original_filename,
                    "status": "failed",
                    "error": str(e)
                })
    
    db.commit()
    return {"results": results, "total": len(results)}


@app.put("/documents/{document_id}/classify/confirm")
def confirm_classification(
    document_id: int,
    request: ClassifyConfirmRequest,
    db: Session = Depends(get_db)
):
    """Confirm or update document classification."""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    if request.category:
        document.document_category = request.category
    document.classification_status = request.status
    db.commit()
    db.refresh(document)
    
    return {
        "document_id": document_id,
        "category": document.document_category,
        "status": document.classification_status,
        "message": f"Classification {request.status} successfully"
    }


@app.post("/documents/{document_id}/extract")
def extract_document(document_id: int, db: Session = Depends(get_db)):
    """Extract structured data from a document using AI."""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    if not document.document_category:
        raise HTTPException(status_code=400, detail="Document must be classified before extraction")
    
    try:
        from app.services.document_parser import parse_document
        from app.services.schema_mapper import get_default_schema
        
        # Get document content
        parsed = parse_document(document.upload_path, document.file_type)
        doc_content = parsed.get("text", "")
        
        # Get schema
        schema = json.loads(document.extraction_schema) if document.extraction_schema else get_default_schema(document.document_category)
        schema_json = json.dumps(schema, indent=2)
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_api_key:
            extracted = _extract_with_gemini(doc_content, schema_json, document.document_category, gemini_api_key)
        else:
            extracted = _mock_extraction(document.document_category, schema)
        
        # Store extracted data
        document.extracted_data = json.dumps(extracted)
        db.commit()
        db.refresh(document)
        
        return {
            "document_id": document_id,
            "category": document.document_category,
            "extracted_data": extracted,
            "schema": schema
        }
    except Exception as e:
        logger.error(f"Extraction failed for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


def _extract_with_gemini(content: str, schema_json: str, category: str, api_key: str) -> list:
    """Extract data using Gemini AI."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Truncate content if too long
        if len(content) > 15000:
            content = content[:15000] + "...[truncated]"
        
        prompt = f"""You are a financial data extraction engine. Extract structured data from this {category} document according to the following schema:

Schema:
{schema_json}

Return ONLY a valid JSON array of objects matching the schema fields. Be precise with numbers — preserve exact values from the document. If a value is not found, use null.

Document content:
{content}"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    except Exception as e:
        logger.error(f"Gemini extraction failed: {e}")
        return []


def _mock_extraction(category: str, schema: list) -> list:
    """Return mock extraction data."""
    mock_data = {
        "ALM (Asset-Liability Management)": [
            {"maturity_bucket": "0-30 days", "assets_amount": 1250.5, "liabilities_amount": 980.3, "gap": 270.2, "cumulative_gap": 270.2},
            {"maturity_bucket": "31-90 days", "assets_amount": 2100.0, "liabilities_amount": 1850.5, "gap": 249.5, "cumulative_gap": 519.7},
            {"maturity_bucket": "91-180 days", "assets_amount": 3500.0, "liabilities_amount": 3200.0, "gap": 300.0, "cumulative_gap": 819.7},
            {"maturity_bucket": "181 days-1 year", "assets_amount": 4200.0, "liabilities_amount": 4100.0, "gap": 100.0, "cumulative_gap": 919.7},
            {"maturity_bucket": "1-3 years", "assets_amount": 8500.0, "liabilities_amount": 7200.0, "gap": 1300.0, "cumulative_gap": 2219.7},
        ],
        "Shareholding Pattern": [
            {"shareholder_name": "Promoter Group", "holding_percentage": 52.5, "share_count": 52500000, "shareholder_category": "Promoter"},
            {"shareholder_name": "Foreign Institutional Investors", "holding_percentage": 18.3, "share_count": 18300000, "shareholder_category": "FII"},
            {"shareholder_name": "Domestic Institutional Investors", "holding_percentage": 12.7, "share_count": 12700000, "shareholder_category": "DII"},
            {"shareholder_name": "Public", "holding_percentage": 16.5, "share_count": 16500000, "shareholder_category": "Public"},
        ],
        "Borrowing Profile": [
            {"lender_name": "State Bank of India", "facility_type": "Term Loan", "sanctioned_amount": 500.0, "outstanding_amount": 350.0, "interest_rate": 9.5, "maturity_date": "2026-03-31"},
            {"lender_name": "HDFC Bank", "facility_type": "Working Capital", "sanctioned_amount": 200.0, "outstanding_amount": 180.0, "interest_rate": 10.25, "maturity_date": "2025-09-30"},
            {"lender_name": "ICICI Bank", "facility_type": "NCD", "sanctioned_amount": 300.0, "outstanding_amount": 300.0, "interest_rate": 9.75, "maturity_date": "2027-06-30"},
        ],
        "Annual Report - Balance Sheet": [
            {"line_item": "Total Assets", "fy_current": 15000.0, "fy_previous": 12500.0, "fy_two_years_ago": 10200.0},
            {"line_item": "Net Worth", "fy_current": 3500.0, "fy_previous": 3100.0, "fy_two_years_ago": 2800.0},
            {"line_item": "Total Borrowings", "fy_current": 8500.0, "fy_previous": 7200.0, "fy_two_years_ago": 5900.0},
            {"line_item": "Current Assets", "fy_current": 4200.0, "fy_previous": 3500.0, "fy_two_years_ago": 2900.0},
            {"line_item": "Fixed Assets", "fy_current": 2800.0, "fy_previous": 2600.0, "fy_two_years_ago": 2300.0},
        ],
        "Annual Report - Profit & Loss": [
            {"line_item": "Total Revenue", "fy_current": 5200.0, "fy_previous": 4500.0, "fy_two_years_ago": 3800.0},
            {"line_item": "Net Interest Income", "fy_current": 1850.0, "fy_previous": 1620.0, "fy_two_years_ago": 1380.0},
            {"line_item": "Operating Expenses", "fy_current": 980.0, "fy_previous": 850.0, "fy_two_years_ago": 720.0},
            {"line_item": "EBITDA", "fy_current": 870.0, "fy_previous": 770.0, "fy_two_years_ago": 660.0},
            {"line_item": "Net Profit", "fy_current": 520.0, "fy_previous": 440.0, "fy_two_years_ago": 380.0},
        ],
        "Annual Report - Cash Flow": [
            {"line_item": "Cash from Operations", "fy_current": 680.0, "fy_previous": 590.0, "fy_two_years_ago": 490.0},
            {"line_item": "Cash from Investing", "fy_current": -420.0, "fy_previous": -380.0, "fy_two_years_ago": -310.0},
            {"line_item": "Cash from Financing", "fy_current": 150.0, "fy_previous": 120.0, "fy_two_years_ago": 90.0},
            {"line_item": "Net Cash Flow", "fy_current": 410.0, "fy_previous": 330.0, "fy_two_years_ago": 270.0},
        ],
        "Portfolio Performance Data": [
            {"segment": "Home Loans", "aum": 5200.0, "npas": 62.4, "provision_coverage": 68.5, "yield_percentage": 9.2},
            {"segment": "Business Loans", "aum": 3800.0, "npas": 114.0, "provision_coverage": 65.0, "yield_percentage": 12.5},
            {"segment": "Vehicle Finance", "aum": 2100.0, "npas": 42.0, "provision_coverage": 72.0, "yield_percentage": 11.8},
            {"segment": "Gold Loans", "aum": 1500.0, "npas": 15.0, "provision_coverage": 85.0, "yield_percentage": 13.5},
        ],
    }
    
    return mock_data.get(category, [{"line_item": "Sample Data", "fy_current": 100.0, "fy_previous": 90.0}])


@app.get("/documents/{document_id}/extraction")
def get_extraction(document_id: int, db: Session = Depends(get_db)):
    """Get extracted data for a document."""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    extracted = None
    if document.extracted_data:
        try:
            extracted = json.loads(document.extracted_data)
        except json.JSONDecodeError:
            extracted = None
    
    return {
        "document_id": document_id,
        "category": document.document_category,
        "extracted_data": extracted,
        "schema": json.loads(document.extraction_schema) if document.extraction_schema else None
    }


@app.put("/documents/{document_id}/extraction")
def update_extraction(
    document_id: int,
    request: ExtractionUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update extracted data (human corrections)."""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    document.extracted_data = json.dumps(request.extracted_data)
    db.commit()
    
    return {"document_id": document_id, "message": "Extraction data updated successfully"}


@app.get("/entity/{entity_id}/schema")
def get_entity_schema(entity_id: int, db: Session = Depends(get_db)):
    """Get extraction schemas for an entity."""
    from app.services.schema_mapper import get_all_default_schemas
    
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    # Check if any documents have custom schemas
    custom_schemas = {}
    for doc in entity.documents:
        if doc.extraction_schema and doc.document_category:
            try:
                custom_schemas[doc.document_category] = json.loads(doc.extraction_schema)
            except json.JSONDecodeError:
                pass
    
    default_schemas = get_all_default_schemas()
    merged = {**default_schemas, **custom_schemas}
    
    return {"entity_id": entity_id, "schemas": merged}


@app.put("/entity/{entity_id}/schema")
def update_entity_schema(
    entity_id: int,
    request: SchemaUpdateRequest,
    db: Session = Depends(get_db)
):
    """Save custom schema definitions for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    # Update schema for all documents of matching categories
    for doc in entity.documents:
        if doc.document_category and doc.document_category in request.schemas:
            doc.extraction_schema = json.dumps(request.schemas[doc.document_category])
    
    db.commit()
    return {"entity_id": entity_id, "message": "Schema updated successfully", "schemas": request.schemas}


@app.post("/entity/{entity_id}/extract-all")
def extract_all_documents(entity_id: int, db: Session = Depends(get_db)):
    """Extract data from all classified documents."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    from app.services.document_parser import parse_document
    from app.services.schema_mapper import get_default_schema
    
    results = []
    for document in entity.documents:
        if document.classification_status in ["classified", "confirmed"] and not document.extracted_data:
            try:
                parsed = parse_document(document.upload_path, document.file_type)
                doc_content = parsed.get("text", "")
                schema = json.loads(document.extraction_schema) if document.extraction_schema else get_default_schema(document.document_category)
                schema_json = json.dumps(schema, indent=2)
                
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if gemini_api_key:
                    extracted = _extract_with_gemini(doc_content, schema_json, document.document_category, gemini_api_key)
                else:
                    extracted = _mock_extraction(document.document_category, schema)
                
                document.extracted_data = json.dumps(extracted)
                results.append({"document_id": document.id, "status": "success", "rows_extracted": len(extracted)})
            except Exception as e:
                results.append({"document_id": document.id, "status": "failed", "error": str(e)})
    
    db.commit()
    return {"results": results, "total": len(results)}


# ============================================================
# STAGE 4: Secondary Research & Analysis
# ============================================================

@app.post("/entity/{entity_id}/secondary-research")
def run_secondary_research(entity_id: int, db: Session = Depends(get_db)):
    """Run secondary research for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    try:
        from app.services.secondary_research import perform_secondary_research
        
        research_data = perform_secondary_research(
            company_name=entity.company_name,
            sector=entity.sector or "Financial Services",
            cin=entity.cin
        )
        
        # Store or update research record
        existing = db.query(models.SecondaryResearch).filter(
            models.SecondaryResearch.entity_id == entity_id
        ).first()
        
        if existing:
            existing.news = json.dumps(research_data.get("news", []))
            existing.legal = json.dumps(research_data.get("legal", []))
            existing.market_sentiment = json.dumps(research_data.get("market_sentiment", {}))
            existing.sector_analysis = research_data.get("sector_analysis", "")
            existing.key_risks = json.dumps(research_data.get("key_risks", []))
            research_record = existing
        else:
            research_record = models.SecondaryResearch(
                entity_id=entity_id,
                news=json.dumps(research_data.get("news", [])),
                legal=json.dumps(research_data.get("legal", [])),
                market_sentiment=json.dumps(research_data.get("market_sentiment", {})),
                sector_analysis=research_data.get("sector_analysis", ""),
                key_risks=json.dumps(research_data.get("key_risks", []))
            )
            db.add(research_record)
        
        db.commit()
        db.refresh(research_record)
        
        return {
            "id": research_record.id,
            "entity_id": entity_id,
            "news": research_data.get("news", []),
            "legal": research_data.get("legal", []),
            "market_sentiment": research_data.get("market_sentiment", {}),
            "sector_analysis": research_data.get("sector_analysis", ""),
            "key_risks": research_data.get("key_risks", []),
            "created_at": research_record.created_at
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Secondary research failed: {e}")
        raise HTTPException(status_code=500, detail=f"Secondary research failed: {str(e)}")


@app.get("/entity/{entity_id}/secondary-research")
def get_secondary_research(entity_id: int, db: Session = Depends(get_db)):
    """Get stored secondary research results."""
    research = db.query(models.SecondaryResearch).filter(
        models.SecondaryResearch.entity_id == entity_id
    ).first()
    
    if not research:
        raise HTTPException(status_code=404, detail="No secondary research found. Run research first.")
    
    return {
        "id": research.id,
        "entity_id": entity_id,
        "news": json.loads(research.news) if research.news else [],
        "legal": json.loads(research.legal) if research.legal else [],
        "market_sentiment": json.loads(research.market_sentiment) if research.market_sentiment else {},
        "sector_analysis": research.sector_analysis or "",
        "key_risks": json.loads(research.key_risks) if research.key_risks else [],
        "created_at": research.created_at
    }


@app.post("/entity/{entity_id}/recommendation")
def generate_recommendation(entity_id: int, db: Session = Depends(get_db)):
    """Generate loan recommendation using AI."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    try:
        from app.services.risk_engine import generate_recommendation as gen_rec
        
        # Gather data
        entity_dict = {c.name: getattr(entity, c.name) for c in entity.__table__.columns}
        loan_dict = None
        if entity.loan_details:
            loan = entity.loan_details[0]
            loan_dict = {c.name: getattr(loan, c.name) for c in loan.__table__.columns}
        
        extracted_data = []
        for doc in entity.documents:
            if doc.extracted_data:
                try:
                    extracted_data.append({
                        "category": doc.document_category,
                        "data": json.loads(doc.extracted_data)
                    })
                except json.JSONDecodeError:
                    pass
        
        secondary_research = None
        research_record = db.query(models.SecondaryResearch).filter(
            models.SecondaryResearch.entity_id == entity_id
        ).first()
        if research_record:
            secondary_research = {
                "news": json.loads(research_record.news) if research_record.news else [],
                "legal": json.loads(research_record.legal) if research_record.legal else [],
                "market_sentiment": json.loads(research_record.market_sentiment) if research_record.market_sentiment else {},
                "sector_analysis": research_record.sector_analysis,
                "key_risks": json.loads(research_record.key_risks) if research_record.key_risks else []
            }
        
        rec_data = gen_rec(entity_dict, loan_dict, extracted_data, secondary_research)
        
        # Store recommendation
        existing = db.query(models.Recommendation).filter(
            models.Recommendation.entity_id == entity_id
        ).first()
        
        if existing:
            existing.decision = rec_data.get("decision", "CONDITIONAL_APPROVE")
            existing.risk_score = rec_data.get("risk_score")
            existing.confidence = rec_data.get("confidence")
            existing.key_metrics = json.dumps(rec_data.get("key_metrics", {}))
            existing.reasoning = json.dumps(rec_data.get("reasoning", []))
            existing.conditions = json.dumps(rec_data.get("conditions", []))
            rec_record = existing
        else:
            rec_record = models.Recommendation(
                entity_id=entity_id,
                decision=rec_data.get("decision", "CONDITIONAL_APPROVE"),
                risk_score=rec_data.get("risk_score"),
                confidence=rec_data.get("confidence"),
                key_metrics=json.dumps(rec_data.get("key_metrics", {})),
                reasoning=json.dumps(rec_data.get("reasoning", [])),
                conditions=json.dumps(rec_data.get("conditions", []))
            )
            db.add(rec_record)
        
        db.commit()
        db.refresh(rec_record)
        
        return {
            "id": rec_record.id,
            "entity_id": entity_id,
            "decision": rec_data.get("decision"),
            "risk_score": rec_data.get("risk_score"),
            "confidence": rec_data.get("confidence"),
            "key_metrics": rec_data.get("key_metrics", {}),
            "reasoning": rec_data.get("reasoning", []),
            "conditions": rec_data.get("conditions", []),
            "created_at": rec_record.created_at
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.get("/entity/{entity_id}/recommendation")
def get_recommendation(entity_id: int, db: Session = Depends(get_db)):
    """Get stored recommendation."""
    rec = db.query(models.Recommendation).filter(
        models.Recommendation.entity_id == entity_id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="No recommendation found. Generate one first.")
    
    return {
        "id": rec.id,
        "entity_id": entity_id,
        "decision": rec.decision,
        "risk_score": rec.risk_score,
        "confidence": rec.confidence,
        "key_metrics": json.loads(rec.key_metrics) if rec.key_metrics else {},
        "reasoning": json.loads(rec.reasoning) if rec.reasoning else [],
        "conditions": json.loads(rec.conditions) if rec.conditions else [],
        "created_at": rec.created_at
    }


@app.post("/entity/{entity_id}/swot")
def generate_swot(entity_id: int, db: Session = Depends(get_db)):
    """Generate SWOT analysis."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    try:
        from app.services.swot_generator import generate_swot as gen_swot
        
        entity_dict = {c.name: getattr(entity, c.name) for c in entity.__table__.columns}
        
        extracted_data = []
        for doc in entity.documents:
            if doc.extracted_data:
                try:
                    extracted_data.append(json.loads(doc.extracted_data))
                except json.JSONDecodeError:
                    pass
        
        research_record = db.query(models.SecondaryResearch).filter(
            models.SecondaryResearch.entity_id == entity_id
        ).first()
        secondary_research = None
        if research_record:
            secondary_research = {
                "sector_analysis": research_record.sector_analysis,
                "key_risks": json.loads(research_record.key_risks) if research_record.key_risks else [],
                "market_sentiment": json.loads(research_record.market_sentiment) if research_record.market_sentiment else {}
            }
        
        swot_data = gen_swot(entity_dict, extracted_data, secondary_research)
        
        # Store SWOT
        existing = db.query(models.SwotAnalysis).filter(
            models.SwotAnalysis.entity_id == entity_id
        ).first()
        
        if existing:
            existing.strengths = json.dumps(swot_data.get("strengths", []))
            existing.weaknesses = json.dumps(swot_data.get("weaknesses", []))
            existing.opportunities = json.dumps(swot_data.get("opportunities", []))
            existing.threats = json.dumps(swot_data.get("threats", []))
            swot_record = existing
        else:
            swot_record = models.SwotAnalysis(
                entity_id=entity_id,
                strengths=json.dumps(swot_data.get("strengths", [])),
                weaknesses=json.dumps(swot_data.get("weaknesses", [])),
                opportunities=json.dumps(swot_data.get("opportunities", [])),
                threats=json.dumps(swot_data.get("threats", []))
            )
            db.add(swot_record)
        
        db.commit()
        db.refresh(swot_record)
        
        return {
            "id": swot_record.id,
            "entity_id": entity_id,
            "strengths": swot_data.get("strengths", []),
            "weaknesses": swot_data.get("weaknesses", []),
            "opportunities": swot_data.get("opportunities", []),
            "threats": swot_data.get("threats", []),
            "created_at": swot_record.created_at
        }
    except Exception as e:
        db.rollback()
        logger.error(f"SWOT generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"SWOT generation failed: {str(e)}")


@app.get("/entity/{entity_id}/swot")
def get_swot(entity_id: int, db: Session = Depends(get_db)):
    """Get stored SWOT analysis."""
    swot = db.query(models.SwotAnalysis).filter(
        models.SwotAnalysis.entity_id == entity_id
    ).first()
    
    if not swot:
        raise HTTPException(status_code=404, detail="No SWOT analysis found. Generate one first.")
    
    return {
        "id": swot.id,
        "entity_id": entity_id,
        "strengths": json.loads(swot.strengths) if swot.strengths else [],
        "weaknesses": json.loads(swot.weaknesses) if swot.weaknesses else [],
        "opportunities": json.loads(swot.opportunities) if swot.opportunities else [],
        "threats": json.loads(swot.threats) if swot.threats else [],
        "created_at": swot.created_at
    }


@app.post("/entity/{entity_id}/report")
def generate_report(entity_id: int, db: Session = Depends(get_db)):
    """Generate the final credit assessment report."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    try:
        from app.services.report_builder import compile_report
        
        entity_dict = {c.name: getattr(entity, c.name) for c in entity.__table__.columns}
        
        loan_dict = None
        if entity.loan_details:
            loan = entity.loan_details[0]
            loan_dict = {c.name: getattr(loan, c.name) for c in loan.__table__.columns}
        
        documents_list = []
        for doc in entity.documents:
            doc_dict = {c.name: getattr(doc, c.name) for c in doc.__table__.columns}
            documents_list.append(doc_dict)
        
        research_record = db.query(models.SecondaryResearch).filter(
            models.SecondaryResearch.entity_id == entity_id
        ).first()
        secondary_research = None
        if research_record:
            secondary_research = {
                "news": json.loads(research_record.news) if research_record.news else [],
                "legal": json.loads(research_record.legal) if research_record.legal else [],
                "market_sentiment": json.loads(research_record.market_sentiment) if research_record.market_sentiment else {},
                "sector_analysis": research_record.sector_analysis,
                "key_risks": json.loads(research_record.key_risks) if research_record.key_risks else []
            }
        
        rec_record = db.query(models.Recommendation).filter(
            models.Recommendation.entity_id == entity_id
        ).first()
        recommendation = None
        if rec_record:
            recommendation = {
                "decision": rec_record.decision,
                "risk_score": rec_record.risk_score,
                "confidence": rec_record.confidence,
                "key_metrics": json.loads(rec_record.key_metrics) if rec_record.key_metrics else {},
                "reasoning": json.loads(rec_record.reasoning) if rec_record.reasoning else [],
                "conditions": json.loads(rec_record.conditions) if rec_record.conditions else []
            }
        
        swot_record = db.query(models.SwotAnalysis).filter(
            models.SwotAnalysis.entity_id == entity_id
        ).first()
        swot = None
        if swot_record:
            swot = {
                "strengths": json.loads(swot_record.strengths) if swot_record.strengths else [],
                "weaknesses": json.loads(swot_record.weaknesses) if swot_record.weaknesses else [],
                "opportunities": json.loads(swot_record.opportunities) if swot_record.opportunities else [],
                "threats": json.loads(swot_record.threats) if swot_record.threats else []
            }
        
        report_data = compile_report(
            entity=entity_dict,
            loan=loan_dict,
            documents=documents_list,
            secondary_research=secondary_research,
            recommendation=recommendation,
            swot=swot
        )
        
        # Store report
        existing = db.query(models.Report).filter(
            models.Report.entity_id == entity_id
        ).first()
        
        if existing:
            existing.report_data = json.dumps(report_data, default=str)
            report_record = existing
        else:
            report_record = models.Report(
                entity_id=entity_id,
                report_data=json.dumps(report_data, default=str)
            )
            db.add(report_record)
        
        db.commit()
        db.refresh(report_record)
        
        return {
            "id": report_record.id,
            "entity_id": entity_id,
            "report_data": report_data,
            "created_at": report_record.created_at
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/entity/{entity_id}/report")
def get_report(entity_id: int, db: Session = Depends(get_db)):
    """Get stored report."""
    report = db.query(models.Report).filter(
        models.Report.entity_id == entity_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No report found. Generate one first.")
    
    return {
        "id": report.id,
        "entity_id": entity_id,
        "report_data": json.loads(report.report_data) if report.report_data else {},
        "created_at": report.created_at
    }


@app.get("/entity/{entity_id}/report/download")
def download_report(entity_id: int, db: Session = Depends(get_db)):
    """Download the report as a PDF."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    report = db.query(models.Report).filter(
        models.Report.entity_id == entity_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No report found. Generate report first.")
    
    try:
        from app.services.report_builder import generate_pdf_report
        
        report_data = json.loads(report.report_data) if report.report_data else {}
        pdf_bytes = generate_pdf_report(report_data, entity.company_name)
        
        # Save PDF to disk
        pdf_path = Path(REPORTS_DIR) / f"report_{entity_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="CreditLens_Report_{entity.company_name.replace(" ", "_")}.pdf"'
            }
        )
    except Exception as e:
        logger.error(f"PDF download failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
