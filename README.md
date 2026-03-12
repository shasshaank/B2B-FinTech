# CreditLens — AI-Powered Enterprise Credit Underwriting Platform

> B2B FinTech Hackathon 2025 | Transforming raw financial data into AI-backed credit decisions

---

## Overview

**CreditLens** is a full-stack web application that automates enterprise credit underwriting for B2B lending. It guides a Credit Analyst through four stages — from entity onboarding to a downloadable PDF report — leveraging Google Gemini AI for document classification, data extraction, market research, and recommendation generation.

---

## Key Features

| Stage | Feature |
|-------|---------|
| **1. Entity Onboarding** | Multi-step form capturing company details (CIN/PAN validated), loan request |
| **2. Document Ingestion** | Drag-and-drop upload for PDFs, Excel, images with category tagging |
| **3. Extraction & Mapping** | AI document classification + confidence scores + human-in-the-loop review + editable extraction tables |
| **4. Analysis & Reporting** | Secondary research (news, legal, market sentiment), risk scoring, SWOT, downloadable PDF report |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Ant Design 5, React Router 6, Recharts, jsPDF |
| Backend | FastAPI, SQLAlchemy, SQLite |
| AI | Google Gemini 2.0 Flash |
| Document Processing | pdfplumber, pandas, pytesseract (OCR), Pillow |
| PDF Generation | fpdf2 |
| Web Scraping | requests, BeautifulSoup4 |

---

## Architecture

```
+--------------------------------------------------------------------+
|                         CreditLens                                 |
|                                                                    |
|  +---------------------+         +-----------------------------+  |
|  |    React Frontend   | --API--> |    FastAPI Backend          |  |
|  |                     |         |                             |  |
|  |  Stage 1: Onboarding|         |  /entity  /loan             |  |
|  |  Stage 2: Ingestion |         |  /documents                 |  |
|  |  Stage 3: Extraction|         |  /classify /extract         |  |
|  |  Stage 4: Analysis  |         |  /recommendation /swot      |  |
|  +---------------------+         +--------------------+--------+  |
|                                                        |           |
|                                 +-----------------------v-------+  |
|                                 |       SQLite Database         |  |
|                                 |  Entity, LoanDetail, Document |  |
|                                 |  SecondaryResearch, Report    |  |
|                                 +-----------------------+-------+  |
|                                                         |           |
|                                 +-----------------------v-------+  |
|                                 |     Google Gemini 2.0 Flash   |  |
|                                 |  Classification, Extraction   |  |
|                                 |  Research, SWOT, Recommend    |  |
|                                 +-------------------------------+  |
+--------------------------------------------------------------------+
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API Key (optional — app works with mock data without it)

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: http://localhost:8000 | Swagger UI: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

Frontend: http://localhost:3000

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | None (mock data) |
| `DATABASE_URL` | SQLite path | `sqlite:///./credit_lens.db` |
| `UPLOAD_DIR` | Upload directory | `./uploads` |
| `REPORTS_DIR` | Reports directory | `./reports` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend URL | `http://localhost:8000` |

---

## API Reference

### Stage 1: Onboarding
- `POST /entity` — Create entity
- `GET /entity/{id}` — Get entity
- `POST /entity/{id}/loan` — Add loan details

### Stage 2: Ingestion
- `POST /entity/{id}/documents` — Upload document
- `GET /entity/{id}/documents` — List documents
- `DELETE /documents/{id}` — Delete document

### Stage 3: Extraction
- `POST /documents/{id}/classify` — AI classify
- `PUT /documents/{id}/classify/confirm` — Confirm/edit classification
- `POST /documents/{id}/extract` — Extract data
- `GET/PUT /documents/{id}/extraction` — Get/update extracted data
- `GET/PUT /entity/{id}/schema` — Get/update schemas

### Stage 4: Analysis
- `POST/GET /entity/{id}/secondary-research` — Run/get research
- `POST/GET /entity/{id}/recommendation` — Generate/get recommendation
- `POST/GET /entity/{id}/swot` — Generate/get SWOT
- `POST/GET /entity/{id}/report` — Generate/get report
- `GET /entity/{id}/report/download` — Download PDF

---

## Gemini API Fallback

All AI services return reasonable mock/demo data when `GEMINI_API_KEY` is not set. The app is fully demonstrable without a Gemini key.

---

## Docker

```bash
cd backend
docker build -t creditlens-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key creditlens-backend
```

---

*Built for B2B FinTech Hackathon 2025 — CreditLens: Intelligent Credit Decisions, Powered by AI*
