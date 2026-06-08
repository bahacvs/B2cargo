"""FastAPI endpoint testleri (adım 13). Mock adapter'larla uçtan uca."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import create_app


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("USE_MOCK_ADAPTERS", "true")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture
def client():
    return TestClient(create_app())


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_turkey_report(client):
    resp = client.get("/reports/turkey")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["depot_reports"]) == 11
    assert "ankara" in body["prioritized_depots"]


def test_depot_report(client):
    resp = client.get("/reports/ankara")
    assert resp.status_code == 200
    body = resp.json()
    assert body["depot_id"] == "ankara"
    by_id = {r["item_id"]: r for r in body["results"]}
    assert by_id["ank-frozen-001"]["level"] == "CRITICAL"


def test_unknown_depot_404(client):
    assert client.get("/reports/yok-boyle-depo").status_code == 404


def test_notifications(client):
    resp = client.get("/notifications")
    assert resp.status_code == 200
    payloads = resp.json()
    assert any(p["item_id"] == "ank-frozen-001" for p in payloads)


def test_alert_endpoint(client):
    resp = client.post("/notifications/alert", json={"depot_id": "ankara"})
    assert resp.status_code == 200
    assert any(p["item_id"] == "ank-frozen-001" for p in resp.json())
