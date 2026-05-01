import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, DateTime, Text,
    ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    organisation = Column(String)
    country = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    parcels = relationship("Parcel", back_populates="owner")
    batches = relationship("CommodityBatch", back_populates="owner")


# ─────────────────────────────────────────────
# PARCEL
# ─────────────────────────────────────────────
class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    farmer_name = Column(String)
    cooperative = Column(String)
    commodity = Column(String, nullable=False)

    country = Column(String, nullable=False)
    region = Column(String)

    geojson = Column(Text, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lon = Column(Float, nullable=False)
    area_ha = Column(Float)

    ndvi_baseline_2020 = Column(Float)
    ndvi_latest = Column(Float)
    ndvi_delta = Column(Float)

    deforestation_score = Column(Float)
    confidence = Column(Float)
    risk_level = Column(String)

    satellite_last_checked = Column(DateTime)
    xai_explanation = Column(Text)

    eudr_compliant = Column(Boolean)
    verified_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="parcels")
    batch_parcels = relationship("BatchParcel", back_populates="parcel")


# ─────────────────────────────────────────────
# COMMODITY BATCH
# ─────────────────────────────────────────────
class CommodityBatch(Base):
    __tablename__ = "commodity_batches"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)

    batch_code = Column(String, unique=True, index=True)
    commodity = Column(String)
    quantity_kg = Column(Float)

    harvest_date = Column(DateTime)
    export_date = Column(DateTime)
    destination_country = Column(String)

    washing_station = Column(String)
    exporter_name = Column(String)
    importer_name = Column(String)

    all_parcels_compliant = Column(Boolean)
    dds_generated = Column(Boolean, default=False)
    dds_reference = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="batches")
    batch_parcels = relationship("BatchParcel", back_populates="batch")
    custody_events = relationship("CustodyEvent", back_populates="batch")


# ─────────────────────────────────────────────
# BATCH ↔ PARCEL LINK
# ─────────────────────────────────────────────
class BatchParcel(Base):
    __tablename__ = "batch_parcels"

    id = Column(String, primary_key=True, default=gen_uuid)
    batch_id = Column(String, ForeignKey("commodity_batches.id"))
    parcel_id = Column(String, ForeignKey("parcels.id"))

    weight_from_parcel_kg = Column(Float)

    batch = relationship("CommodityBatch", back_populates="batch_parcels")
    parcel = relationship("Parcel", back_populates="batch_parcels")


# ─────────────────────────────────────────────
# CUSTODY EVENTS (FIXED)
# ─────────────────────────────────────────────
class CustodyEvent(Base):
    __tablename__ = "custody_events"

    id = Column(String, primary_key=True, default=gen_uuid)
    batch_id = Column(String, ForeignKey("commodity_batches.id"), nullable=False)

    event_type = Column(String, nullable=False)
    event_timestamp = Column(DateTime, default=datetime.utcnow)

    location_name = Column(String)
    gps_lat = Column(Float)
    gps_lon = Column(Float)

    actor_name = Column(String)
    notes = Column(Text)

    # IMPORTANT FIX: renamed from "metadata" (reserved keyword)
    event_metadata = Column(JSON)

    batch = relationship("CommodityBatch", back_populates="custody_events")