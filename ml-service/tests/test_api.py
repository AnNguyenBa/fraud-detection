
import pytest

from fastapi.testclient import TestClient

from main import app


API_KEY = "test-api-key"


@pytest.fixture(scope="module")
def client():
    """Khởi động FastAPI và load model cho test."""

    import os

    os.environ["ML_API_KEY"] = API_KEY

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def headers():
    return {
        "X-API-Key": API_KEY,
    }


@pytest.fixture
def valid_transaction():
    transaction = {
        "time": 150000.0,
        "amount": 100.0,
    }

    for i in range(1, 29):
        transaction[f"v{i}"] = 0.1

    return transaction


def test_health_success(client, headers):
    response = client.get(
        "/health",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "UP"
    assert data["model_version"] == "v1"


def test_health_missing_api_key(client):
    response = client.get("/health")

    assert response.status_code == 401


def test_health_wrong_api_key(client):
    response = client.get(
        "/health",
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


def test_score_success(client, headers, valid_transaction):
    response = client.post(
        "/score",
        headers=headers,
        json={
            "transactions": [valid_transaction],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "SUCCESS"
    assert data["total"] == 1
    assert data["model_version"] == "v1"

    result = data["results"][0]

    assert 0 <= result["anomaly_score"] <= 100
    assert 0 <= result["fraud_probability"] <= 100


def test_score_missing_feature(client, headers, valid_transaction):
    invalid_transaction = valid_transaction.copy()
    del invalid_transaction["v1"]

    response = client.post(
        "/score",
        headers=headers,
        json={
            "transactions": [invalid_transaction],
        },
    )

    assert response.status_code == 422


def test_score_invalid_type(client, headers, valid_transaction):
    invalid_transaction = valid_transaction.copy()
    invalid_transaction["v1"] = "not-a-number"

    response = client.post(
        "/score",
        headers=headers,
        json={
            "transactions": [invalid_transaction],
        },
    )

    assert response.status_code == 422


def test_score_empty_batch(client, headers):
    response = client.post(
        "/score",
        headers=headers,
        json={
            "transactions": [],
        },
    )

    assert response.status_code == 422


def test_score_batch_over_limit(client, headers, valid_transaction):
    transactions = [
        valid_transaction.copy()
        for _ in range(1001)
    ]

    response = client.post(
        "/score",
        headers=headers,
        json={
            "transactions": transactions,
        },
    )

    assert response.status_code == 422


def test_score_missing_api_key(client, valid_transaction):
    response = client.post(
        "/score",
        json={
            "transactions": [valid_transaction],
        },
    )

    assert response.status_code == 401
