
from pathlib import Path

import pandas as pd
import matplotlib

# Sử dụng chế độ không cần mở cửa sổ biểu đồ
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# Đường dẫn dự án
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Đường dẫn dataset
DATASET_PATH = PROJECT_ROOT / "data" / "creditcard.csv"

# Thư mục lưu biểu đồ
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def analyze_duplicates(df):
    print("\n========== 1. PHÂN TÍCH BẢN GHI TRÙNG ==========")

    # Các bản ghi trùng tính từ lần xuất hiện thứ hai
    duplicated_rows = df[df.duplicated(keep="first")]

    print(f"Tổng bản ghi trùng: {len(duplicated_rows):,}")

    print("\nBản ghi trùng theo Class:")
    print(duplicated_rows["Class"].value_counts().sort_index())

    # Tất cả các dòng tham gia vào nhóm trùng, bao gồm cả dòng đầu tiên
    duplicate_groups = df[df.duplicated(keep=False)]

    print("\nTổng số dòng tham gia vào các nhóm trùng:")
    print(f"{len(duplicate_groups):,}")

    # Kiểm tra cùng đặc trưng nhưng khác Class
    feature_columns = [
        column for column in df.columns if column != "Class"
    ]

    label_conflicts = (
        df.groupby(feature_columns, dropna=False)["Class"]
        .nunique()
    )

    conflict_count = (label_conflicts > 1).sum()

    print(
        "\nSố nhóm có cùng đặc trưng nhưng khác nhãn: "
        f"{conflict_count:,}"
    )


def analyze_class_distribution(df):
    print("\n========== 2. PHÂN BỐ CLASS ==========")

    counts = df["Class"].value_counts().sort_index()

    for class_value, count in counts.items():
        percentage = count / len(df) * 100

        label = (
            "Bình thường" if class_value == 0 else "Gian lận"
        )

        print(
            f"{label}: {count:,} "
            f"({percentage:.4f}%)"
        )


def analyze_time(df):
    print("\n========== 3. PHÂN TÍCH TIME ==========")

    # Dataset sử dụng Time tính bằng giây
    # Chia thành các khoảng một giờ
    df_time = df.copy()
    df_time["Hour"] = (df_time["Time"] // 3600).astype(int)

    time_summary = (
        df_time.groupby(["Hour", "Class"])
        .size()
        .unstack(fill_value=0)
    )

    print(time_summary)

    # Vẽ biểu đồ số lượng giao dịch theo giờ
    ax = time_summary.plot(
        kind="bar",
        figsize=(12, 5),
        width=0.8
    )

    ax.set_title("Number of Transactions by Time Interval")
    ax.set_xlabel("Hour interval")
    ax.set_ylabel("Number of transactions")
    ax.legend(["Normal (0)", "Fraud (1)"])

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "transactions_by_time.png")
    plt.close()


def analyze_amount(df):
    print("\n========== 4. PHÂN TÍCH AMOUNT ==========")

    amount_summary = df.groupby("Class")["Amount"].describe()

    print(amount_summary)

    # Log1p giúp biểu diễn dữ liệu Amount có độ lệch lớn
    df_plot = df.copy()
    df_plot["LogAmount"] = (
        df_plot["Amount"].apply(lambda value: __import__("math").log1p(value))
    )

    plt.figure(figsize=(10, 5))

    for class_value, label in [
        (0, "Normal"),
        (1, "Fraud")
    ]:
        values = df_plot.loc[
            df_plot["Class"] == class_value,
            "LogAmount"
        ]

        plt.hist(
            values,
            bins=50,
            alpha=0.5,
            density=True,
            label=label
        )

    plt.title("Log-transformed Transaction Amount Distribution")
    plt.xlabel("log(1 + Amount)")
    plt.ylabel("Density")
    plt.legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "amount_distribution.png")
    plt.close()


def analyze_features(df):
    print("\n========== 5. PHÂN TÍCH V1-V28 ==========")

    feature_columns = [
        f"V{i}" for i in range(1, 29)
    ]

    # Thống kê các đặc trưng theo từng lớp
    summary = df.groupby("Class")[feature_columns].agg(
        ["mean", "std", "median"]
    )

    print(summary.to_string())

    # Vẽ phân bố từng đặc trưng
    fig, axes = plt.subplots(
        nrows=7,
        ncols=4,
        figsize=(18, 24)
    )

    for index, feature in enumerate(feature_columns):
        ax = axes[index // 4, index % 4]

        for class_value, label in [
            (0, "Normal"),
            (1, "Fraud")
        ]:
            values = df.loc[
                df["Class"] == class_value,
                feature
            ]

            ax.hist(
                values,
                bins=40,
                alpha=0.5,
                density=True,
                label=label
            )

        ax.set_title(feature)
        ax.legend(fontsize=7)

    plt.suptitle("Distribution of V1-V28 by Class")
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "feature_distributions.png")
    plt.close()


def explore_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dataset: {DATASET_PATH}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Đang đọc dataset...")
    df = pd.read_csv(DATASET_PATH)

    # Kiểm tra các cột bắt buộc
    required_columns = (
            ["Time"]
            + [f"V{i}" for i in range(1, 29)]
            + ["Amount", "Class"]
    )

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset thiếu các cột: {missing_columns}"
        )

    analyze_duplicates(df)
    analyze_class_distribution(df)
    analyze_time(df)
    analyze_amount(df)
    analyze_features(df)

    print("\n========== HOÀN TẤT ==========")
    print(f"Biểu đồ được lưu tại: {OUTPUT_DIR}")


if __name__ == "__main__":
    explore_dataset()
