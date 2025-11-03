"""
API 路由和端点聚合。

本模块收集所有 API 路由，并提供函数将它们注册到主 FastAPI 应用中。
"""

from fastapi import FastAPI

from .health import router as health_router
from .webhook import router as webhook_router


def register_routers(app: FastAPI) -> None:
    """
    将所有 API 路由注册到 FastAPI 应用。

    路由按功能区域组织：
    - 健康检查端点（无前缀，供监控工具使用）
    - Webhook 端点（在 /webhook 前缀下）
    - 未来的 API 端点（在 /api/v1 前缀下）

    Args:
        app: FastAPI 应用实例
    """
    # 健康检查在根级别（无前缀，供监控工具使用）
    app.include_router(health_router, tags=["Health"])

    # Webhook 端点
    app.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])

    # 未来版本化 API 路由的占位符
    # api_v1_router = APIRouter(prefix="/api/v1")
    # app.include_router(api_v1_router, tags=["API v1"])
