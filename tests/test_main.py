import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_analytics_contract():
    """Test GET /api/v1/analytics/contract returns 200 with JSON"""
    response = client.get("/api/v1/analytics/contract")
    
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    
    data = response.json()
    assert "qualitative" in data
    assert "quantitative" in data
    assert isinstance(data["qualitative"], list)
    assert isinstance(data["quantitative"], list)


def test_get_instance_metrics():
    """Test GET /api/v1/analytics/instances/{instance_id}/metrics returns 200 with JSON"""
    instance_id = "inst_abc123"
    response = client.get(f"/api/v1/analytics/instances/{instance_id}/metrics")
    
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    
    data = response.json()
    assert data["instance_id"] == instance_id
    assert "metrics" in data
    assert "qualitative" in data
    assert "calculated_at" in data
    
    # Check metrics structure
    metrics = data["metrics"]
    assert "started_exercises" in metrics
    assert "completed_exercises" in metrics
    assert "final_score" in metrics
    assert "activity_success" in metrics


def test_health_check():
    """Test GET /health returns 200 with healthy status"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "mrnewton-analytics"
