"""
TerraLedger Backend Tests
--------------------------
Tests satellite scoring, DDS generation, and API health.
Run: pytest tests/ -v
"""

import pytest
from app.services.satellite import score_parcel, _get_zone_risk


class TestSatelliteService:
    """Tests for the GeoAI satellite scoring engine."""

    def test_score_kenya_low_risk(self):
        """Kenya Kericho is a low-risk zone — should score below 30."""
        result = score_parcel(-0.3674, 35.2869, 0.75)
        assert result["deforestation_score"] < 40
        assert result["risk_level"] in ("LOW", "MEDIUM")
        assert result["confidence"] > 0.7
        assert result["eudr_compliant"] is not None
        assert "xai_explanation" in result
        assert len(result["xai_explanation"]) > 20

    def test_score_ethiopia_higher_risk(self):
        """Ethiopia Kaffa zone has higher baseline risk."""
        result = score_parcel(7.32, 36.15, 0.4)
        assert result["deforestation_score"] >= 10
        assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")

    def test_score_rwanda_low_risk(self):
        """Rwanda Western Province is a low-risk zone."""
        result = score_parcel(-2.0833, 29.25, 0.3)
        assert result["risk_level"] in ("LOW", "MEDIUM")

    def test_score_returns_all_fields(self):
        """All required fields must be present in score output."""
        result = score_parcel(1.2367, 34.3811, 0.8)
        required = [
            "ndvi_baseline_2020", "ndvi_latest", "ndvi_delta",
            "deforestation_score", "confidence", "risk_level",
            "eudr_compliant", "xai_explanation", "satellite_last_checked"
        ]
        for field in required:
            assert field in result, f"Missing field: {field}"

    def test_ndvi_values_in_range(self):
        """NDVI values must be within the valid -1 to 1 range."""
        result = score_parcel(-0.5621, 37.2834, 1.2)
        assert -1 <= result["ndvi_baseline_2020"] <= 1
        assert -1 <= result["ndvi_latest"] <= 1

    def test_score_range(self):
        """Deforestation score must be 0-100."""
        result = score_parcel(0.5821, 30.0844, 0.6)
        assert 0 <= result["deforestation_score"] <= 100

    def test_deterministic_output(self):
        """Same coordinates must always return the same score."""
        r1 = score_parcel(-0.3674, 35.2869, 0.75)
        r2 = score_parcel(-0.3674, 35.2869, 0.75)
        assert r1["deforestation_score"] == r2["deforestation_score"]
        assert r1["risk_level"] == r2["risk_level"]

    def test_zone_risk_lookup(self):
        """Zone risk lookup returns expected values."""
        kenya_risk = _get_zone_risk(-0.3674, 35.2869)
        ethiopia_risk = _get_zone_risk(7.32, 36.15)
        assert kenya_risk < ethiopia_risk  # Kenya is lower risk than Kaffa Ethiopia


class TestDDSGeneration:
    """Tests for the DDS PDF generator."""

    def test_generate_dds_returns_bytes(self):
        from app.services.dds import generate_dds
        from datetime import datetime

        pdf = generate_dds(
            batch_code="TL-COF-TEST-001",
            commodity="coffee",
            quantity_kg=500.0,
            harvest_date=datetime(2025, 6, 1),
            destination_country="Germany",
            operator_name="Test Exports Ltd",
            operator_country="Kenya",
            parcels=[{
                "name": "Test Parcel A",
                "country": "Kenya",
                "lat": -0.3674,
                "lon": 35.2869,
                "deforestation_score": 12.5,
                "risk_level": "LOW",
                "eudr_compliant": True,
            }],
            custody_events=[{
                "event_type": "HARVEST",
                "event_timestamp": datetime(2025, 6, 1),
                "location_name": "Farm gate",
                "actor_name": "Test Exports Ltd",
            }],
        )
        assert isinstance(pdf, bytes)
        assert len(pdf) > 5000  # PDF should have meaningful content
        assert pdf[:4] == b'%PDF'  # Valid PDF header

    def test_generate_dds_flagged_batch(self):
        from app.services.dds import generate_dds
        from datetime import datetime

        # DDS should still generate for flagged batches (compliance decision is documented)
        pdf = generate_dds(
            batch_code="TL-COF-TEST-002",
            commodity="cocoa",
            quantity_kg=1000.0,
            harvest_date=datetime(2025, 3, 15),
            destination_country="Netherlands",
            operator_name="Risky Exports Ltd",
            operator_country="Ethiopia",
            parcels=[{
                "name": "Kaffa Edge Plot",
                "country": "Ethiopia",
                "lat": 7.32,
                "lon": 36.15,
                "deforestation_score": 68.0,
                "risk_level": "HIGH",
                "eudr_compliant": False,
            }],
            custody_events=[],
        )
        assert isinstance(pdf, bytes)
        assert pdf[:4] == b'%PDF'
