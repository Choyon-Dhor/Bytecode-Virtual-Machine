"""Unit tests for FastAPI endpoints (/health, /api/evaluate, static assets)."""

import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert "Bytecode VM" in data["engine"]


def test_evaluate_endpoint_success():
    payload = {"expression": "2 ^ 3 ^ 2"}
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["result"] == 512
    assert len(data["tokens"]) > 0
    assert data["ast"]["type"] == "BinaryOpNode"
    assert len(data["bytecode"]) > 0
    assert len(data["trace"]) > 0
    assert "metrics" in data
    assert data["metrics"]["instruction_count"] == len(data["bytecode"])


def test_evaluate_with_environment():
    payload = {
        "expression": "radius * 2",
        "environment": {"radius": 15},
    }
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 30


def test_evaluate_syntax_error():
    payload = {"expression": "2 + * 3"}
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "ParserError"
    assert data["diagnostic"] is not None


def test_evaluate_division_by_zero_error():
    payload = {"expression": "10 / (5 - 5)"}
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "DivisionByZeroError"


def test_evaluate_undefined_variable_error():
    payload = {"expression": "unknown_var + 1"}
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "UndefinedVariableError"


def test_frontend_index_serving():
    response = client.get("/")
    assert response.status_code == 200
    assert "Bytecode Virtual Machine" in response.text
