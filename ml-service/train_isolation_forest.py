
"""
Huấn luyện Isolation Forest để phát hiện giao dịch bất thường.

- Không sử dụng Class khi huấn luyện.
- Chỉ huấn luyện trên X_train_scaled.
- Dùng dữ liệu Test để đánh giá sau khi huấn luyện.
- Lưu model và thông tin cần thiết để sử dụng khi inference.
"""

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
)


# =========================================================
# 1. CẤU HÌNH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

PREPARED_DATA_PATH = OUTPUT_DIR / "prepared_data.joblib"

# Tỷ lệ giao dịch được đưa vào nhóm cảnh báo ban đầu.
# Đây là ngưỡng vận hành thử nghiệm, không phải xác suất gian lận.
ALERT_RATE = 0.002

RANDOM_STATE = 42


# =========================================================
# 2. ĐỌC DỮ LIỆU ĐÃ CHUẨN BỊ
# =========================================================

print("========== 1. ĐỌC DỮ LIỆU ==========")

if not PREPARED_DATA_PATH.exists():
    raise FileNotFoundError(
        f"Không tìm thấy file: {PREPARED_DATA_PATH}"
    )

prepared_data = joblib.load(PREPARED_DATA_PATH)

X_train = prepared_data["X_train_scaled"]
X_test = prepared_data["X_test_scaled"]

y_test = prepared_data["y_test"]

print(f"X_train: {X_train.shape}")
print(f"X_test: {X_test.shape}")
print(f"Số giao dịch gian lận trong Test: {int(np.sum(y_test))}")


# =========================================================
# 3. KHỞI TẠO ISOLATION FOREST
# =========================================================

print("\n========== 2. KHỞI TẠO MÔ HÌNH ==========")

model = IsolationForest(
    n_estimators=300,
    contamination="auto",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

print("Đã khởi tạo Isolation Forest.")
print("Số cây:", 300)


# =========================================================
# 4. HUẤN LUYỆN
# =========================================================

print("\n========== 3. HUẤN LUYỆN ==========")

# Không truyền y_train vào model.
# Isolation Forest học cấu trúc dữ liệu mà không cần nhãn.
model.fit(X_train)

print("Huấn luyện hoàn tất.")


# =========================================================
# 5. TÍNH ĐIỂM BẤT THƯỜNG
# =========================================================

print("\n========== 4. TÍNH ANOMALY SCORE ==========")

# score_samples càng thấp thì càng bất thường.
train_scores = model.score_samples(X_train)
test_scores = model.score_samples(X_test)

# Sắp xếp điểm Train để quy đổi điểm Test thành thang 0-100.
sorted_train_scores = np.sort(train_scores)

# Ngưỡng cảnh báo được xác định từ Train.
threshold = np.quantile(train_scores, ALERT_RATE)

# Lưu model và thông tin cần thiết cho bước inference.
isolation_model_path = OUTPUT_DIR / "isolation_forest_model.joblib"

joblib.dump(
    {
        "model": model,
        "sorted_train_scores": sorted_train_scores,
        "raw_score_threshold": float(threshold),
        "alert_rate": ALERT_RATE,
    },
    isolation_model_path,
)

print(f"Đã lưu Isolation Forest: {isolation_model_path}")

# Đếm tỷ lệ điểm Train lớn hơn hoặc bằng điểm của giao dịch.
# Điểm càng thấp thì anomaly_score càng cao.
anomaly_scores = (
                         (
                                 len(sorted_train_scores)
                                 - np.searchsorted(
                             sorted_train_scores,
                             test_scores,
                             side="left",
                         )
                         )
                         / len(sorted_train_scores)
                 ) * 100

anomaly_scores = np.clip(anomaly_scores, 0, 100)

# Điểm thấp hơn hoặc bằng threshold được đánh dấu bất thường.
y_pred = (test_scores <= threshold).astype(int)

print(f"Anomaly score nhỏ nhất: {anomaly_scores.min():.4f}")
print(f"Anomaly score lớn nhất: {anomaly_scores.max():.4f}")
print(f"Ngưỡng cảnh báo score_samples: {threshold:.6f}")
print(f"Tỷ lệ cảnh báo mục tiêu: {ALERT_RATE * 100:.2f}%")


# =========================================================
# 6. ĐÁNH GIÁ
# =========================================================

print("\n========== 5. ĐÁNH GIÁ MÔ HÌNH ==========")

# Đảo dấu vì score_samples càng thấp thì càng bất thường.
# Average Precision được sử dụng làm chỉ số PR-AUC.
pr_auc = average_precision_score(y_test, -test_scores)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0,
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0,
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0,
)

print(f"Precision: {precision:.6f}")
print(f"Recall:    {recall:.6f}")
print(f"F1-score:  {f1:.6f}")
print(f"PR-AUC:    {pr_auc:.6f}")

print(f"Số giao dịch bị cảnh báo: {int(y_pred.sum())}")
print(f"Số giao dịch gian lận thực tế: {int(np.sum(y_test))}")


# =========================================================
# 7. LƯU KẾT QUẢ
# =========================================================

print("\n========== 6. LƯU KẾT QUẢ ==========")

results = pd.DataFrame({
    "actual_class": y_test,
    "anomaly_score": anomaly_scores,
    "raw_anomaly_score": test_scores,
    "predicted_anomaly": y_pred,
})

results_path = OUTPUT_DIR / "isolation_forest_results.csv"

results.to_csv(
    results_path,
    index=False,
)

metrics = {
    "model": "IsolationForest",
    "pr_auc": float(pr_auc),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
    "alert_rate": ALERT_RATE,
    "raw_score_threshold": float(threshold),
    "n_estimators": 300,
    "preprocessing_version": prepared_data["preprocessing_version"],
}

metrics_path = OUTPUT_DIR / "isolation_forest_metrics.json"

with open(metrics_path, "w", encoding="utf-8") as file:
    json.dump(
        metrics,
        file,
        indent=4,
        ensure_ascii=False,
    )

print(f"Đã lưu kết quả: {results_path}")
print(f"Đã lưu metrics: {metrics_path}")

print("\n========== HOÀN TẤT ==========")
