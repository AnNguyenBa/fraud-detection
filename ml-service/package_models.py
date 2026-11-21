
"""
Đóng gói các thành phần ML thành một file duy nhất.

Bao gồm:
- Random Forest
- Isolation Forest
- StandardScaler
- Danh sách features
- Dữ liệu tham chiếu tính anomaly_score
- Các ngưỡng dự đoán
- Feature importance
- Model version
"""

from pathlib import Path

import joblib
import numpy as np


# =========================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"

PREPARED_DATA_PATH = OUTPUT_DIR / "prepared_data.joblib"
RANDOM_FOREST_PATH = OUTPUT_DIR / "random_forest_model.joblib"
ISOLATION_FOREST_PATH = OUTPUT_DIR / "isolation_forest_model.joblib"

OUTPUT_MODEL_PATH = MODEL_DIR / "fraud_detection_v1.joblib"

MODEL_VERSION = "v1"
RF_THRESHOLD = 0.5


# =========================================================
# 2. KIỂM TRA FILE ĐẦU VÀO
# =========================================================

print("========== 1. KIỂM TRA FILE ==========")

required_files = [
    PREPARED_DATA_PATH,
    RANDOM_FOREST_PATH,
    ISOLATION_FOREST_PATH,
]

for file_path in required_files:
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy file: {file_path}"
        )

    print(f"Đã tìm thấy: {file_path.name}")


# =========================================================
# 3. ĐỌC CÁC THÀNH PHẦN
# =========================================================

print("\n========== 2. ĐỌC MODEL VÀ PREPROCESSING ==========")

prepared_data = joblib.load(PREPARED_DATA_PATH)
random_forest = joblib.load(RANDOM_FOREST_PATH)
isolation_data = joblib.load(ISOLATION_FOREST_PATH)

scaler = prepared_data["scaler"]
feature_columns = list(prepared_data["feature_columns"])

isolation_forest = isolation_data["model"]
sorted_train_scores = np.asarray(
    isolation_data["sorted_train_scores"],
    dtype=np.float64,
)

isolation_threshold = float(
    isolation_data["raw_score_threshold"]
)

alert_rate = float(isolation_data["alert_rate"])

preprocessing_version = prepared_data["preprocessing_version"]

print("Đã đọc xong các thành phần.")


# =========================================================
# 4. KIỂM TRA TÍNH NHẤT QUÁN
# =========================================================

print("\n========== 3. KIỂM TRA TÍNH NHẤT QUÁN ==========")

expected_features = ["Amount"] + [
    f"V{i}" for i in range(1, 29)
]

if feature_columns != expected_features:
    raise ValueError(
        "Danh sách features không đúng thứ tự mong muốn.\n"
        f"Thực tế: {feature_columns}"
    )

if len(feature_columns) != 29:
    raise ValueError("Số lượng features phải bằng 29.")

if scaler.n_features_in_ != len(feature_columns):
    raise ValueError("Số features của Scaler không khớp.")

if random_forest.n_features_in_ != len(feature_columns):
    raise ValueError("Số features của Random Forest không khớp.")

if isolation_forest.n_features_in_ != len(feature_columns):
    raise ValueError("Số features của Isolation Forest không khớp.")

if sorted_train_scores.size == 0:
    raise ValueError("Dữ liệu tham chiếu anomaly score đang rỗng.")

if not np.all(np.isfinite(sorted_train_scores)):
    raise ValueError("Dữ liệu tham chiếu chứa NaN hoặc Infinity.")

if not np.all(np.diff(sorted_train_scores) >= 0):
    raise ValueError("sorted_train_scores chưa được sắp xếp tăng dần.")

if not np.isfinite(isolation_threshold):
    raise ValueError("Isolation threshold không hợp lệ.")

if not 0 < alert_rate < 1:
    raise ValueError("Isolation alert_rate không hợp lệ.")

if not 0 < RF_THRESHOLD < 1:
    raise ValueError("Random Forest threshold không hợp lệ.")

if not hasattr(random_forest, "feature_importances_"):
    raise ValueError("Random Forest không có feature_importances_.")

if len(random_forest.feature_importances_) != len(feature_columns):
    raise ValueError("Feature importance không khớp số features.")

feature_importances = {
    feature: float(importance)
    for feature, importance in zip(
        feature_columns,
        random_forest.feature_importances_,
    )
}

print("Số features:", len(feature_columns))
print("Scaler: hợp lệ")
print("Random Forest: hợp lệ")
print("Isolation Forest: hợp lệ")
print("Dữ liệu tham chiếu: hợp lệ")
print("Feature importance: hợp lệ")


# =========================================================
# 5. ĐÓNG GÓI
# =========================================================

print("\n========== 4. ĐÓNG GÓI MODEL ==========")

MODEL_DIR.mkdir(parents=True, exist_ok=True)

model_package = {
    "model_version": MODEL_VERSION,

    # Danh sách features và thứ tự đầu vào.
    "feature_columns": feature_columns,

    # Preprocessing.
    "scaler": scaler,
    "preprocessing_version": preprocessing_version,

    # Random Forest.
    "random_forest": random_forest,
    "random_forest_threshold": RF_THRESHOLD,
    "feature_importances": feature_importances,

    # Isolation Forest.
    "isolation_forest": isolation_forest,
    "sorted_train_scores": sorted_train_scores,
    "isolation_threshold": isolation_threshold,
    "isolation_alert_rate": alert_rate,
}

joblib.dump(
    model_package,
    OUTPUT_MODEL_PATH,
    compress=3,
)

print(f"Đã đóng gói model: {OUTPUT_MODEL_PATH}")


# =========================================================
# 6. KIỂM TRA FILE SAU KHI LƯU
# =========================================================

print("\n========== 5. KIỂM TRA FILE ĐÃ ĐÓNG GÓI ==========")

loaded_package = joblib.load(OUTPUT_MODEL_PATH)

# Kiểm tra dự đoán thử bằng một dòng dữ liệu test.
X_test_raw = prepared_data["X_test_raw"]

if len(X_test_raw) == 0:
    raise ValueError("Không có dữ liệu test để kiểm tra model.")

sample = np.asarray(X_test_raw[:1], dtype=np.float64)

# Random Forest sử dụng dữ liệu chưa scale.
rf_probability = loaded_package[
    "random_forest"
].predict_proba(sample)[0, 1]

# Isolation Forest sử dụng dữ liệu đã scale.
sample_scaled = loaded_package["scaler"].transform(sample)

if_score = loaded_package[
    "isolation_forest"
].score_samples(sample_scaled)

print("Model version:", loaded_package["model_version"])
print("Số features:", len(loaded_package["feature_columns"]))

print(
    "Random Forest:",
    type(loaded_package["random_forest"]).__name__,
)

print(
    "Isolation Forest:",
    type(loaded_package["isolation_forest"]).__name__,
)

print(
    "Scaler:",
    type(loaded_package["scaler"]).__name__,
)

print("Random Forest probability mẫu:", float(rf_probability))
print("Isolation Forest raw score mẫu:", float(if_score[0]))

print("Random Forest threshold:", loaded_package["random_forest_threshold"])
print("Isolation threshold:", loaded_package["isolation_threshold"])

print(
    "Kích thước file:",
    f"{OUTPUT_MODEL_PATH.stat().st_size / (1024 * 1024):.2f} MB",
)

print("\n========== ĐÓNG GÓI HOÀN TẤT ==========")
