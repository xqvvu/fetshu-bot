"""
飞书机器人应用的核心配置模块。

本模块使用 Pydantic 的 BaseSettings 管理所有应用设置，
从环境变量加载配置，并提供合理的默认值。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    从环境变量加载的应用设置。

    所有设置都可以通过设置相应的环境变量来覆盖
    (例如：APP_NAME, DEBUG, HOST, PORT)。
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # 应用元数据
    APP_NAME: str = "Feishu Bot"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "集成 Coze AI 的飞书机器人"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS 配置
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Coze AI 配置
    COZE_API_BASE_URL: str = "https://api.coze.cn"
    COZE_ACCESS_TOKEN: str = ""  # 从环境变量获取
    COZE_WORKFLOW_ID: str = ""  # 从环境变量获取
    COZE_APP_ID: str = ""  # 从环境变量获取
    COZE_TIMEOUT: int = 30  # API 请求超时时间（秒）

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./feishu-bot.sqlite"
    DATABASE_ECHO: bool = False  # 设置为 True 以启用 SQL 查询日志
    DATABASE_POOL_SIZE: int = 5
    DATABASE_POOL_TIMEOUT: int = 30


@lru_cache
def get_settings() -> Settings:
    """
    获取缓存的应用设置实例。

    此函数被缓存以确保设置只加载一次，
    并在整个应用生命周期中重用同一实例。

    Returns:
        Settings: 应用设置实例
    """
    return Settings()
