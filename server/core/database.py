"""
数据库连接和会话管理模块。

本模块提供 SQLAlchemy 异步引擎和会话工厂，
用于管理数据库连接和事务。
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import get_settings

logger = logging.getLogger(__name__)

# 全局数据库引擎和会话工厂
_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    获取或创建异步数据库引擎。

    引擎在首次调用时创建，并在整个应用生命周期中重用。

    Returns:
        AsyncEngine: SQLAlchemy 异步引擎实例
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,  # 验证连接有效性
            future=True,  # 使用 SQLAlchemy 2.0 风格
        )
        logger.info(f"数据库引擎已创建: {settings.DATABASE_URL}")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    获取或创建异步会话工厂。

    会话工厂用于创建数据库会话实例。

    Returns:
        async_sessionmaker[AsyncSession]: SQLAlchemy 异步会话工厂
    """
    global _async_session_factory
    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # 提交后对象不会过期
            autoflush=True,  # 自动刷新更改
            autocommit=False,  # 禁用自动提交
        )
        logger.info("数据库会话工厂已创建")
    return _async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖项：提供数据库会话。

    此函数用作 FastAPI 路由的依赖项，自动管理会话生命周期。
    会话在请求结束时自动关闭，异常时自动回滚。

    Yields:
        AsyncSession: SQLAlchemy 异步会话实例

    Example:
        >>> from fastapi import Depends
        >>> from sqlalchemy.ext.asyncio import AsyncSession
        >>>
        >>> @app.get("/users")
        >>> async def get_users(db: AsyncSession = Depends(get_db_session)):
        >>>     result = await db.execute(select(User))
        >>>     return result.scalars().all()
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    初始化数据库架构。

    在应用启动时调用，创建所有定义的数据库表。
    此操作是幂等的 - 如果表已存在则不会重复创建。

    Raises:
        Exception: 数据库初始化失败时抛出异常
    """
    from ..models.base import Base  # 延迟导入避免循环依赖

    engine = get_engine()
    logger.info("开始初始化数据库架构...")

    try:
        async with engine.begin() as conn:
            # 创建所有表（幂等操作）
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库架构初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


async def dispose_engine() -> None:
    """
    释放数据库引擎和所有连接。

    在应用关闭时调用，确保所有数据库连接正确关闭。
    """
    global _engine, _async_session_factory

    if _engine is not None:
        logger.info("正在关闭数据库连接...")
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("数据库连接已关闭")
