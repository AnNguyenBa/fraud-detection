
"""
FastAPI service cho hệ thống Fraud Detection.

Chức năng:
- GET /health: kiểm tra trạng thái ML Service.
- POST /score: chấm điểm một hoặc nhiều giao dịch.
- Xác thực bằng X-API-Key.
- Không kết nối database.
"""

import logging
import math
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Depends, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from scoring import load_model, score_transactions


# =========================================================
# 1. LOGGING
# =========================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraud-detection")


# =========================================================
# 2. SCHEMA REQUEST
# =========================================================

class Transaction(BaseModel):
    """
    Dữ liệu một giao dịch.

    Time chỉ dùng làm thông tin đầu vào,
    không được đưa vào 29 features của model.
    """

    model_config = ConfigDict(extra="forbid")

    time: float = Field(ge=0)
    amount: float = Field(ge=0)

    v1: float
    v2: float
    v3: float
    v4: float
    v5: float
    v6: float
    v7: float
    v8: float
    v9: float
    v10: float
    v11: float
    v12: float
    v13: float
    v14: float
    v15: float
    v16: float
    v17: float
    v18: float
    v19: float
    v20: float
    v21: float
    v22: float
    v23: float
    v24: float
    v25: float
    v26: float
    v27: float
    v28: float

    @field_validator("*", mode="before")
    @classmethod
    def validate_numeric_type(cls, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Giá trị phải là số.")

        return value

    @field_validator("*")
    @classmethod
    def validate_finite(cls, value):
        if not math.isfinite(value):
            raise ValueError("Giá trị phải là số hữu hạn.")

        return value


class ScoreRequest(BaseModel):
    """Request chấm điểm nhiều giao dịch."""

    transactions: list[Transaction] = Field(
        min_length=1,
        max_length=1000,
    )


# =========================================================
# 3. SCHEMA RESPONSE
# =========================================================

class FeatureImportance(BaseModel):
    feature: str
    importance: float


class ScoreResult(BaseModel):
    anomaly_score: float
    fraud_probability: float
    top_features: list[FeatureImportance]
    model_version: str


class ScoreResponse(BaseModel):
    status: str
    total: int
    model_version: str
    results: list[ScoreResult]


# =========================================================
# 4. LOAD MODEL KHI KHỞI ĐỘNG SERVICE
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Đang load Fraud Detection model...")

    # Load model một lần khi service khởi động.
    app.state.model_package = load_model()

    logger.info(
        "Load model thành công: %s",
        app.state.model_package["model_version"],
    )

    yield

    logger.info("Fraud Detection service stopped.")


app = FastAPI(
    title="Fraud Detection ML Service",
    description="API chấm điểm bất thường và gian lận giao dịch.",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# 5. API KEY AUTHENTICATION
# =========================================================

def verify_api_key(
        request: Request,
        api_key: str | None = Header(
            default=None,
            alias="X-API-Key",
        ),
):
    """
    Kiểm tra API Key từ HTTP Header.

    API Key được lấy từ biến môi trường ML_API_KEY.
    Không lưu API Key trong source code.
    """

    expected_api_key = os.getenv("ML_API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=503,
            detail="ML Service chưa được cấu hình API Key.",
        )

    if not api_key or not secrets.compare_digest(
            api_key,
            expected_api_key,
    ):
        raise HTTPException(
            status_code=401,
            detail="API Key không hợp lệ hoặc bị thiếu.",
        )


# =========================================================
# 6. HEALTH CHECK
# =========================================================

@app.get("/health", dependencies=[Depends(verify_api_key)])
def health_check(request: Request):
    """
    Kiểm tra trạng thái ML Service.
    """

    package = request.app.state.model_package

    return {
        "status": "UP",
        "model_version": package["model_version"],
    }


# =========================================================
# 7. SCORING API
# =========================================================

@app.post(
    "/score",
    response_model=ScoreResponse,
    dependencies=[Depends(verify_api_key)],
)
def score(request: Request, body: ScoreRequest):
    """
    Chấm điểm tối đa 1000 giao dịch trong một request.
    """

    package = request.app.state.model_package

    try:
        # Chuyển Pydantic objects thành list dictionary.
        transactions = [
            transaction.model_dump()
            for transaction in body.transactions
        ]

        # Gọi scoring.py để chấm điểm.
        results = score_transactions(
            transactions,
            package,
        )

        return {
            "status": "SUCCESS",
            "total": len(results),
            "model_version": package["model_version"],
            "results": results,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except Exception:
        logger.exception("Lỗi khi chấm điểm giao dịch.")

        raise HTTPException(
            status_code=500,
            detail="ML Service gặp lỗi khi chấm điểm.",
        )
