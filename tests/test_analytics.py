"""
Tests for the MrNewton Analytics API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_redirects_to_docs():
    """Test that root endpoint redirects to API docs"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/api-docs" in response.headers["location"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "mrnewton-analytics"
    assert "timestamp" in data


def test_get_analytics_contract():
    """Test analytics contract endpoint"""
    response = client.get("/api/v1/analytics/contract")
    assert response.status_code == 200
    data = response.json()
    
    # Check structure
    assert "qualAnalytics" in data
    assert "quantAnalytics" in data
    
    # Check qualitative metrics
    assert isinstance(data["qualAnalytics"], list)
    if data["qualAnalytics"]:
        qual_metric = data["qualAnalytics"][0]
        assert "name" in qual_metric
        assert "type" in qual_metric
    
    # Check quantitative metrics
    assert isinstance(data["quantAnalytics"], list)
    assert len(data["quantAnalytics"]) > 0
    
    # Verify expected metrics exist
    metric_names = [m["name"] for m in data["quantAnalytics"]]
    expected_metrics = [
        "total_attempts",
        "total_time_seconds",
        "average_time_per_attempt",
        "number_of_correct_answers",
        "final_score",
        "activity_success"
    ]
    
    for expected in expected_metrics:
        assert expected in metric_names, f"Missing metric: {expected}"


def test_get_student_metrics_not_found():
    """Test metrics endpoint with non-existent data"""
    response = client.get("/api/v1/analytics/instances/fake_instance/students/fake_student/metrics")
    
    # Should return 404 or 500 depending on Activity service availability
    assert response.status_code in [404, 500]


# Integration tests would require:
# - Mock Activity service
# - MongoDB test database
# - Sample submission data

@pytest.mark.skip(reason="Requires Activity service and test data")
def test_get_student_metrics_success():
    """Test successful metrics calculation"""
    # This would require:
    # 1. Activity service running
    # 2. Test instance created
    # 3. Test submission recorded
    pass
