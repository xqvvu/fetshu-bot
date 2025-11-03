"""
健康检查端点。

为监控系统提供应用健康状况和状态信息。
"""

from datetime import datetime

from fastapi import APIRouter

from ..core import get_settings
from ..models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    健康检查端点。

    返回应用当前的健康状态、版本信息和时间戳。
    此端点始终可访问，不需要身份验证。

    Returns:
        HealthResponse: 当前健康状态、版本和时间戳

    Example:
        ```
        GET /health
        Response:
        {
            "status": "healthy",
            "version": "0.1.0",
            "timestamp": "2025-11-02T19:30:00.000000"
        }
        ```
    """
    settings = get_settings()

    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(),
    )
