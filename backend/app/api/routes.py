from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, get_current_user_email
)
from app.core.config import settings
from app.models.models import User, Parcel, CommodityBatch, BatchParcel, CustodyEvent
from app.schemas.schemas import (
    TokenResponse, UserCreate, UserOut,
    ParcelCreate, ParcelOut, ParcelScore,
    BatchCreate, BatchOut,
    CustodyEventCreate, CustodyEventOut, CustodyTrailOut,
    DDSRequest,
)
from app.services.satellite import score_parcel
from app.services.dds import generate_dds

router = APIRouter()


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/auth/register", response_model=UserOut, tags=["Auth"])
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        organisation=user_in.organisation,
        country=user_in.country,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/token", response_model=TokenResponse, tags=["Auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Allow demo user login without DB entry
    if form.username == settings.DEMO_EMAIL and form.password == settings.DEMO_PASSWORD:
        token = create_access_token({"sub": settings.DEMO_EMAIL})
        return {"access_token": token, "token_type": "bearer"}

    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# ── Parcels ───────────────────────────────────────────────────────────────────

@router.post("/parcels/", response_model=ParcelOut, tags=["Parcels"])
def create_parcel(
    parcel_in: ParcelCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    user = _get_or_create_demo_user(current_user, db)
    parcel = Parcel(
        owner_id=user.id,
        name=parcel_in.name,
        farmer_name=parcel_in.farmer_name,
        cooperative=parcel_in.cooperative,
        commodity=parcel_in.commodity.lower(),
        country=parcel_in.country,
        region=parcel_in.region,
        geojson=parcel_in.geojson,
        centroid_lat=parcel_in.centroid_lat,
        centroid_lon=parcel_in.centroid_lon,
        area_ha=parcel_in.area_ha,
    )
    db.add(parcel)
    db.commit()
    db.refresh(parcel)

    # Trigger satellite scoring automatically on creation
    _run_satellite_score(parcel, db)
    return parcel


@router.get("/parcels/", response_model=list[ParcelOut], tags=["Parcels"])
def list_parcels(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    user = _get_or_create_demo_user(current_user, db)
    return db.query(Parcel).filter(Parcel.owner_id == user.id).all()


@router.get("/parcels/{parcel_id}", response_model=ParcelOut, tags=["Parcels"])
def get_parcel(
    parcel_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(404, "Parcel not found")
    return parcel


@router.post("/parcels/{parcel_id}/rescore", response_model=ParcelScore, tags=["Parcels"])
def rescore_parcel(
    parcel_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(404, "Parcel not found")
    result = _run_satellite_score(parcel, db)
    return ParcelScore(parcel_id=parcel_id, **result)


# ── Batches ───────────────────────────────────────────────────────────────────

@router.post("/batches/", response_model=BatchOut, tags=["Batches"])
def create_batch(
    batch_in: BatchCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    user = _get_or_create_demo_user(current_user, db)

    # Validate all parcels exist
    parcels = []
    for pid in batch_in.parcel_ids:
        p = db.query(Parcel).filter(Parcel.id == pid).first()
        if not p:
            raise HTTPException(400, f"Parcel {pid} not found")
        parcels.append(p)

    batch_code = f"TL-{batch_in.commodity.upper()[:3]}-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    all_compliant = all(p.eudr_compliant for p in parcels if p.eudr_compliant is not None)

    batch = CommodityBatch(
        owner_id=user.id,
        batch_code=batch_code,
        commodity=batch_in.commodity.lower(),
        quantity_kg=batch_in.quantity_kg,
        harvest_date=batch_in.harvest_date,
        export_date=batch_in.export_date,
        destination_country=batch_in.destination_country,
        washing_station=batch_in.washing_station,
        exporter_name=batch_in.exporter_name,
        importer_name=batch_in.importer_name,
        all_parcels_compliant=all_compliant,
    )
    db.add(batch)
    db.flush()

    for p in parcels:
        bp = BatchParcel(batch_id=batch.id, parcel_id=p.id)
        db.add(bp)

    # Auto-create HARVEST custody event
    evt = CustodyEvent(
        batch_id=batch.id,
        event_type="HARVEST",
        event_timestamp=batch_in.harvest_date,
        location_name=batch_in.washing_station or "Farm gate",
        actor_name=batch_in.exporter_name or user.email,
    )
    db.add(evt)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/batches/", response_model=list[BatchOut], tags=["Batches"])
def list_batches(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    user = _get_or_create_demo_user(current_user, db)
    return db.query(CommodityBatch).filter(CommodityBatch.owner_id == user.id).all()


@router.get("/batches/{batch_id}/custody", response_model=CustodyTrailOut, tags=["Batches"])
def get_custody_trail(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    batch = db.query(CommodityBatch).filter(CommodityBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found")

    events = db.query(CustodyEvent).filter(
        CustodyEvent.batch_id == batch_id
    ).order_by(CustodyEvent.event_timestamp).all()

    parcel_count = db.query(BatchParcel).filter(BatchParcel.batch_id == batch_id).count()

    return CustodyTrailOut(
        batch_id=batch.id,
        batch_code=batch.batch_code,
        commodity=batch.commodity,
        quantity_kg=batch.quantity_kg,
        parcel_count=parcel_count,
        all_compliant=batch.all_parcels_compliant,
        events=events,
    )


@router.post("/custody/", response_model=CustodyEventOut, tags=["Custody"])
def add_custody_event(
    event_in: CustodyEventCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    batch = db.query(CommodityBatch).filter(CommodityBatch.id == event_in.batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found")

    evt = CustodyEvent(
        batch_id=event_in.batch_id,
        event_type=event_in.event_type,
        event_timestamp=event_in.event_timestamp or datetime.utcnow(),
        location_name=event_in.location_name,
        gps_lat=event_in.gps_lat,
        gps_lon=event_in.gps_lon,
        actor_name=event_in.actor_name,
        notes=event_in.notes,
        metadata=event_in.metadata,
    )
    db.add(evt)
    db.commit()
    db.refresh(evt)
    return evt


# ── DDS Generation ────────────────────────────────────────────────────────────

@router.post("/dds/generate", tags=["DDS"])
def generate_dds_endpoint(
    req: DDSRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_email),
):
    batch = db.query(CommodityBatch).filter(CommodityBatch.id == req.batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found")

    # Collect parcels
    batch_parcels = db.query(BatchParcel).filter(BatchParcel.batch_id == batch.id).all()
    parcels_data = []
    for bp in batch_parcels:
        p = bp.parcel
        parcels_data.append({
            "name": p.name,
            "country": p.country,
            "lat": p.centroid_lat,
            "lon": p.centroid_lon,
            "deforestation_score": p.deforestation_score or 0,
            "risk_level": p.risk_level or "UNKNOWN",
            "eudr_compliant": p.eudr_compliant or False,
        })

    # Collect custody events
    events = db.query(CustodyEvent).filter(
        CustodyEvent.batch_id == batch.id
    ).order_by(CustodyEvent.event_timestamp).all()
    events_data = [
        {
            "event_type": e.event_type,
            "event_timestamp": e.event_timestamp,
            "location_name": e.location_name or "—",
            "actor_name": e.actor_name or "—",
        }
        for e in events
    ]

    dds_ref = f"TL-DDS-{batch.batch_code}"
    pdf_bytes = generate_dds(
        batch_code=batch.batch_code,
        commodity=batch.commodity,
        quantity_kg=batch.quantity_kg,
        harvest_date=batch.harvest_date,
        destination_country=batch.destination_country or "EU",
        operator_name=req.operator_name,
        operator_country=req.operator_country,
        parcels=parcels_data,
        custody_events=events_data,
        statement_date=req.statement_date or datetime.utcnow(),
        dds_reference=dds_ref,
    )

    # Mark DDS as generated
    batch.dds_generated = True
    batch.dds_reference = dds_ref
    db.commit()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{dds_ref}.pdf"'},
    )


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "satellite_mode": settings.SATELLITE_MODE,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_create_demo_user(email: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        from app.core.security import get_password_hash
        user = User(
            email=email,
            hashed_password=get_password_hash("demo"),
            organisation="TerraLedger Demo",
            country="Kenya",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def _run_satellite_score(parcel: Parcel, db: Session) -> dict:
    result = score_parcel(parcel.centroid_lat, parcel.centroid_lon, parcel.area_ha or 1.0)
    parcel.ndvi_baseline_2020 = result["ndvi_baseline_2020"]
    parcel.ndvi_latest = result["ndvi_latest"]
    parcel.ndvi_delta = result["ndvi_delta"]
    parcel.deforestation_score = result["deforestation_score"]
    parcel.confidence = result["confidence"]
    parcel.risk_level = result["risk_level"]
    parcel.eudr_compliant = result["eudr_compliant"]
    parcel.xai_explanation = result["xai_explanation"]
    parcel.satellite_last_checked = result["satellite_last_checked"]
    db.commit()
    db.refresh(parcel)
    return result
