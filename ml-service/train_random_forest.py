
"""
Huấn luyện Random Forest để phân loại giao dịch gian lận.

- Sử dụng Class khi huấn luyện.
- Xử lý mất cân bằng dữ liệu bằng class_weight.
- Không sử dụng Test để huấn luyện.
- Đánh giá bằng Precision, Recall, F1-score và PR-AUC.
"""

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


# =========================================================
# 1. CẤU HÌNH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

PREPARED_DATA_PATH = OUTPUT_DIR / "prepared_data.joblib"

RANDOM_STATE = 42

# Ngưỡng phân loại ban đầu.
# Chưa tối ưu ngưỡng dựa trên Test.
CLASSIFICATION_THRESHOLD = 0.5


# =========================================================
# 2. ĐỌC DỮ LIỆU
# =========================================================

print("========== 1. ĐỌC DỮ LIỆU ==========")

if not PREPARED_DATA_PATH.exists():
    raise FileNotFoundError(
        f"Không tìm thấy file: {PREPARED_DATA_PATH}"
    )

prepared_data = joblib.load(PREPARED_DATA_PATH)

# Random Forest sử dụng dữ liệu gốc, không cần StandardScaler.
X_train = prepared_data["X_train_raw"]
X_test = prepared_data["X_test_raw"]

y_train = prepared_data["y_train"]
y_test = prepared_data["y_test"]

feature_columns = prepared_data["feature_columns"]

print(f"X_train: {X_train.shape}")
print(f"X_test: {X_test.shape}")

print(f"Fraud trong Train: {int(np.sum(y_train))}")
print(f"Fraud trong Test: {int(np.sum(y_test))}")


# =========================================================
# 3. KHỞI TẠO RANDOM FOREST
# =========================================================

print("\n========== 2. KHỞI TẠO MÔ HÌNH ==========")

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=16,
    min_samples_leaf=2,
    max_features="sqrt",
    class_weight="balanced_subsample",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

print("Đã khởi tạo Random Forest.")
print("Số cây:", 300)
print("Max depth:", 16)
print("Class weight: balanced_subsample")


# =========================================================
# 4. HUẤN LUYỆN
# =========================================================

print("\n========== 3. HUẤN LUYỆN ==========")

model.fit(X_train, y_train)

print("Huấn luyện hoàn tất.")


# =========================================================
# 5. DỰ ĐOÁN
# =========================================================

print("\n========== 4. DỰ ĐOÁN ==========")

# Lấy xác suất dự đoán cho Class = 1.
fraud_class_index = list(model.classes_).index(1)

fraud_probability = model.predict_proba(X_test)[
    :, fraud_class_index
]

# Phân loại dựa trên ngưỡng 0.5.
y_pred = (
        fraud_probability >= CLASSIFICATION_THRESHOLD
).astype(int)

print("Đã dự đoán trên tập Test.")
print(f"Ngưỡng phân loại: {CLASSIFICATION_THRESHOLD}")


# =========================================================
# 6. ĐÁNH GIÁ
# =========================================================

print("\n========== 5. ĐÁNH GIÁ MÔ HÌNH ==========")

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

# Average Precision là cách tính PR-AUC được dùng ở đây.
pr_auc = average_precision_score(
    y_test,
    fraud_probability,
)

tn, fp, fn, tp = confusion_matrix(
    y_test,
    y_pred,
    labels=[0, 1],
).ravel()

print(f"Precision: {precision:.6f}")
print(f"Recall:    {recall:.6f}")
print(f"F1-score:  {f1:.6f}")
print(f"PR-AUC:    {pr_auc:.6f}")

print("\nConfusion Matrix:")
print(f"True Positive:  {tp}")
print(f"False Positive: {fp}")
print(f"True Negative:  {tn}")
print(f"False Negative: {fn}")

print(f"\nSố giao dịch bị dự đoán gian lận: {int(y_pred.sum())}")
print(f"Số giao dịch gian lận thực tế: {int(np.sum(y_test))}")


# =========================================================
# 7. PHÂN TÍCH FEATURE IMPORTANCE
# =========================================================

print("\n========== 6. FEATURE IMPORTANCE ==========")

importance_df = pd.DataFrame({
    "feature": feature_columns,
    "importance": model.feature_importances_,
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False,
)

print("\nTop 10 features quan trọng nhất:")
print(importance_df.head(10).to_string(index=False))

importance_path = OUTPUT_DIR / "random_forest_feature_importance.csv"

importance_df.to_csv(
    importance_path,
    index=False,
)


# =========================================================
# 8. LƯU KẾT QUẢ
# =========================================================

print("\n========== 7. LƯU KẾT QUẢ ==========")

results = pd.DataFrame({
    "actual_class": y_test,
    "fraud_probability": fraud_probability,
    "predicted_class": y_pred,
})

results_path = OUTPUT_DIR / "random_forest_results.csv"

results.to_csv(
    results_path,
    index=False,
)

metrics = {
    "model": "RandomForestClassifier",
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
    "pr_auc": float(pr_auc),
    "threshold": CLASSIFICATION_THRESHOLD,
    "true_positive": int(tp),
    "false_positive": int(fp),
    "true_negative": int(tn),
    "false_negative": int(fn),
    "n_estimators": 300,
    "max_depth": 16,
    "preprocessing_version": prepared_data["preprocessing_version"],
}

metrics_path = OUTPUT_DIR / "random_forest_metrics.json"

with open(metrics_path, "w", encoding="utf-8") as file:
    json.dump(
        metrics,
        file,
        indent=4,
        ensure_ascii=False,
    )

# Lưu model để có thể sử dụng lại, không cần huấn luyện lại.
model_path = OUTPUT_DIR / "random_forest_model.joblib"

joblib.dump(model, model_path)

print(f"Đã lưu kết quả: {results_path}")
print(f"Đã lưu metrics: {metrics_path}")
print(f"Đã lưu feature importance: {importance_path}")
print(f"Đã lưu model: {model_path}")

print("\n========== HOÀN TẤT ==========")
