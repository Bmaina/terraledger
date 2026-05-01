from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import get_db, User, Parcel, CustodyEvent

router = APIRouter()


# ── HEALTH ───────────────────────────────────────────────
@router.get("/health")
def health():
    return {"status": "ok", "service": "TerraLedger"}


# ── SIMPLE USER CREATION (TEMP AUTH) ─────────────────────
@router.post("/auth/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(400, "User already exists")

    user = User(
        email=email,
        hashed_password=password,
        organisation="default",
        country="KE",
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


# ── PARCELS ──────────────────────────────────────────────
@router.post("/parcels")
def create_parcel(name: str, lat: float, lon: float, db: Session = Depends(get_db)):

    parcel = Parcel(
        name=name,
        centroid_lat=lat,
        centroid_lon=lon,
        created_at=datetime.utcnow(),
    )

    db.add(parcel)
    db.commit()
    db.refresh(parcel)
    return parcel


@router.get("/parcels")
def list_parcels(db: Session = Depends(get_db)):
    return db.query(Parcel).all()


# ── CUSTODY ───────────────────────────────────────────────
@router.post("/custody")
def add_custody(parcel_id: int, event_type: str, db: Session = Depends(get_db)):

    event = CustodyEvent(
        parcel_id=parcel_id,
        event_type=event_type,
        timestamp=datetime.utcnow(),
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return event