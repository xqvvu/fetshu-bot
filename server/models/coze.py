"""
Coze AI API 数据模型。

本模块定义了与 Coze AI 对话流 API 交互所需的数据模型。
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class CozeMessage(BaseModel):
    """Coze 对话消息模型。"""
    
    content: str = Field(..., description="消息内容")
    content_type: Literal["text", "image", "file"] = Field(default="text", description="内容类型")
    role: Literal["user", "assistant"] = Field(..., description="消息角色")
    type: Literal["question", "answer", "function_call", "tool_output", "follow_up"] = Field(..., description="消息类型")


class CozeWorkflowChatRequest(BaseModel):
    """Coze 对话流请求模型。"""
    
    workflow_id: str = Field(..., description="工作流 ID")
    app_id: str = Field(..., description="应用 ID")
    conversation_id: Optional[str] = Field(default=None, description="对话 ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工作流参数")
    additional_messages: List[CozeMessage] = Field(default_factory=list, description="附加消息")


class CozeWorkflowEvent(BaseModel):
    """Coze 工作流事件模型。"""
    
    event: str = Field(..., description="事件类型")
    data: Optional[Dict[str, Any]] = Field(default=None, description="事件数据")


class CozeWorkflowResponse(BaseModel):
    """Coze 工作流响应模型。"""
    
    events: List[CozeWorkflowEvent] = Field(default_factory=list, description="事件列表")
    debug_url: Optional[str] = Field(default=None, description="调试链接")
    conversation_id: Optional[str] = Field(default=None, description="对话 ID")


class CozeErrorResponse(BaseModel):
    """Coze API 错误响应模型。"""
    
    code: int = Field(..., description="错误代码")
    msg: str = Field(..., description="错误消息")
    detail: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")


class CozeAIResponse(BaseModel):
    """Coze AI 处理结果模型。"""
    
    success: bool = Field(..., description="处理是否成功")
    content: Optional[str] = Field(default=None, description="AI 回复内容")
    debug_url: Optional[str] = Field(default=None, description="调试链接")
    conversation_id: Optional[str] = Field(default=None, description="对话 ID")
    error_message: Optional[str] = Field(default=None, description="错误消息")