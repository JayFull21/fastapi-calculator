"""
test_main.py

Integration tests for the FastAPI application's HTTP endpoints. Uses
FastAPI's TestClient (built on httpx) so no real server needs to be
running - requests go through the ASGI app in-process.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_index_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "FastAPI Calculator" in response.text


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("endpoint, a, b, expected", [
    ("/add", 2, 3, 5),
    ("/add", -2, -3, -5),
    ("/subtract", 10, 4, 6),
    ("/subtract", 4, 10, -6),
    ("/multiply", 3, 5, 15),
    ("/multiply", -3, 5, -15),
    ("/divide", 10, 2, 5),
    ("/divide", 7, 2, 3.5),
])
def test_arithmetic_endpoints(endpoint, a, b, expected):
    response = client.post(endpoint, json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json()["result"] == expected


def test_divide_by_zero_returns_400():
    response = client.post("/divide", json={"a": 5, "b": 0})
    assert response.status_code == 400
    assert "Division by zero" in response.json()["detail"]


@pytest.mark.parametrize("endpoint", ["/add", "/subtract", "/multiply", "/divide"])
def test_missing_fields_returns_422(endpoint):
    response = client.post(endpoint, json={"a": 1})
    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", ["/add", "/subtract", "/multiply", "/divide"])
def test_invalid_types_returns_422(endpoint):
    response = client.post(endpoint, json={"a": "not-a-number", "b": 2})
    assert response.status_code == 422
