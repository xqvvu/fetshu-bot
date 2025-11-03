"""
SQLAlchemy 基础模型和通用 Mixin。

本模块提供所有数据库模型的基类和常用字段的 Mixin。
"""

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    所有 ORM 模型的声明式基类。

    继承此类以创建数据库模型。

    Example:
        >>> class User(Base):
        >>>     __tablename__ = "users"
        >>>     id: Mapped[int] = mapped_column(primary_key=True)
        >>>     name: Mapped[str]
    """

    pass


class TimestampMixin:
    """
    时间戳 Mixin，提供创建和更新时间字段。

    包含字段：
    - created_at: 记录创建时间（自动设置）
    - updated_at: 记录最后更新时间（自动更新）

    Example:
        >>> class User(Base, TimestampMixin):
        >>>     __tablename__ = "users"
        >>>     id: Mapped[int] = mapped_column(primary_key=True)
        >>>     name: Mapped[str]
    """

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        server_onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


class PrimaryKeyMixin:
    """
    主键 Mixin，提供自增整数主键字段。

    包含字段：
    - id: 自增整数主键

    Example:
        >>> class User(Base, PrimaryKeyMixin):
        >>>     __tablename__ = "users"
        >>>     name: Mapped[str]
    """

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="主键ID",
    )
