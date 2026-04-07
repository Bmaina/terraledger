"""
TerraLedger Demo Seed Script
-----------------------------
Populates the database with realistic East African coffee farm parcels,
commodity batches, and custody events for investor demos.

Run: python scripts/seed_demo.py
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.core.database import Base
from app.core.security import get_password_hash
from app.models.models import User, Parcel, CommodityBatch, BatchParcel, CustodyEvent
from app.services.satellite import score_parcel

# Import all models so Base.metadata knows about them
from app.models import models  # noqa

Base.metadata.create_all(bind=engine)


DEMO_PARCELS = [
    # Kenya — Low risk region
    {
        "name": "Kericho Highland A-12",
        "farmer_name": "Joseph Kibet",
        "cooperative": "New Murarandia FCS",
        "commodity": "coffee",
        "country": "Kenya",
        "region": "Kericho County",
        "centroid_lat": -0.3674,
        "centroid_lon": 35.2869,
        "area_ha": 0.75,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[35.2849, -0.3694], [35.2889, -0.3694],
                              [35.2889, -0.3654], [35.2849, -0.3654], [35.2849, -0.3694]]]
        }),
    },
    {
        "name": "Kirinyaga Plot B-07",
        "farmer_name": "Grace Wanjiku",
        "cooperative": "Othaya FCS",
        "commodity": "coffee",
        "country": "Kenya",
        "region": "Kirinyaga County",
        "centroid_lat": -0.5621,
        "centroid_lon": 37.2834,
        "area_ha": 1.2,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[37.2814, -0.5641], [37.2854, -0.5641],
                              [37.2854, -0.5601], [37.2814, -0.5601], [37.2814, -0.5641]]]
        }),
    },
    {
        "name": "Kisii Arabica Plot C-19",
        "farmer_name": "Emmanuel Onyango",
        "cooperative": "Kisii Central Coop",
        "commodity": "coffee",
        "country": "Kenya",
        "region": "Kisii County",
        "centroid_lat": -0.6820,
        "centroid_lon": 34.7660,
        "area_ha": 0.5,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[34.7640, -0.6840], [34.7680, -0.6840],
                              [34.7680, -0.6800], [34.7640, -0.6800], [34.7640, -0.6840]]]
        }),
    },
    # Ethiopia — Variable risk
    {
        "name": "Yirgacheffe Forest Plot 01",
        "farmer_name": "Bekele Tadesse",
        "cooperative": "Yirgacheffe Coffee Farmers Coop",
        "commodity": "coffee",
        "country": "Ethiopia",
        "region": "Gedeo Zone",
        "centroid_lat": 6.1527,
        "centroid_lon": 38.2079,
        "area_ha": 0.11,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[38.2059, 6.1507], [38.2099, 6.1507],
                              [38.2099, 6.1547], [38.2059, 6.1547], [38.2059, 6.1507]]]
        }),
    },
    {
        "name": "Jimma Agroforest Plot 03",
        "farmer_name": "Mulugeta Abebe",
        "cooperative": "Jimma Coffee Exporters Union",
        "commodity": "coffee",
        "country": "Ethiopia",
        "region": "Jimma Zone",
        "centroid_lat": 7.6731,
        "centroid_lon": 36.8344,
        "area_ha": 0.3,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[36.8324, 7.6711], [36.8364, 7.6711],
                              [36.8364, 7.6751], [36.8324, 7.6751], [36.8324, 7.6711]]]
        }),
    },
    {
        "name": "Kaffa Forest Edge Plot 08",
        "farmer_name": "Tigist Haile",
        "cooperative": "Kaffa Coffee Development",
        "commodity": "coffee",
        "country": "Ethiopia",
        "region": "Kaffa Zone",
        "centroid_lat": 7.3200,
        "centroid_lon": 36.1500,
        "area_ha": 0.4,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[36.1480, 7.3180], [36.1520, 7.3180],
                              [36.1520, 7.3220], [36.1480, 7.3220], [36.1480, 7.3180]]]
        }),
    },
    # Uganda
    {
        "name": "Mt Elgon Arabica 14",
        "farmer_name": "Peter Wafula",
        "cooperative": "Sipi Falls Coffee Coop",
        "commodity": "coffee",
        "country": "Uganda",
        "region": "Kapchorwa District",
        "centroid_lat": 1.2367,
        "centroid_lon": 34.3811,
        "area_ha": 0.8,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[34.3791, 1.2347], [34.3831, 1.2347],
                              [34.3831, 1.2387], [34.3791, 1.2387], [34.3791, 1.2347]]]
        }),
    },
    {
        "name": "Rwenzori Highland Plot 06",
        "farmer_name": "Sarah Birungi",
        "cooperative": "Rwenzori Specialty Coffee",
        "commodity": "coffee",
        "country": "Uganda",
        "region": "Kasese District",
        "centroid_lat": 0.5821,
        "centroid_lon": 30.0844,
        "area_ha": 0.6,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[30.0824, 0.5801], [30.0864, 0.5801],
                              [30.0864, 0.5841], [30.0824, 0.5841], [30.0824, 0.5801]]]
        }),
    },
    # Rwanda
    {
        "name": "Western Province Plot 22",
        "farmer_name": "Claudine Mukamana",
        "cooperative": "COOPAC Specialty Coffee",
        "commodity": "coffee",
        "country": "Rwanda",
        "region": "Western Province",
        "centroid_lat": -2.0833,
        "centroid_lon": 29.2500,
        "area_ha": 0.3,
        "geojson": json.dumps({
            "type": "Polygon",
            "coordinates": [[[29.2480, -2.0853], [29.2520, -2.0853],
                              [29.2520, -2.0813], [29.2480, -2.0813], [29.2480, -2.0853]]]
        }),
    },
]

CUSTODY_EVENTS_TEMPLATE = [
    {"event_type": "HARVEST", "location_name": "Farm gate", "offset_days": -60},
    {"event_type": "TRANSPORT", "location_name": "Washing Station", "offset_days": -58},
    {"event_type": "PROCESS", "location_name": "Central Dry Mill", "offset_days": -45},
    {"event_type": "TRANSPORT", "location_name": "Nairobi Export Hub", "offset_days": -30},
    {"event_type": "EXPORT", "location_name": "Mombasa Port", "offset_days": -14},
]


def seed():
    db = SessionLocal()
    try:
        # Clean existing demo data
        print("Clearing existing demo data...")
        db.query(CustodyEvent).delete()
        db.query(BatchParcel).delete()
        db.query(CommodityBatch).delete()
        db.query(Parcel).delete()
        db.query(User).filter(User.email == "demo@terraledger.io").delete()
        db.commit()

        # Create demo user
        print("Creating demo user...")
        user = User(
            email="demo@terraledger.io",
            hashed_password=get_password_hash("TerraDemo2026"),
            organisation="TerraLedger Demo Account",
            country="Kenya",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create parcels with satellite scores
        print(f"Seeding {len(DEMO_PARCELS)} farm parcels...")
        created_parcels = []
        for pd in DEMO_PARCELS:
            score_result = score_parcel(pd["centroid_lat"], pd["centroid_lon"], pd.get("area_ha", 1.0))
            parcel = Parcel(
                owner_id=user.id,
                name=pd["name"],
                farmer_name=pd.get("farmer_name"),
                cooperative=pd.get("cooperative"),
                commodity=pd["commodity"],
                country=pd["country"],
                region=pd.get("region"),
                geojson=pd["geojson"],
                centroid_lat=pd["centroid_lat"],
                centroid_lon=pd["centroid_lon"],
                area_ha=pd.get("area_ha"),
                ndvi_baseline_2020=score_result["ndvi_baseline_2020"],
                ndvi_latest=score_result["ndvi_latest"],
                ndvi_delta=score_result["ndvi_delta"],
                deforestation_score=score_result["deforestation_score"],
                confidence=score_result["confidence"],
                risk_level=score_result["risk_level"],
                eudr_compliant=score_result["eudr_compliant"],
                xai_explanation=score_result["xai_explanation"],
                satellite_last_checked=score_result["satellite_last_checked"],
            )
            db.add(parcel)
            db.flush()
            created_parcels.append(parcel)
            status = "✓ COMPLIANT" if parcel.eudr_compliant else "⚠ FLAGGED"
            print(f"  {parcel.name} [{parcel.country}] — {parcel.risk_level} risk — Score: {parcel.deforestation_score}/100 — {status}")

        db.commit()

        # Create demo batches
        print("\nSeeding commodity batches...")
        now = datetime.utcnow()

        # Batch 1: Kenya parcels — compliant
        kenya_parcels = [p for p in created_parcels if p.country == "Kenya"]
        batch1 = CommodityBatch(
            owner_id=user.id,
            batch_code="TL-COF-20260101-A1B2C3",
            commodity="coffee",
            quantity_kg=2400.0,
            harvest_date=now - timedelta(days=60),
            export_date=now - timedelta(days=14),
            destination_country="Germany",
            washing_station="Kericho Central Washing Station",
            exporter_name="Kenya Premium Exports Ltd",
            importer_name="Dallmayr GmbH",
            all_parcels_compliant=all(p.eudr_compliant for p in kenya_parcels),
        )
        db.add(batch1)
        db.flush()
        for p in kenya_parcels:
            db.add(BatchParcel(batch_id=batch1.id, parcel_id=p.id, weight_from_parcel_kg=800.0))

        # Add custody trail for batch 1
        actors = ["Kenya Premium Exports Ltd", "Freight EA Ltd", "Mombasa Port Authority", "Dallmayr GmbH"]
        for i, evt_tmpl in enumerate(CUSTODY_EVENTS_TEMPLATE):
            db.add(CustodyEvent(
                batch_id=batch1.id,
                event_type=evt_tmpl["event_type"],
                event_timestamp=now + timedelta(days=evt_tmpl["offset_days"]),
                location_name=evt_tmpl["location_name"],
                gps_lat=-0.3674 if i == 0 else None,
                gps_lon=35.2869 if i == 0 else None,
                actor_name=actors[min(i, len(actors) - 1)],
            ))

        # Batch 2: Ethiopia parcels
        eth_parcels = [p for p in created_parcels if p.country == "Ethiopia"]
        batch2 = CommodityBatch(
            owner_id=user.id,
            batch_code="TL-COF-20260115-D4E5F6",
            commodity="coffee",
            quantity_kg=1800.0,
            harvest_date=now - timedelta(days=45),
            export_date=now - timedelta(days=7),
            destination_country="Netherlands",
            washing_station="Yirgacheffe Wet Mill #3",
            exporter_name="Ethiopia Coffee Export PLC",
            importer_name="Trabocca BV",
            all_parcels_compliant=all(p.eudr_compliant for p in eth_parcels),
        )
        db.add(batch2)
        db.flush()
        for p in eth_parcels:
            db.add(BatchParcel(batch_id=batch2.id, parcel_id=p.id, weight_from_parcel_kg=600.0))
        db.add(CustodyEvent(
            batch_id=batch2.id,
            event_type="HARVEST",
            event_timestamp=now - timedelta(days=45),
            location_name="Yirgacheffe Cooperative",
            actor_name="Ethiopia Coffee Export PLC",
        ))
        db.add(CustodyEvent(
            batch_id=batch2.id,
            event_type="PROCESS",
            event_timestamp=now - timedelta(days=30),
            location_name="Addis Ababa Dry Mill",
            actor_name="ECTA Processing Hub",
        ))
        db.add(CustodyEvent(
            batch_id=batch2.id,
            event_type="EXPORT",
            event_timestamp=now - timedelta(days=7),
            location_name="Djibouti Port",
            actor_name="Ethiopia Coffee Export PLC",
        ))

        db.commit()
        print(f"  Batch: {batch1.batch_code} — Kenya — {batch1.quantity_kg}kg — {'COMPLIANT' if batch1.all_parcels_compliant else 'FLAGGED'}")
        print(f"  Batch: {batch2.batch_code} — Ethiopia — {batch2.quantity_kg}kg — {'COMPLIANT' if batch2.all_parcels_compliant else 'FLAGGED'}")

        print("\n✅ Demo seed complete!")
        print(f"\nDemo login: {user.email} / TerraDemo2026")
        print(f"Parcels: {len(created_parcels)} | Batches: 2")
        compliant = sum(1 for p in created_parcels if p.eudr_compliant)
        print(f"Compliant parcels: {compliant}/{len(created_parcels)}")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
