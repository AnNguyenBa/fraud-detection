
import pytest

from scoring import (
    load_model,
    score_transaction,
    score_transactions,
)


@pytest.fixture(scope="module")
def model_package():
    """Load model một lần cho toàn bộ test scoring."""
    return load_model()


@pytest.fixture
def valid_transaction():
    """Tạo một giao dịch hợp lệ với 29 features."""

    transaction = {
        "time": 150000.0,
        "amount": 100.0,
    }

    for i in range(1, 29):
        transaction[f"v{i}"] = 0.1

    return transaction


def test_score_one_transaction(model_package, valid_transaction):
    """Kiểm tra chấm điểm một giao dịch."""

    result = score_transaction(
        valid_transaction,
        model_package,
    )

    assert 0 <= result["anomaly_score"] <= 100
    assert 0 <= result["fraud_probability"] <= 100
    assert result["model_version"] == "v1"
    assert isinstance(result["top_features"], list)


def test_score_batch(model_package, valid_transaction):
    """Kiểm tra chấm điểm nhiều giao dịch."""

    transactions = [
        valid_transaction,
        valid_transaction.copy(),
    ]

    results = score_transactions(
        transactions,
        model_package,
    )

    assert len(results) == 2

    for result in results:
        assert 0 <= result["anomaly_score"] <= 100
        assert 0 <= result["fraud_probability"] <= 100


def test_missing_feature(model_package, valid_transaction):
    """Thiếu feature phải báo lỗi."""

    invalid_transaction = valid_transaction.copy()
    del invalid_transaction["v1"]

    with pytest.raises(ValueError):
        score_transaction(
            invalid_transaction,
            model_package,
        )


def test_invalid_numeric_value(model_package, valid_transaction):
    """Giá trị không hợp lệ phải bị từ chối."""

    invalid_transaction = valid_transaction.copy()
    invalid_transaction["v1"] = float("nan")

    with pytest.raises(ValueError):
        score_transaction(
            invalid_transaction,
            model_package,
        )
