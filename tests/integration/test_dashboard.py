"""Dashboard endpoint testi."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import create_app


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("USE_MOCK_ADAPTERS", "true")


def test_dashboard_served():
    client = TestClient(create_app())
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Axiom Logistics Intelligence" in resp.text
    # Panelin veriyi çektiği endpoint referansı sayfada bulunmalı.
    assert "/reports/turkey" in resp.text
