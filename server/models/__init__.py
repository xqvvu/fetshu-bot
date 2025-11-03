"""
用于请求/响应验证和序列化的 Pydantic 模型，以及数据库 ORM 模型。

注意：
- Pydantic 模型用于 API 请求/响应验证
- SQLAlchemy 模型用于数据库持久化
"""

from .coze import (
    CozeAIResponse,
    CozeErrorResponse,
    CozeMessage,
    CozeWorkflowChatRequest,
    CozeWorkflowEvent,
    CozeWorkflowResponse,
)
from .base import Base, PrimaryKeyMixin, TimestampMixin
from .health import HealthResponse
from .webhook import FeishuWebhookEvent, WebhookChallenge, WebhookResponse

__all__ = [
    # Pydantic 模型
    "HealthResponse",
    "FeishuWebhookEvent",
    "WebhookChallenge",
    "WebhookResponse",

    # Coze 模型
    "CozeAIResponse",
    "CozeErrorResponse",
    "CozeMessage",
    "CozeWorkflowChatRequest",
    "CozeWorkflowEvent",
    "CozeWorkflowResponse",

    # SQLAlchemy 模型基类和 Mixin
    "Base",
    "PrimaryKeyMixin",
    "TimestampMixin",
]
