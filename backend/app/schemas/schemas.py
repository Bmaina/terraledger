from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    organisation: Optional[str] = None
    country: Optional[str] = None


class UserOut(BaseModel):
    id: str
    email: str
    organisation: Optional[str]
    country: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Parcels ───────────────────────────────────────────────────────────────────

class ParcelCreate(BaseModel):
    name: str = Field(..., example="Kericho Plot A-12")
    farmer_name: Optional[str] = Field(None, example="John Kamau")
    cooperative: Optional[str] = Field(None, example="New Murarandia FCS")
    commodity: str = Field(..., example="coffee")
    country: str = Field(..., example="Kenya")
    region: Optional[str] = Field(None, example="Kericho County")
    geojson: str = Field(..., description="GeoJSON polygon string")
    centroid_lat: float = Field(..., example=-0.3674)
    centroid_lon: float = Field(..., example=35.2869)
    area_ha: Optional[float] = Field(None, example=0.75)


class ParcelScore(BaseModel):
    parcel_id: str
    ndvi_baseline_2020: float
    ndvi_latest: float
    ndvi_delta: float
    deforestation_score: float
    confidence: float
    risk_level: str
    eudr_compliant: bool
    xai_explanation: str
    satellite_last_checked: datetime


class ParcelOut(BaseModel):
    id: str
    name: str
    farmer_name: Optional[str]
    cooperative: Optional[str]
    commodity: str
    country: str
    region: Optional[str]
    centroid_lat: float
    centroid_lon: float
    area_ha: Optional[float]
    deforestation_score: Optional[float]
    risk_level: Optional[str]
    eudr_compliant: Optional[bool]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Batches ───────────────────────────────────────────────────────────────────

class BatchCreate(BaseModel):
    commodity: str = Field(..., example="coffee")
    quantity_kg: float = Field(..., example=500.0)
    harvest_date: datetime
    export_date: Optional[datetime] = None
    destination_country: Optional[str] = Field(None, example="Germany")
    washing_station: Optional[str] = Field(None, example="Kericho Central Washing Station")
    exporter_name: Optional[str] = Field(None, example="Kenya Coffee Exporters Ltd")
    importer_name: Optional[str] = None
    parcel_ids: List[str] = Field(..., description="List of parcel IDs included in this batch")


class BatchOut(BaseModel):
    id: str
    batch_code: str
    commodity: str
    quantity_kg: float
    harvest_date: datetime
    destination_country: Optional[str]
    all_parcels_compliant: Optional[bool]
    dds_generated: bool
    dds_reference: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Custody ───────────────────────────────────────────────────────────────────

class CustodyEventCreate(BaseModel):
    batch_id: str
    event_type: str = Field(..., example="TRANSPORT")
    event_timestamp: Optional[datetime] = None
    location_name: Optional[str] = Field(None, example="Nairobi Dry Mill")
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    actor_name: Optional[str] = Field(None, example="Freight Logistics EA")
    notes: Optional[str] = None
    metadata: Optional[Any] = None


class CustodyEventOut(BaseModel):
    id: str
    event_type: str
    event_timestamp: datetime
    location_name: Optional[str]
    gps_lat: Optional[float]
    gps_lon: Optional[float]
    actor_name: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class CustodyTrailOut(BaseModel):
    batch_id: str
    batch_code: str
    commodity: str
    quantity_kg: float
    parcel_count: int
    all_compliant: Optional[bool]
    events: List[CustodyEventOut]


# ── DDS ───────────────────────────────────────────────────────────────────────

class DDSRequest(BaseModel):
    batch_id: str
    operator_name: str = Field(..., example="Arabica Exports Ltd")
    operator_country: str = Field(..., example="Kenya")
    statement_date: Optional[datetime] = None
