-- 1. Người dùng
CREATE TABLE app_user (
    id             NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username       VARCHAR2(50)  NOT NULL,
    password_hash  VARCHAR2(100) NOT NULL,            -- BCrypt
    role           VARCHAR2(20)  NOT NULL,
    enabled        NUMBER(1)     DEFAULT 1 NOT NULL,
    created_at     TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT uq_app_user_username UNIQUE (username),
    CONSTRAINT ck_app_user_role CHECK (role IN ('NHAN_VIEN', 'QUAN_LY')),
    CONSTRAINT ck_app_user_enabled CHECK (enabled IN (0, 1))
);

-- 2. Phiên bản mô hình (để biết cảnh báo cũ do mô hình nào sinh ra)
CREATE TABLE model_version (
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version     VARCHAR2(50)  NOT NULL,
    trained_at  TIMESTAMP,
    notes       VARCHAR2(500),
    CONSTRAINT uq_model_version UNIQUE (version)
);

-- 3. Lần tải file CSV
CREATE TABLE upload_file (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_name       VARCHAR2(255) NOT NULL,
    uploaded_by     NUMBER        NOT NULL,
    status          VARCHAR2(20)  DEFAULT 'DANG_XU_LY' NOT NULL,
    total_rows      NUMBER        DEFAULT 0 NOT NULL,
    valid_rows      NUMBER        DEFAULT 0 NOT NULL,
    invalid_rows    NUMBER        DEFAULT 0 NOT NULL,
    created_at      TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
    finished_at     TIMESTAMP,
    CONSTRAINT fk_upload_user FOREIGN KEY (uploaded_by) REFERENCES app_user (id),
    CONSTRAINT ck_upload_status CHECK (status IN ('DANG_XU_LY', 'HOAN_TAT', 'LOI'))
);

-- 4. Lô xử lý nền (khoảng 1000 dòng/lô)
CREATE TABLE upload_chunk (
    id             NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    upload_id      NUMBER        NOT NULL,
    chunk_no       NUMBER        NOT NULL,
    row_from       NUMBER        NOT NULL,
    row_to         NUMBER        NOT NULL,
    status         VARCHAR2(20)  DEFAULT 'CHO_XU_LY' NOT NULL,
    error_message  VARCHAR2(500),
    CONSTRAINT fk_chunk_upload FOREIGN KEY (upload_id) REFERENCES upload_file (id),
    CONSTRAINT uq_chunk UNIQUE (upload_id, chunk_no),
    CONSTRAINT ck_chunk_status CHECK (status IN ('CHO_XU_LY', 'DANG_XU_LY', 'XONG', 'LOI'))
);

-- 5. Lỗi từng dòng khi kiểm tra dữ liệu
CREATE TABLE upload_error (
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    upload_id   NUMBER         NOT NULL,
    row_number  NUMBER         NOT NULL,
    field_name  VARCHAR2(50),
    message     VARCHAR2(300)  NOT NULL,
    CONSTRAINT fk_error_upload FOREIGN KEY (upload_id) REFERENCES upload_file (id)
);

-- 6. Giao dịch (định dạng Kaggle: Time, V1..V28, Amount, Class)
--    upload_id = NULL nghĩa là giao dịch đến từ đường realtime.
--    Không lưu số thẻ (Kaggle không có).
CREATE TABLE txn (
    id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    upload_id    NUMBER,
    source       VARCHAR2(10)  NOT NULL,
    time_sec     NUMBER        NOT NULL,              -- giây tương đối, không phải ngày thật
    amount       NUMBER(14,2)  NOT NULL,
    v1  BINARY_DOUBLE, v2  BINARY_DOUBLE, v3  BINARY_DOUBLE, v4  BINARY_DOUBLE,
    v5  BINARY_DOUBLE, v6  BINARY_DOUBLE, v7  BINARY_DOUBLE, v8  BINARY_DOUBLE,
    v9  BINARY_DOUBLE, v10 BINARY_DOUBLE, v11 BINARY_DOUBLE, v12 BINARY_DOUBLE,
    v13 BINARY_DOUBLE, v14 BINARY_DOUBLE, v15 BINARY_DOUBLE, v16 BINARY_DOUBLE,
    v17 BINARY_DOUBLE, v18 BINARY_DOUBLE, v19 BINARY_DOUBLE, v20 BINARY_DOUBLE,
    v21 BINARY_DOUBLE, v22 BINARY_DOUBLE, v23 BINARY_DOUBLE, v24 BINARY_DOUBLE,
    v25 BINARY_DOUBLE, v26 BINARY_DOUBLE, v27 BINARY_DOUBLE, v28 BINARY_DOUBLE,
    class_label  NUMBER(1),                           -- nhãn thật của Kaggle, chỉ để đánh giá
    status       VARCHAR2(10)  DEFAULT 'CHO_CHAM' NOT NULL,
    created_at   TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_txn_upload FOREIGN KEY (upload_id) REFERENCES upload_file (id),
    CONSTRAINT ck_txn_source CHECK (source IN ('CSV', 'REALTIME')),
    CONSTRAINT ck_txn_status CHECK (status IN ('CHO_CHAM', 'DA_CHAM', 'LOI_CHAM')),
    CONSTRAINT ck_txn_class CHECK (class_label IS NULL OR class_label IN (0, 1)),
    CONSTRAINT ck_txn_amount CHECK (amount >= 0),
    CONSTRAINT ck_txn_time CHECK (time_sec >= 0)
);

-- 7. Kết quả chấm điểm (mỗi giao dịch, mỗi phiên bản mô hình một dòng)
--    risk_level được lưu lại như "ảnh chụp" vì ngưỡng có thể chỉnh sau này.
CREATE TABLE txn_score (
    id                 NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    txn_id             NUMBER        NOT NULL,
    model_version_id   NUMBER        NOT NULL,
    anomaly_score      NUMBER(6,2)   NOT NULL,        -- 0..100 (Isolation Forest)
    fraud_probability  NUMBER(6,2)   NOT NULL,        -- 0..100 (mô hình có giám sát)
    rule_score         NUMBER(6,2)   NOT NULL,        -- 0..100 (luật Java)
    final_score        NUMBER(6,2)   NOT NULL,        -- 0..100 (gộp có trọng số)
    risk_level         VARCHAR2(10)  NOT NULL,
    top_features       CLOB,                          -- JSON: đặc trưng bất thường nhất
    scored_at          TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_score_txn FOREIGN KEY (txn_id) REFERENCES txn (id),
    CONSTRAINT fk_score_model FOREIGN KEY (model_version_id) REFERENCES model_version (id),
    CONSTRAINT uq_score UNIQUE (txn_id, model_version_id),
    CONSTRAINT ck_score_level CHECK (risk_level IN ('THAP', 'TRUNG_BINH', 'CAO')),
    CONSTRAINT ck_score_range CHECK (
        anomaly_score      BETWEEN 0 AND 100 AND
        fraud_probability  BETWEEN 0 AND 100 AND
        rule_score         BETWEEN 0 AND 100 AND
        final_score        BETWEEN 0 AND 100),
    CONSTRAINT ck_score_json CHECK (top_features IS JSON)
);

-- 8. Luật nào đã kích hoạt (mỗi luật một dòng, đúng 1NF)
CREATE TABLE score_rule_hit (
    id         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    score_id   NUMBER        NOT NULL,
    rule_code  VARCHAR2(50)  NOT NULL,
    points     NUMBER(6,2)   NOT NULL,
    detail     VARCHAR2(300),
    CONSTRAINT fk_hit_score FOREIGN KEY (score_id) REFERENCES txn_score (id)
);

-- 9. Cảnh báo (sinh cho mức CAO)
CREATE TABLE alert (
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    score_id    NUMBER        NOT NULL,
    status      VARCHAR2(15)  DEFAULT 'MOI' NOT NULL,
    created_at  TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_alert_score FOREIGN KEY (score_id) REFERENCES txn_score (id),
    CONSTRAINT uq_alert_score UNIQUE (score_id),
    CONSTRAINT ck_alert_status CHECK (status IN ('MOI', 'DANG_XEM', 'DA_DONG'))
);

-- 10. Kết quả rà soát (giữ lịch sử, một cảnh báo có thể được đánh giá lại)
CREATE TABLE alert_review (
    id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alert_id     NUMBER        NOT NULL,
    reviewer_id  NUMBER        NOT NULL,
    verdict      VARCHAR2(15)  NOT NULL,
    note         VARCHAR2(1000),
    reviewed_at  TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_review_alert FOREIGN KEY (alert_id) REFERENCES alert (id),
    CONSTRAINT fk_review_user FOREIGN KEY (reviewer_id) REFERENCES app_user (id),
    CONSTRAINT ck_review_verdict CHECK (verdict IN ('GIAN_LAN', 'BINH_THUONG', 'CAN_XEM_THEM'))
);
