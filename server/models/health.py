"""健康检查响应模型。"""

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """
    健康检查响应模型。

    Attributes:
        status: 应用的当前健康状态
        version: 应用版本字符串
        timestamp: 健康检查的 ISO 时间戳
    """

    status: str = Field(
        default="healthy", description="当前健康状态", examples=["healthy"]
    )
    version: str = Field(description="应用版本", examples=["0.1.0"])
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="ISO 格式的健康检查时间戳",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2025-11-02T19:30:00.000000",
            }
        }
