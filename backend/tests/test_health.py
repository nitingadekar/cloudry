"""Tests for health check endpoints."""


def test_health(test_client):
    resp = test_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "cloudry-api"


def test_liveness(test_client):
    resp = test_client.get("/_admin/health/liveness")
    assert resp.status_code == 200
    assert resp.json()["status"] == "alive"


def test_readiness(test_client):
    resp = test_client.get("/_admin/health/readiness")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"
