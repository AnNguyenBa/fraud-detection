# Fraud Detection – Machine Learning Service

## 1. Giới thiệu

ML Service là thành phần Machine Learning trong hệ thống phát hiện giao dịch thẻ tín dụng bất thường.

Hệ thống sử dụng Python và Scikit-learn để xây dựng hai mô hình:

- **Isolation Forest:** phát hiện giao dịch bất thường theo phương pháp không giám sát.
- **Random Forest:** phân loại giao dịch gian lận và ước lượng fraud score.

ML Service cung cấp REST API bằng FastAPI để Backend Java Spring Boot gửi dữ liệu giao dịch và nhận kết quả chấm điểm.

**Phạm vi:** Python ML Service không kết nối trực tiếp tới Oracle Database. Việc quản lý nghiệp vụ và dữ liệu thuộc Backend Java.

## 2. Công nghệ sử dụng

- Python 3.14.5
- Pandas
- NumPy
- Scikit-learn
- Joblib
- FastAPI
- Uvicorn
- Pytest

## 3. Cấu trúc thư mục

```text
ml-service/
├── main.py
├── scoring.py
├── explore_data.py
├── analyze_time_split.py
├── prepare_data.py
├── train_isolation_forest.py
├── train_random_forest.py
├── package_models.py
├── requirements.txt
├── models/
│   └── fraud_detection_v1.joblib
├── outputs/
│   ├── time_split_summary.csv
│   ├── fraud_by_time_interval.csv
│   ├── random_forest_metrics.json
│   ├── isolation_forest_metrics.json
│   └── ...
└── tests/
    ├── __init__.py
    ├── test_scoring.py
    └── test_api.py
```

## 4. Dataset

Sử dụng bộ dữ liệu Credit Card Fraud Detection từ Kaggle.

Đặc điểm:

- Tổng số giao dịch: 284,807.
- Giao dịch bình thường: 284,315.
- Giao dịch gian lận: 492.
- Tỷ lệ gian lận: khoảng 0.1727%.
- Số feature đầu vào: 29.

Các feature gồm Amount và V1 đến V28.

Cột Time được giữ để phục vụ phân chia dữ liệu theo thời gian, không đưa vào đầu vào của mô hình.

Lưu ý: Time là số giây tính từ giao dịch đầu tiên trong dataset, không phải giờ thực tế trong ngày.

## 5. Quy trình xử lý dữ liệu

### 5.1. Khảo sát dữ liệu

Sử dụng `explore_data.py` để:

- Kiểm tra kích thước dataset.
- Kiểm tra dữ liệu thiếu.
- Phân tích dữ liệu trùng lặp.
- Phân tích phân bố giao dịch gian lận.
- Khảo sát Amount và các feature V1–V28.

Không tự động xóa các bản ghi trùng lặp vì cần đánh giá ảnh hưởng của chúng trước khi xử lý.

### 5.2. Chia dữ liệu

Dữ liệu được chia theo thứ tự thời gian:

- Train: 80%.
- Test: 20%.

Không sử dụng random split để tránh đưa dữ liệu tương lai vào quá trình huấn luyện.

Kết quả thực tế:

| Tập dữ liệu | Tổng giao dịch | Fraud |
|---|---:|---:|
| Train | 227,845 | 417 |
| Test | 56,962 | 75 |

### 5.3. Tiền xử lý

Sử dụng StandardScaler cho Isolation Forest.

Scaler chỉ được fit trên tập Train, sau đó dùng để transform Train và Test.

Random Forest sử dụng dữ liệu feature chưa chuẩn hóa.

## 6. Huấn luyện mô hình

### 6.1. Isolation Forest

Mô hình phát hiện bất thường không cần nhãn trong quá trình huấn luyện.

Các tham số chính:

- n_estimators: 300.
- contamination: auto.
- random_state: 42.

Anomaly score được chuẩn hóa về thang 0–100 bằng percentile ranking so với phân bố score trên tập Train.

Điểm càng cao thể hiện giao dịch càng bất thường. Đây không phải xác suất gian lận.

### 6.2. Random Forest

Mô hình phân loại có giám sát.

Các tham số chính:

- n_estimators: 300.
- max_depth: 16.
- min_samples_leaf: 2.
- class_weight: balanced_subsample.
- random_state: 42.

Mô hình sử dụng predict_proba để tạo fraud score.

Lưu ý: Fraud probability hiện là xác suất đầu ra của Random Forest, chưa được hiệu chỉnh xác suất (probability calibration).

## 7. Kết quả đánh giá mô hình

Kết quả chạy thực tế trên tập Test:

### Random Forest

| Metric | Kết quả |
|---|---:|
| Precision | 98.15% |
| Recall | 70.67% |
| F1-score | 82.17% |
| PR-AUC (Average Precision) | 81.94% |

Confusion matrix:

- TP: 53
- FP: 1
- TN: 56,886
- FN: 22

### Isolation Forest

| Metric | Kết quả |
|---|---:|
| Precision | 0% |
| Recall | 0% |
| F1-score | 0% |
| PR-AUC (Average Precision) | 4.03% |

Với ngưỡng cảnh báo được chọn từ Train ở mức 0.2%, mô hình đánh dấu 74 giao dịch trên Test nhưng không phát hiện đúng giao dịch gian lận nào.

Do đó, Isolation Forest hiện chỉ đóng vai trò bổ sung để đánh giá mức độ bất thường, không nên sử dụng độc lập làm bộ phân loại gian lận.

Các kết quả trên được đo trên tập Test có 75 giao dịch gian lận, nên cần thận trọng khi khái quát sang dữ liệu thực tế.

## 8. Đóng gói mô hình

Các thành phần được đóng gói trong một file:

`models/fraud_detection_v1.joblib`

Bao gồm:

- Model Random Forest.
- Model Isolation Forest.
- StandardScaler.
- Feature columns.
- Ngưỡng Isolation Forest.
- Dữ liệu hiệu chỉnh anomaly score.
- Feature importance.
- Model version.

Model được load một lần khi FastAPI khởi động.

## 9. Cài đặt môi trường

Mở PowerShell tại thư mục `ml-service`:

```powershell
cd C:\Users\PC\fraud-detection\ml-service
```

Tạo virtual environment:

```powershell
py -m venv .venv
```

Kích hoạt:

```powershell
.\.venv\Scripts\Activate.ps1
```

Cài dependency:

```powershell
python -m pip install -r requirements.txt
```

## 10. Huấn luyện lại mô hình

Dataset cần đặt tại:

`../data/creditcard.csv`

Chạy theo thứ tự:

```powershell
python explore_data.py
python analyze_time_split.py
python prepare_data.py
python train_isolation_forest.py
python train_random_forest.py
python package_models.py
```

Sau khi hoàn tất, model được đóng gói tại:

`models/fraud_detection_v1.joblib`

## 11. Chạy ML Service

Cấu hình API Key trong PowerShell:

```powershell
$key = py -c "import secrets; print(secrets.token_urlsafe(32))"
$env:ML_API_KEY = $key
```

Khởi động FastAPI:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

API chạy tại:

`http://127.0.0.1:8000`

Swagger UI:

`http://127.0.0.1:8000/docs`

Lưu ý: Swagger cần gửi header X-API-Key khi gọi endpoint được bảo vệ.

## 12. API Endpoints

### GET /health

Kiểm tra trạng thái ML Service.

Header:

`X-API-Key: <API_KEY>`

Response:

```json
{
  "status": "UP",
  "model_version": "v1"
}
```

### POST /score

Chấm điểm một hoặc nhiều giao dịch.

Header:

`X-API-Key: <API_KEY>`

Request:

```json
{
  "transactions": [
    {
      "time": 150000.0,
      "amount": 100.0,
      "v1": 0.1,
      "v2": 0.1,
      "v3": 0.1,
      "v4": 0.1,
      "v5": 0.1,
      "v6": 0.1,
      "v7": 0.1,
      "v8": 0.1,
      "v9": 0.1,
      "v10": 0.1,
      "v11": 0.1,
      "v12": 0.1,
      "v13": 0.1,
      "v14": 0.1,
      "v15": 0.1,
      "v16": 0.1,
      "v17": 0.1,
      "v18": 0.1,
      "v19": 0.1,
      "v20": 0.1,
      "v21": 0.1,
      "v22": 0.1,
      "v23": 0.1,
      "v24": 0.1,
      "v25": 0.1,
      "v26": 0.1,
      "v27": 0.1,
      "v28": 0.1
    }
  ]
}
```

Giới hạn batch: tối đa 1,000 giao dịch mỗi request.

Response có cấu trúc:

```json
{
  "status": "SUCCESS",
  "total": 1,
  "model_version": "v1",
  "results": [
    {
      "anomaly_score": 14.0995,
      "fraud_probability": 0.0,
      "top_features": [],
      "model_version": "v1"
    }
  ]
}
```

Các giá trị trong response trên chỉ minh họa cấu trúc.

### HTTP status

| Status | Ý nghĩa |
|---|---|
| 200 | Thành công |
| 401 | API Key thiếu hoặc không hợp lệ |
| 422 | Dữ liệu đầu vào không hợp lệ |
| 500 | Lỗi trong quá trình scoring |
| 503 | Chưa cấu hình API Key |

## 13. Kiểm thử

Cài thư viện:

```powershell
python -m pip install pytest httpx
```

Chạy toàn bộ test:

```powershell
python -m pytest -v
```

Kết quả kiểm thử thực tế:

- 13 tests passed.
- 0 tests failed.
- Thời gian chạy: 1.82 giây.
- Có 1 StarletteDeprecationWarning liên quan đến httpx và TestClient.

Các test bao gồm:

- Scoring một giao dịch.
- Scoring batch.
- Kiểm tra feature bị thiếu.
- Kiểm tra giá trị số không hợp lệ.
- Kiểm tra API health.
- Kiểm tra API Key.
- Kiểm tra dữ liệu POST /score.
- Kiểm tra giới hạn batch.

## 14. Giới hạn của hệ thống

1. Dataset sử dụng các feature V1–V28 đã được ẩn danh, không cung cấp thông tin gốc về chủ thẻ hoặc đặc điểm giao dịch có thể giải thích trực tiếp.
2. Top features thể hiện mức độ quan trọng toàn cục của mô hình, không phải lời giải thích nguyên nhân riêng cho từng giao dịch.
3. Fraud probability chưa được hiệu chỉnh xác suất.
4. Dataset chỉ có 492 giao dịch gian lận, trong đó Test có 75 giao dịch, nên kết quả đánh giá có thể biến động.
5. Dữ liệu thực tế có thể khác phân bố dữ liệu Kaggle, vì vậy cần đánh giá lại trước khi triển khai vận hành.

## 15. Bảo mật và quản lý Git

Không commit các dữ liệu và file sau:

- Dataset gốc.
- File `.joblib`.
- Virtual environment `.venv`.
- API Key và file `.env`.

API Key được lấy từ biến môi trường `ML_API_KEY`, không hardcode trong source code.

ML Service chỉ bind vào `127.0.0.1` trong cấu hình chạy hiện tại. Khi triển khai trên môi trường khác cần cấu hình mạng, xác thực và bảo mật phù hợp.