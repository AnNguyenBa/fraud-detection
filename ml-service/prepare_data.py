
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler


# ==========================================
# 1. Khai báo đường dẫn
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

TRAIN_PATH = OUTPUT_DIR / "train_data.csv"
TEST_PATH = OUTPUT_DIR / "test_data.csv"

OUTPUT_FILE = OUTPUT_DIR / "prepared_data.joblib"


# ==========================================
# 2. Khai báo các cột đầu vào
# ==========================================

FEATURE_COLUMNS = [
    "Amount",
    *[f"V{i}" for i in range(1, 29)]
]

LABEL_COLUMN = "Class"
TIME_COLUMN = "Time"


# ==========================================
# 3. Đọc dữ liệu
# ==========================================

print("========== 1. ĐỌC DỮ LIỆU ==========")

if not TRAIN_PATH.exists():
    raise FileNotFoundError(f"Không tìm thấy: {TRAIN_PATH}")

if not TEST_PATH.exists():
    raise FileNotFoundError(f"Không tìm thấy: {TEST_PATH}")

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

print(f"Train: {len(train_df):,} dòng")
print(f"Test: {len(test_df):,} dòng")


# ==========================================
# 4. Kiểm tra dữ liệu
# ==========================================

print("\n========== 2. KIỂM TRA DỮ LIỆU ==========")

required_columns = [
    TIME_COLUMN,
    *FEATURE_COLUMNS,
    LABEL_COLUMN
]

for name, data in [
    ("Train", train_df),
    ("Test", test_df)
]:
    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{name} thiếu cột: {missing_columns}"
        )

    if data[required_columns].isnull().any().any():
        raise ValueError(
            f"{name} có giá trị thiếu."
        )

    if not np.isfinite(
            data[FEATURE_COLUMNS].to_numpy(dtype=float)
    ).all():
        raise ValueError(
            f"{name} có giá trị NaN hoặc vô cực trong features."
        )

    if not data[LABEL_COLUMN].isin([0, 1]).all():
        raise ValueError(
            f"{name} có nhãn Class không hợp lệ."
        )

print("Không có cột bị thiếu.")
print("Không có giá trị thiếu.")
print("Features đều là giá trị hữu hạn.")
print("Nhãn Class hợp lệ.")


# ==========================================
# 5. Tách Features và Label
# ==========================================

print("\n========== 3. TÁCH FEATURES VÀ LABEL ==========")

# X: thông tin giao dịch dùng để dự đoán
X_train = train_df[FEATURE_COLUMNS].astype(float)
X_test = test_df[FEATURE_COLUMNS].astype(float)

# y: nhãn thực tế, chỉ dùng cho huấn luyện
# và đánh giá mô hình supervised
y_train = train_df[LABEL_COLUMN].astype(int)
y_test = test_df[LABEL_COLUMN].astype(int)

print(f"Số features: {len(FEATURE_COLUMNS)}")
print(f"X_train: {X_train.shape}")
print(f"X_test: {X_test.shape}")

print(f"Fraud trong train: {(y_train == 1).sum()}")
print(f"Fraud trong test: {(y_test == 1).sum()}")


# ==========================================
# 6. Chuẩn hóa dữ liệu cho Isolation Forest
# ==========================================

print("\n========== 4. STANDARD SCALER ==========")

scaler = StandardScaler()

# Chỉ học mean và standard deviation từ Train
X_train_scaled = scaler.fit_transform(X_train)

# Test chỉ được transform, không được fit
X_test_scaled = scaler.transform(X_test)

print("Đã fit scaler trên Train.")
print("Đã transform Train và Test.")

print(
    "Train scaled mean trung bình:",
    round(float(X_train_scaled.mean()), 6)
)

print(
    "Train scaled std trung bình:",
    round(float(X_train_scaled.std()), 6)
)


# ==========================================
# 7. Chuyển dữ liệu về numpy array
# ==========================================

print("\n========== 5. CHUẨN BỊ DỮ LIỆU ==========")

prepared_data = {
    "feature_columns": FEATURE_COLUMNS,

    # Dữ liệu chưa chuẩn hóa cho Random Forest
    "X_train_raw": X_train.to_numpy(),
    "X_test_raw": X_test.to_numpy(),

    # Dữ liệu chuẩn hóa cho Isolation Forest
    "X_train_scaled": X_train_scaled,
    "X_test_scaled": X_test_scaled,

    # Nhãn thực tế
    "y_train": y_train.to_numpy(),
    "y_test": y_test.to_numpy(),

    # Scaler dùng lại khi dự đoán giao dịch mới
    "scaler": scaler,

    # Thông tin phiên bản tiền xử lý
    "preprocessing_version": "v1"
}


# ==========================================
# 8. Lưu dữ liệu đã xử lý
# ==========================================

joblib.dump(
    prepared_data,
    OUTPUT_FILE,
    compress=3
)

print("\n========== 6. LƯU KẾT QUẢ ==========")
print(f"Đã lưu: {OUTPUT_FILE}")

print("\n========== HOÀN TẤT ==========")
