import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    organisation = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parcels = relationship("Parcel", back_populates="owner")
    batches = relationship("CommodityBatch", back_populates="owner")


class Parcel(Base):
    """A farm parcel — the core unit of EUDR compliance."""
    __tablename__ = "parcels"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Identity
    name = Column(String, nullable=False)
    farmer_name = Column(String, nullable=True)
    cooperative = Column(String, nullable=True)
    commodity = Column(String, nullable=False)  # coffee, cocoa, timber, rubber, soy
    country = Column(String, nullable=False)
    region = Column(String, nullable=True)

    # Geospatial — stored as GeoJSON string
    geojson = Column(Text, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lon = Column(Float, nullable=False)
    area_ha = Column(Float, nullable=True)

    # Satellite scoring
    ndvi_baseline_2020 = Column(Float, nullable=True)    # NDVI score at Dec 2020 baseline
    ndvi_latest = Column(Float, nullable=True)           # Most recent NDVI score
    ndvi_delta = Column(Float, nullable=True)            # Change since baseline
    deforestation_score = Column(Float, nullable=True)   # 0-100, higher = more risk
    confidence = Column(Float, nullable=True)            # 0-1 confidence interval
    risk_level = Column(String, nullable=True)           # LOW / MEDIUM / HIGH
    satellite_last_checked = Column(DateTime, nullable=True)
    xai_explanation = Column(Text, nullable=True)        # Human-readable AI explanation

    # Status
    eudr_compliant = Column(Boolean, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="parcels")
    batch_parcels = relationship("BatchParcel", back_populates="parcel")


class CommodityBatch(Base):
    """A traceable lot of commodity — linked to verified parcels."""
    __tablename__ = "commodity_batches"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Identity
    batch_code = Column(String, unique=True, nullable=False, index=True)
    commodity = Column(String, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    harvest_date = Column(DateTime, nullable=False)
    export_date = Column(DateTime, nullable=True)
    destination_country = Column(String, nullable=True)

    # Processing
    washing_station = Column(String, nullable=True)
    exporter_name = Column(String, nullable=True)
    importer_name = Column(String, nullable=True)

    # Compliance
    all_parcels_compliant = Column(Boolean, nullable=True)
    dds_generated = Column(Boolean, default=False)
    dds_reference = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="batches")
    batch_parcels = relationship("BatchParcel", back_populates="batch")
    custody_events = relationship("CustodyEvent", back_populates="batch")


class BatchParcel(Base):
    """Many-to-many link: a batch can span multiple parcels."""
    __tablename__ = "batch_parcels"

    id = Column(String, primary_key=True, default=gen_uuid)
    batch_id = Column(String, ForeignKey("commodity_batches.id"), nullable=False)
    parcel_id = Column(String, ForeignKey("parcels.id"), nullable=False)
    weight_from_parcel_kg = Column(Float, nullable=True)

    batch = relationship("CommodityBatch", back_populates="batch_parcels")
    parcel = relationship("Parcel", back_populates="batch_parcels")


class CustodyEvent(Base):
    """Immutable audit trail — every time a batch changes hands or location."""
    __tablename__ = "custody_events"

    id = Column(String, primary_key=True, default=gen_uuid)
    batch_id = Column(String, ForeignKey("commodity_batches.id"), nullable=False)

    event_type = Column(String, nullable=False)  # HARVEST, TRANSPORT, PROCESS, EXPORT, IMPORT
    event_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    location_name = Column(String, nullable=True)
    gps_lat = Column(Float, nullable=True)
    gps_lon = Column(Float, nullable=True)
    actor_name = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    batch = relationship("CommodityBatch", back_populates="custody_events")
