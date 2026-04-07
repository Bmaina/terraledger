# TerraLedger — GitHub \& Deployment Guide

## 1\. Push to GitHub

```bash
cd TerraLedger

# Initialize git
git init
git add .
git commit -m "feat: TerraLedger MVP — EUDR compliance platform with GeoAI scoring"

# Create repo on GitHub (via CLI or web), then:
git remote add origin https://github.com/YOUR\_USERNAME/terraledger.git
git branch -M main
git push -u origin main
```

\---

## 2\. Local Development (No Docker)

### Step 1 — PostgreSQL + PostGIS

```bash
# macOS
brew install postgresql postgis
createdb terraledger\_db
psql terraledger\_db -c "CREATE EXTENSION postgis;"
psql terraledger\_db -c "CREATE USER terraledger WITH PASSWORD 'terraledger';"
psql terraledger\_db -c "GRANT ALL ON DATABASE terraledger\_db TO terraledger;"

# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib postgis
sudo -u postgres createdb terraledger\_db
sudo -u postgres psql -c "CREATE EXTENSION postgis;" terraledger\_db
sudo -u postgres psql -c "CREATE USER terraledger WITH PASSWORD 'terraledger';"
sudo -u postgres psql -c "GRANT ALL ON DATABASE terraledger\_db TO terraledger;"
```

### Step 2 — Backend

```bash
cd backend
python -m venv venv \&\& source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Edit DATABASE\_URL if needed
alembic upgrade head          # Run migrations
python scripts/seed\_demo.py   # Load East Africa demo data
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Step 3 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: http://localhost:5173
Login: demo@terraledger.io / TerraDemo2026

\---

## 3\. Full Stack via Docker (Recommended for demos)

```bash
# From the root terraledger/ directory
docker compose up --build

# First run takes \~3 minutes (builds images, runs migrations, seeds data)
# Dashboard: http://localhost:5173
# API docs:  http://localhost:8000/docs
```

\---

## 4\. Deploy to Cloud (Investor Demo URL)

### Option A — Railway (fastest, \~5 min)

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

Set env vars in Railway dashboard: DATABASE\_URL, SECRET\_KEY, SATELLITE\_MODE=demo

### Option B — Render

* Connect GitHub repo to render.com
* Add a PostgreSQL service (free tier)
* Add a Web Service pointing to backend/
* Set BUILD\_COMMAND: `pip install -r requirements.txt`
* Set START\_COMMAND: `alembic upgrade head \&\& python scripts/seed\_demo.py \&\& uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option C — Google Cloud Run (production-grade)

```bash
gcloud builds submit --tag gcr.io/YOUR\_PROJECT/terraledger-backend ./backend
gcloud run deploy terraledger-backend \\
  --image gcr.io/YOUR\_PROJECT/terraledger-backend \\
  --platform managed \\
  --region europe-west1 \\
  --set-env-vars DATABASE\_URL=...,SATELLITE\_MODE=demo
```

\---

## 5\. Enabling Live Satellite Data (Google Earth Engine)

1. Register at https://earthengine.google.com
2. Create a service account in Google Cloud Console
3. Download the JSON key file
4. Set in .env:

```
   SATELLITE\_MODE=live
   GEE\_SERVICE\_ACCOUNT=your-sa@project.iam.gserviceaccount.com
   GEE\_KEY\_FILE=/path/to/key.json
   ```

5. Install GEE client: `pip install earthengine-api`

The `score\_parcel()` function in `app/services/satellite.py` automatically
switches to live GEE analysis when SATELLITE\_MODE=live.

\---

## 6\. Investor Demo Checklist

Before showing to investors:

* \[ ] App is live at a public URL (Railway/Render free tier works)
* \[ ] Demo credentials visible on login screen
* \[ ] All 9 parcels visible on map with color-coded risk markers
* \[ ] Generate DDS PDF for the Kenya batch — downloads instantly
* \[ ] Show XAI explanation panel by clicking a parcel marker
* \[ ] API docs at /docs show all endpoints — demonstrates technical depth

Talking points:

* "Each dot is a real GPS location in Kenya, Ethiopia, Uganda, Rwanda"
* "The scoring engine uses the same Sentinel-2 data the EU uses for benchmarking"
* "This PDF is a legally-structured Due Diligence Statement under EU 2023/1115"
* "The chain of custody trail is append-only — immutable audit log"
* "In production mode, we swap the simulation for live Google Earth Engine calls"

