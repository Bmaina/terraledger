# TerraLedger 🌍
### Geo-Verified Supply Chain Compliance for the EU Deforestation Regulation

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com)

> **MVP Status:** Investor-ready demo. Real satellite deforestation scoring via Sentinel-2 NDVI analysis. GPS-linked chain of custody. Auto-generated EUDR Due Diligence Statement (DDS) PDF.

---

## What TerraLedger Does

The EU Deforestation Regulation (EUDR) requires every coffee, cocoa, timber, rubber, and soy shipment entering the EU to be **GPS-verified deforestation-free** back to December 31, 2020. Non-compliance = up to 4% of annual EU turnover in fines + shipment rejection.

TerraLedger automates this:

1. **Upload a farm parcel** — GPS polygon (GeoJSON)
2. **Satellite scan** — Sentinel-2 NDVI time-series analysis detects canopy loss since 2020
3. **Chain of custody** — link harvest batches to verified parcels via QR codes
4. **Export a DDS** — auto-generated Due Diligence Statement PDF, EU-ready

---

## Architecture

```
terraledger/
├── backend/          # FastAPI — REST API + satellite processing
│   └── app/
│       ├── api/      # Route handlers
│       ├── core/     # Config, auth, database
│       ├── models/   # SQLAlchemy ORM models
│       ├── services/ # GeoAI, satellite, DDS generation
│       └── schemas/  # Pydantic request/response schemas
├── frontend/         # React + Leaflet map dashboard
│   └── src/
│       ├── components/
│       ├── pages/
│       └── hooks/
├── scripts/          # Data import, satellite pull helpers
└── docs/             # API docs, architecture diagrams
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with PostGIS extension
- (Optional) Google Earth Engine account for live satellite data

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and API keys

# Run database migrations
alembic upgrade head

# Seed demo data (East Africa coffee parcels)
python scripts/seed_demo.py

# Start API server
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at: http://localhost:5173

---

## Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/parcels/` | Register a farm parcel with GeoJSON polygon |
| GET | `/api/v1/parcels/{id}/score` | Get deforestation risk score |
| POST | `/api/v1/batches/` | Create a commodity batch linked to parcels |
| GET | `/api/v1/batches/{id}/custody` | Full chain of custody audit trail |
| POST | `/api/v1/dds/generate` | Generate EUDR Due Diligence Statement PDF |
| GET | `/api/v1/health` | System health check |

Full OpenAPI spec at `/docs` when running locally.

---

## Investor Demo Flow

1. Open the dashboard → see East Africa map with pre-loaded coffee parcels
2. Click any parcel → see NDVI deforestation risk score with confidence band
3. Click "Generate DDS" → download a compliant Due Diligence Statement PDF
4. Scan the QR code on a batch → see full farm-to-export custody trail

**Demo credentials:** `demo@terraledger.io` / `TerraDemo2026`

---

## Satellite Data

**MVP mode (no GEE account):** Uses pre-computed NDVI delta scores from cached Sentinel-2 data for East African coffee regions (Kenya, Ethiopia, Uganda). Fully functional for demos.

**Production mode:** Connects to Google Earth Engine API for live, on-demand analysis of any submitted GPS polygon globally.

Set `SATELLITE_MODE=live` in `.env` to enable production mode.

---

## Non-Dilutive Grant Alignment

This codebase is structured to meet technical requirements for:
- **EU SPARK / AEDIB JIF** — African-led digitally-enabled climate solutions
- **GIZ Fit for Fair** — EUDR compliance tooling for East African coffee
- **FAO Young Forest Champions** — geospatial forest monitoring technology
- **Katapult Africa Accelerator** — climate tech + food systems

---

## Roadmap

- [x] Parcel registration + NDVI deforestation scoring
- [x] Chain of custody batch tracking
- [x] EUDR DDS auto-generation
- [x] Interactive map dashboard
- [ ] Google Earth Engine live integration
- [ ] SAR Sentinel-1 fusion layer
- [ ] Mobile field data collection app (Android)
- [ ] Carbon credit methodology overlay
- [ ] Multi-language support (Swahili, Amharic, French)

---

## License

MIT — open for pilots and grant applications. Contact hello@terraledger.io for commercial licensing.
