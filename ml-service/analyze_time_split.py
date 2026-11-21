
from pathlib import Path

import pandas as pd


# ==============================
# 1. Khai báo đường dẫn
# ==============================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR.parent / "data" / "creditcard.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==============================
# 2. Đọc dữ liệu
# ==============================

df = pd.read_csv(DATA_PATH)

print("========== THÔNG TIN DỮ LIỆU ==========")
print(f"Tổng số giao dịch: {len(df):,}")
print(f"Time nhỏ nhất: {df['Time'].min()}")
print(f"Time lớn nhất: {df['Time'].max()}")


# ==============================
# 3. Kiểm tra thứ tự thời gian
# ==============================

is_sorted = df["Time"].is_monotonic_increasing

print("\n========== KIỂM TRA THỨ TỰ ==========")
print(f"Dữ liệu đã sắp xếp theo Time: {is_sorted}")

# Sắp xếp theo Time tăng dần.
# mergesort giữ thứ tự ban đầu của các dòng có cùng Time.
df = df.sort_values(
    by="Time",
    ascending=True,
    kind="mergesort"
).reset_index(drop=True)


# ==============================
# 4. Chia train/test theo thời gian
# ==============================

train_ratio = 0.8

# Vị trí dự kiến của mốc chia 80/20
split_index = int(len(df) * train_ratio)

# Lấy Time tại vị trí chia
cutoff_time = df.iloc[split_index]["Time"]

# Không chia các giao dịch có cùng Time sang hai tập khác nhau.
train_df = df[df["Time"] < cutoff_time].copy()
test_df = df[df["Time"] >= cutoff_time].copy()


# ==============================
# 5. Thống kê hai tập dữ liệu
# ==============================

def print_dataset_info(name, data):
    total = len(data)

    normal_count = int((data["Class"] == 0).sum())
    fraud_count = int((data["Class"] == 1).sum())

    fraud_rate = (
        fraud_count / total * 100
        if total > 0
        else 0
    )

    print(f"\n========== {name} ==========")
    print(f"Tổng giao dịch: {total:,}")
    print(f"Giao dịch bình thường: {normal_count:,}")
    print(f"Giao dịch gian lận: {fraud_count:,}")
    print(f"Tỷ lệ gian lận: {fraud_rate:.4f}%")

    if total > 0:
        print(f"Time nhỏ nhất: {data['Time'].min()}")
        print(f"Time lớn nhất: {data['Time'].max()}")


print_dataset_info("TRAIN", train_df)
print_dataset_info("TEST", test_df)


# ==============================
# 6. Kiểm tra ranh giới thời gian
# ==============================

print("\n========== KIỂM TRA RANH GIỚI ==========")

if not train_df.empty and not test_df.empty:
    train_max_time = train_df["Time"].max()
    test_min_time = test_df["Time"].min()

    print(f"Time lớn nhất của train: {train_max_time}")
    print(f"Time nhỏ nhất của test: {test_min_time}")

    print(
        "Không trùng Time giữa train và test:",
        train_max_time < test_min_time
    )
else:
    print("Không thể kiểm tra vì một trong hai tập rỗng.")


# ==============================
# 7. Thống kê gian lận theo khoảng
#    3600 giây trong Time
# ==============================

df["time_interval"] = (
        df["Time"] // 3600
).astype(int)

time_stats = (
    df.groupby("time_interval")
    .agg(
        total_transactions=("Class", "count"),
        fraud_transactions=("Class", "sum")
    )
    .reset_index()
)

time_stats["normal_transactions"] = (
        time_stats["total_transactions"]
        - time_stats["fraud_transactions"]
)

time_stats.to_csv(
    OUTPUT_DIR / "fraud_by_time_interval.csv",
    index=False
)


# ==============================
# 8. Xuất báo cáo tổng hợp
# ==============================

summary = {
    "total_transactions": len(df),
    "originally_sorted_by_time": bool(is_sorted),
    "train_ratio_target": train_ratio,
    "cutoff_time": float(cutoff_time),
    "train_transactions": len(train_df),
    "test_transactions": len(test_df),
    "train_fraud": int((train_df["Class"] == 1).sum()),
    "test_fraud": int((test_df["Class"] == 1).sum()),
    "train_normal": int((train_df["Class"] == 0).sum()),
    "test_normal": int((test_df["Class"] == 0).sum()),
}

summary_df = pd.DataFrame(
    [summary]
)

summary_df.to_csv(
    OUTPUT_DIR / "time_split_summary.csv",
    index=False
)

# Lưu dữ liệu đã chia để các bước sau có thể sử dụng.
# Đây là dữ liệu trung gian, không phải dữ liệu gốc.
train_df.to_csv(
    OUTPUT_DIR / "train_data.csv",
    index=False
)

test_df.to_csv(
    OUTPUT_DIR / "test_data.csv",
    index=False
)


print("\n========== HOÀN TẤT ==========")
print(f"Ngưỡng chia Time: {cutoff_time}")
print(f"Thư mục kết quả: {OUTPUT_DIR}")
print("Đã xuất:")
print("- time_split_summary.csv")
print("- fraud_by_time_interval.csv")
print("- train_data.csv")
print("- test_data.csv")
