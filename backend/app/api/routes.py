from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.models import User, Parcel, CustodyEvent

router = APIRouter()


# ─────────────────────────────────────────────
# HEALTH CHECK (NO DB DEPENDENCY)
# ─────────────────────────────────────────────
@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TerraLedger"
    }


# ─────────────────────────────────────────────
# AUTH (MVP - NOT SECURE FOR PRODUCTION)
# ─────────────────────────────────────────────
@router.post("/auth/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=email,
        hashed_password=password,  # ⚠️ hash in production
        organisation="default",
        country="KE",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email
    }


# ─────────────────────────────────────────────
# PARCELS
# ─────────────────────────────────────────────
@router.post("/parcels")
def create_parcel(
    name: str,
    lat: float,
    lon: float,
    db: Session = Depends(get_db)
):
    parcel = Parcel(
        name=name,
        centroid_lat=lat,
        centroid_lon=lon,
        country="KE",
        commodity="coffee",
        geojson="{}",
    )

    db.add(parcel)
    db.commit()
    db.refresh(parcel)

    return parcel


@router.get("/parcels")
def list_parcels(db: Session = Depends(get_db)):
    return db.query(Parcel).all()


# ─────────────────────────────────────────────
# CUSTODY EVENTS
# ─────────────────────────────────────────────
@router.post("/custody")
def add_custody(
    batch_id: str,
    event_type: str,
    db: Session = Depends(get_db)
):
    event = CustodyEvent(
        batch_id=batch_id,
        event_type=event_type,
        event_timestamp=datetime.utcnow(),
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event