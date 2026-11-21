"""
Scoring service cho hệ thống Fraud Detection.

Đầu vào mỗi giao dịch:
- time
- amount
- v1 ... v28

Đầu ra:
- anomaly_score: điểm bất thường 0-100
- fraud_probability: điểm dự đoán gian lận 0-100
- top_features: 5 features quan trọng nhất
- model_version: phiên bản mô hình

Không kết nối database.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# =========================================================
# 1. CẤU HÌNH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "fraud_detection_v1.joblib"
PREPARED_DATA_PATH = BASE_DIR / "outputs" / "prepared_data.joblib"

MAX_BATCH_SIZE = 1000
TOP_FEATURE_COUNT = 5

INPUT_COLUMNS = ["time", "amount"] + [
    f"v{i}" for i in range(1, 29)
]


# =========================================================
# 2. LOAD MODEL
# =========================================================

def load_model(model_path=MODEL_PATH):
    """
    Load model bundle.

    Chỉ gọi một lần khi khởi động service,
    không load lại model cho từng giao dịch.
    """

    model_path = Path(model_path)

    if not model_path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy model: {model_path}"
        )

    package = joblib.load(model_path)

    required_keys = [
        "model_version",
        "feature_columns",
        "scaler",
        "random_forest",
        "random_forest_threshold",
        "feature_importances",
        "isolation_forest",
        "sorted_train_scores",
        "isolation_threshold",
        "isolation_alert_rate",
    ]

    for key in required_keys:
        if key not in package:
            raise ValueError(
                f"Model bundle thiếu thành phần: {key}"
            )

    # Kiểm tra số lượng features.
    if len(package["feature_columns"]) != 29:
        raise ValueError(
            "Model phải sử dụng đúng 29 features."
        )

    # Kiểm tra dữ liệu tham chiếu.
    sorted_scores = np.asarray(
        package["sorted_train_scores"],
        dtype=np.float64,
    )

    if sorted_scores.size == 0:
        raise ValueError(
            "Dữ liệu tham chiếu anomaly score bị rỗng."
        )

    if not np.all(np.isfinite(sorted_scores)):
        raise ValueError(
            "Dữ liệu tham chiếu chứa NaN hoặc Infinity."
        )

    if not np.all(np.diff(sorted_scores) >= 0):
        raise ValueError(
            "Dữ liệu tham chiếu chưa được sắp xếp."
        )

    package["sorted_train_scores"] = sorted_scores

    return package


# =========================================================
# 3. VALIDATE GIAO DỊCH
# =========================================================

def validate_transaction(transaction):
    """
    Kiểm tra dữ liệu đầu vào của một giao dịch.
    """

    if not isinstance(transaction, dict):
        raise ValueError(
            "Mỗi giao dịch phải là một object."
        )

    missing_columns = [
        column
        for column in INPUT_COLUMNS
        if column not in transaction
    ]

    if missing_columns:
        raise ValueError(
            f"Thiếu các trường: {missing_columns}"
        )

    values = {}

    for column in INPUT_COLUMNS:
        value = transaction[column]

        if isinstance(value, bool):
            raise ValueError(
                f"Trường {column} không được là boolean."
            )

        if not isinstance(value, (int, float, np.number)):
            raise ValueError(
                f"Trường {column} phải là số."
            )

        value = float(value)

        if not np.isfinite(value):
            raise ValueError(
                f"Trường {column} phải là số hữu hạn."
            )

        values[column] = value

    if values["time"] < 0:
        raise ValueError(
            "Time không được âm."
        )

    if values["amount"] < 0:
        raise ValueError(
            "Amount không được âm."
        )

    return values


# =========================================================
# 4. TẠO VECTOR FEATURES
# =========================================================

def build_feature_vector(transaction, feature_columns):
    """
    Chuyển giao dịch thành vector 29 features.

    Thứ tự features lấy trực tiếp từ model bundle.
    Time không được đưa vào mô hình.
    """

    values = validate_transaction(transaction)

    feature_values = []

    for feature in feature_columns:
        input_name = feature.lower()

        if input_name not in values:
            raise ValueError(
                f"Không tìm thấy feature: {input_name}"
            )

        feature_values.append(
            values[input_name]
        )

    return np.asarray(
        feature_values,
        dtype=np.float64,
    ).reshape(1, -1)


# =========================================================
# 5. PREPROCESSING CHO ISOLATION FOREST
# =========================================================


def scale_features(X_raw, scaler):
    """
    Chuẩn hóa dữ liệu bằng StandardScaler.

    Luôn truyền DataFrame có tên cột đúng như lúc fit.
    """

    # Lấy tên feature mà Scaler đã sử dụng khi huấn luyện.
    if not hasattr(scaler, "feature_names_in_"):
        raise ValueError(
            "Scaler không lưu feature_names_in_. "
            "Cần kiểm tra lại bước prepare_data.py."
        )

    feature_names = list(scaler.feature_names_in_)

    if len(feature_names) != X_raw.shape[1]:
        raise ValueError(
            "Số feature đầu vào không khớp với Scaler."
        )

    # Chuyển NumPy array thành DataFrame có tên cột.
    X_dataframe = pd.DataFrame(
        X_raw,
        columns=feature_names,
    )

    # Chuẩn hóa.
    return scaler.transform(X_dataframe)



# =========================================================
# 6. TÍNH ANOMALY SCORE
# =========================================================

def calculate_anomaly_score(
    isolation_model,
    scaler,
    sorted_train_scores,
    X_raw,
):
    """
    Tính điểm bất thường từ 0 đến 100.

    Isolation Forest:
    score_samples càng thấp -> càng bất thường.

    Quy đổi:
    So sánh raw score của giao dịch với phân phối
    raw score trên tập Train.

    Điểm càng cao -> mức bất thường càng cao.
    """

    X_scaled = scale_features(
        X_raw,
        scaler,
    )

    raw_score = float(
        isolation_model.score_samples(X_scaled)[0]
    )

    rank = np.searchsorted(
        sorted_train_scores,
        raw_score,
        side="right",
    )

    anomaly_score = (
        1.0 - rank / len(sorted_train_scores)
    ) * 100.0

    anomaly_score = float(
        np.clip(anomaly_score, 0.0, 100.0)
    )

    return round(anomaly_score, 4)


# =========================================================
# 7. TÍNH FRAUD PROBABILITY
# =========================================================

def calculate_fraud_probability(
    random_forest,
    X_raw,
):
    """
    Random Forest dự đoán xác suất Class = 1.

    Kết quả trả về theo thang 0-100.

    Lưu ý:
    predict_proba chưa được calibration.
    Đây là điểm xác suất mô hình ước lượng,
    không phải xác suất đã hiệu chỉnh.
    """

    probabilities = random_forest.predict_proba(
        X_raw
    )

    fraud_probability = float(
        probabilities[0, 1]
    )

    return round(
        float(
            np.clip(
                fraud_probability * 100.0,
                0.0,
                100.0,
            )
        ),
        4,
    )


# =========================================================
# 8. LẤY TOP FEATURES
# =========================================================

def get_top_features(feature_importances):
    """
    Lấy TOP 5 feature importance của Random Forest.

    Đây là mức độ quan trọng toàn cục của mô hình,
    không phải nguyên nhân cụ thể của từng giao dịch.
    """

    sorted_features = sorted(
        feature_importances.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        {
            "feature": feature,
            "importance": round(
                float(importance),
                6,
            ),
        }
        for feature, importance in sorted_features[
            :TOP_FEATURE_COUNT
        ]
    ]


# =========================================================
# 9. CHẤM ĐIỂM MỘT GIAO DỊCH
# =========================================================

def score_transaction(transaction, package):
    """
    Chấm điểm một giao dịch bằng hai mô hình.
    """

    X_raw = build_feature_vector(
        transaction,
        package["feature_columns"],
    )

    anomaly_score = calculate_anomaly_score(
        package["isolation_forest"],
        package["scaler"],
        package["sorted_train_scores"],
        X_raw,
    )

    fraud_probability = calculate_fraud_probability(
        package["random_forest"],
        X_raw,
    )

    top_features = get_top_features(
        package["feature_importances"]
    )

    return {
        "anomaly_score": anomaly_score,
        "fraud_probability": fraud_probability,
        "top_features": top_features,
        "model_version": package["model_version"],
    }


# =========================================================
# 10. CHẤM ĐIỂM NHIỀU GIAO DỊCH
# =========================================================

def score_transactions(transactions, package):
    """
    Chấm điểm tối đa 1000 giao dịch mỗi lần.

    Nếu một giao dịch không hợp lệ:
    trả lỗi và không trả kết quả một phần.
    """

    if not isinstance(transactions, list):
        raise ValueError(
            "transactions phải là một danh sách."
        )

    if len(transactions) == 0:
        raise ValueError(
            "Danh sách giao dịch không được rỗng."
        )

    if len(transactions) > MAX_BATCH_SIZE:
        raise ValueError(
            f"Mỗi batch tối đa {MAX_BATCH_SIZE} giao dịch."
        )

    results = []

    for index, transaction in enumerate(transactions):
        try:
            result = score_transaction(
                transaction,
                package,
            )

            results.append(result)

        except (ValueError, TypeError) as error:
            raise ValueError(
                f"Giao dịch tại vị trí {index} không hợp lệ: {error}"
            ) from error

    return results


# =========================================================
# 11. CHẠY THỬ ĐỘC LẬP
# =========================================================

if __name__ == "__main__":

    print("========== 1. LOAD MODEL ==========")

    model_package = load_model()

    print(
        "Model version:",
        model_package["model_version"],
    )

    print(
        "Số features:",
        len(model_package["feature_columns"]),
    )

    print("\n========== 2. TẠO GIAO DỊCH THỬ ==========")

    # Chỉ lấy một dòng từ tập Test đã chuẩn bị.
    # Không thay đổi dữ liệu gốc.
    prepared_data = joblib.load(
        PREPARED_DATA_PATH
    )

    X_test_raw = prepared_data["X_test_raw"]

    if len(X_test_raw) == 0:
        raise ValueError(
            "Tập Test không có dữ liệu."
        )

    sample = np.asarray(
        X_test_raw[0],
        dtype=np.float64,
    )

    transaction = {
        "time": 150000.0,
        "amount": float(sample[0]),
    }

    for index in range(1, 29):
        transaction[f"v{index}"] = float(
            sample[index]
        )

    print("\n========== 3. CHẤM ĐIỂM ==========")

    result = score_transaction(
        transaction,
        model_package,
    )

    print("Kết quả:")
    print(result)

    print("\n========== 4. KIỂM TRA BATCH ==========")

    batch_results = score_transactions(
        [transaction, transaction],
        model_package,
    )

    print(
        "Số giao dịch đã chấm điểm:",
        len(batch_results),
    )

    print("\n========== SCORING HOÀN TẤT ==========")
