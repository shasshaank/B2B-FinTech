# CreditLens — AI-Powered Enterprise Credit Underwriting Platform

> **B2B FinTech Hackathon Project** | Built with FastAPI + React + Google Gemini AI

CreditLens transforms raw, unstructured financial documents into a comprehensive AI-backed credit assessment report. It guides a Credit Analyst through **4 intelligent stages**: Entity Onboarding → Document Ingestion → Extraction & Schema Mapping → Analysis & Reporting.

---

## ✨ Key Features

- 🏢 **Entity Onboarding** — Capture company details (CIN, PAN, sector, financials) and loan requirements
- 📂 **Smart Document Ingestion** — Drag-and-drop upload for PDFs, Excel files, and images with AI auto-classification
- 🤖 **AI Data Extraction** — Google Gemini classifies documents and extracts structured financial data
- 👤 **Human-in-the-Loop** — Approve/edit/reject AI classifications and correct extracted data
- 📊 **Secondary Research** — Automated news scraping + AI-generated market intelligence
- ⚖️ **Risk Assessment** — AI-powered APPROVE/CONDITIONAL_APPROVE/REJECT recommendation with risk scoring
- 🔍 **SWOT Analysis** — AI-generated Strengths, Weaknesses, Opportunities, Threats
- 📄 **PDF Report Generation** — Downloadable professional credit assessment report

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   CreditLens Platform                    │
├─────────────────────────────────────────────────────────┤
│  FRONTEND (React + Ant Design)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Stage 1   │ │Stage 2   │ │Stage 3   │ │Stage 4   │  │
│  │Onboarding│→│Ingestion │→│Extraction│→│Analysis  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│  BACKEND (FastAPI + Python)                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Entity API│ │Doc API   │ │Classify  │ │Research  │  │
│  │Loan API  │ │Upload    │ │Extract   │ │Risk/SWOT │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│               ┌──────────────────────────────────────┐  │
│               │      Google Gemini AI (gemini-2.0-flash) │
│               └──────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  DATABASE: SQLite (SQLAlchemy ORM)                      │
│  Entity → LoanDetail → Document → SecondaryResearch     │
│  Recommendation → SwotAnalysis → Report                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Ant Design 5, React Router 6 |
| Charts | Recharts |
| PDF Export | jsPDF + html2canvas (frontend), fpdf2 (backend) |
| Backend | FastAPI, Python 3.11, Uvicorn |
| Database | SQLite + SQLAlchemy 2.0 |
| AI/ML | Google Gemini 2.0 Flash |
| Document Parsing | pdfplumber (PDF), pandas/openpyxl (Excel), pytesseract (images) |
| Web Scraping | requests + BeautifulSoup4 |
| Containerization | Docker |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- A Google Gemini API key (optional — app works with mock data without it)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Ensure REACT_APP_API_URL=http://localhost:8000

# Start the development server
npm start
```

Frontend runs at: http://localhost:3000

### Docker (Backend)

```bash
cd backend
docker build -t creditlens-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key_here creditlens-backend
```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | (optional — uses mock data) |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./credit_lens.db` |
| `UPLOAD_DIR` | Directory for uploaded files | `./uploads` |
| `REPORTS_DIR` | Directory for generated reports | `./reports` |

### Frontend (`frontend/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API base URL | `http://localhost:8000` |

---

## 📡 API Documentation

### Stage 1: Entity Onboarding
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/entity` | Create entity |
| GET | `/entity/{id}` | Get entity details |
| PUT | `/entity/{id}` | Update entity |
| POST | `/entity/{id}/loan` | Add loan details |
| GET | `/entity/{id}/loan` | Get loan details |

### Stage 2: Document Ingestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/entity/{id}/documents` | Upload document |
| GET | `/entity/{id}/documents` | List documents |
| DELETE | `/documents/{id}` | Delete document |

### Stage 3: Extraction & Classification
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/{id}/classify` | AI classify document |
| POST | `/entity/{id}/classify-all` | Classify all documents |
| PUT | `/documents/{id}/classify/confirm` | Confirm classification |
| POST | `/documents/{id}/extract` | Extract data from document |
| POST | `/entity/{id}/extract-all` | Extract all documents |
| GET | `/documents/{id}/extraction` | Get extracted data |
| PUT | `/documents/{id}/extraction` | Update extracted data |
| GET | `/entity/{id}/schema` | Get extraction schemas |
| PUT | `/entity/{id}/schema` | Update extraction schemas |

### Stage 4: Analysis & Reporting
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/entity/{id}/secondary-research` | Run AI secondary research |
| GET | `/entity/{id}/secondary-research` | Get research results |
| POST | `/entity/{id}/recommendation` | Generate risk recommendation |
| GET | `/entity/{id}/recommendation` | Get recommendation |
| POST | `/entity/{id}/swot` | Generate SWOT analysis |
| GET | `/entity/{id}/swot` | Get SWOT analysis |
| POST | `/entity/{id}/report` | Compile final report |
| GET | `/entity/{id}/report` | Get report |
| GET | `/entity/{id}/report/download` | Download PDF report |

---

## 📁 Project Structure

```
├── frontend/
│   ├── public/index.html
│   └── src/
│       ├── components/
│       │   ├── common/           # Navbar, StepProgress, LoadingSpinner
│       │   ├── onboarding/       # EntityForm, LoanDetailsForm
│       │   ├── ingestion/        # DocumentUpload, DocumentPreview
│       │   ├── extraction/       # ClassificationReview, SchemaEditor, ExtractionResults
│       │   └── analysis/         # SecondaryResearch, RiskAssessment, SwotAnalysis, ReportGenerator
│       ├── pages/                # OnboardingPage, IngestionPage, ExtractionPage, AnalysisPage
│       ├── services/api.js       # Axios API client
│       └── App.jsx               # Root component with stage routing
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app with all endpoints
│   │   ├── database.py           # SQLAlchemy setup
│   │   ├── models.py             # ORM models
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── services/             # AI service modules
│   │   └── utils/                # OCR & text utilities
│   ├── uploads/                  # Uploaded documents (gitignored)
│   ├── reports/                  # Generated PDF reports (gitignored)
│   ├── requirements.txt
│   └── Dockerfile
└── data/sample_documents/        # Sample financial documents
```

---

## 🤖 AI Integration

CreditLens uses **Google Gemini 2.0 Flash** for:

1. **Document Classification** — Identifies document type (ALM, Balance Sheet, P&L, etc.) with confidence score
2. **Data Extraction** — Extracts structured financial data according to configurable schemas
3. **Secondary Research** — Generates market intelligence, news analysis, and risk signals
4. **Risk Assessment** — Produces APPROVE/CONDITIONAL_APPROVE/REJECT with detailed reasoning
5. **SWOT Analysis** — AI-generated strengths, weaknesses, opportunities, threats
6. **Executive Summary** — Professional summary for the final report

> **Note:** If `GEMINI_API_KEY` is not set, all AI features return realistic mock data so the app is fully demonstrable.

---

## 📋 Supported Document Types

| Category | Description | Key Extracted Fields |
|----------|-------------|---------------------|
| ALM | Asset-Liability Management | maturity_bucket, assets, liabilities, gap |
| Shareholding | Shareholding Pattern | shareholder_name, holding_%, category |
| Borrowing Profile | Credit facilities | lender, facility_type, outstanding_amount |
| Annual Report - P&L | Profit & Loss | line_item, fy_current, fy_previous |
| Annual Report - BS | Balance Sheet | line_item, fy_current, fy_previous |
| Annual Report - CF | Cash Flow Statement | line_item, fy_current, fy_previous |
| Portfolio Data | Portfolio Performance | segment, aum, npas, yield |

---

## 🏆 Hackathon Context

Built for a **B2B FinTech Hackathon** demonstrating:
- End-to-end AI integration in financial services
- Human-in-the-loop design for high-stakes decisions
- Multi-modal document processing (PDF + Excel + images)
- Professional credit underwriting workflow automation
- Scalable FastAPI backend with clean React frontend
