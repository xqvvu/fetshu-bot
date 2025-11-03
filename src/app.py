"""
FastAPI 应用工厂。

本模块创建并配置 FastAPI 应用实例，包括所有必要的中间件、异常处理器和路由。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import register_routers
from .core import get_settings
from .core.database import dispose_engine, init_db

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    创建并配置 FastAPI 应用。

    此工厂函数：
    - 创建带有元数据的 FastAPI 实例
    - 配置 CORS 中间件
    - 注册异常处理器
    - 注册所有 API 路由

    Returns:
        FastAPI: 配置好的 FastAPI 应用实例

    Example:
        >>> app = create_app()
        >>> # 使用 uvicorn: uvicorn.run(app, host="0.0.0.0", port=8000)
    """
    settings = get_settings()

    # 创建带有元数据的 FastAPI 应用
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        debug=settings.DEBUG,
        # 自定义 OpenAPI 文档
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # 配置 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # 注册全局异常处理器
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        处理所有未捕获的异常。

        在生产模式下，返回通用错误消息。
        在调试模式下，包含完整的异常详情。
        """
        error_detail = str(exc) if settings.DEBUG else "服务器内部错误"

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": error_detail,
                "path": str(request.url),
            },
        )

    # 注册所有 API 路由
    register_routers(app)

    # 注册数据库生命周期事件
    @app.on_event("startup")
    async def startup_event():
        """
        应用启动事件：初始化数据库。

        在应用启动时创建所有数据库表。
        如果数据库初始化失败，应用将无法启动。
        """
        try:
            logger.info("应用启动：初始化数据库...")
            await init_db()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        """
        应用关闭事件：清理数据库连接。

        在应用关闭时释放所有数据库连接。
        """
        logger.info("应用关闭：清理数据库连接...")
        await dispose_engine()
        logger.info("数据库连接已清理")

    return app


# 创建应用实例供 uvicorn 或其他 ASGI 服务器使用
app = create_app()
