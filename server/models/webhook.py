"""飞书 Webhook 事件模型。"""

from typing import Any

from pydantic import BaseModel, Field


class WebhookChallenge(BaseModel):
    """
    飞书 Webhook URL 验证挑战模型。

    注册 Webhook URL 时，飞书会发送一个挑战值，
    必须将其回传以验证所有权。

    Attributes:
        challenge: 需要回传的挑战字符串
        token: 可选的验证令牌
        type: 事件类型，通常为 "url_verification"
    """

    challenge: str = Field(description="要返回的挑战字符串")
    token: str | None = Field(default=None, description="验证令牌")
    type: str = Field(default="url_verification", description="验证的事件类型")


class FeishuWebhookEvent(BaseModel):
    """
    通用飞书 Webhook 事件模型。

    这表示飞书 Webhook 事件的通用结构。
    特定事件类型可能有额外的字段。

    Attributes:
        schema: 事件 schema 版本
        header: 包含元数据的事件头
        event: 事件负载数据
    """

    schema_: str | None = Field(
        default=None, alias="schema", description="事件 schema 版本"
    )
    header: dict[str, Any] = Field(
        default_factory=dict, description="带有元数据的事件头"
    )
    event: dict[str, Any] = Field(default_factory=dict, description="事件负载数据")

    class Config:
        populate_by_name = True


class WebhookResponse(BaseModel):
    """
    标准 Webhook 响应模型。

    Attributes:
        success: Webhook 是否处理成功
        message: 描述结果的可选消息
        challenge: URL 验证的可选挑战响应
    """

    success: bool = Field(default=True, description="处理成功状态")
    message: str | None = Field(default=None, description="响应消息")
    challenge: str | None = Field(default=None, description="URL 验证的挑战响应")
