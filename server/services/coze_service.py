"""
Coze AI 服务模块。

本模块提供与 Coze AI 对话流 API 的集成功能，支持流式响应处理。
"""

import json
import logging
from typing import AsyncGenerator, Dict, List, Optional

import httpx
from httpx import AsyncClient

from ..core import get_settings
from ..models import (
    CozeAIResponse,
    CozeErrorResponse,
    CozeMessage,
    CozeWorkflowChatRequest,
    CozeWorkflowEvent,
)

logger = logging.getLogger(__name__)


class CozeService:
    """Coze AI 服务类。"""

    def __init__(self):
        """初始化 Coze 服务。"""
        self.settings = get_settings()
        self.base_url = self.settings.COZE_API_BASE_URL
        self.access_token = self.settings.COZE_ACCESS_TOKEN
        self.workflow_id = self.settings.COZE_WORKFLOW_ID
        self.app_id = self.settings.COZE_APP_ID
        self.timeout = self.settings.COZE_TIMEOUT

    def _get_headers(self) -> Dict[str, str]:
        """获取 API 请求头。"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def _handle_error_response(self, response: httpx.Response) -> CozeAIResponse:
        """处理错误响应。"""
        try:
            error_data = response.json()
            error = CozeErrorResponse(**error_data)
            logger.error(f"Coze API 错误: {error.code} - {error.msg}")
            return CozeAIResponse(
                success=False,
                error_message=f"API 错误 {error.code}: {error.msg}"
            )
        except Exception as e:
            logger.error(f"解析错误响应失败: {e}")
            return CozeAIResponse(
                success=False,
                error_message=f"HTTP {response.status_code}: {response.text}"
            )

    async def _parse_stream_response(self, response: httpx.Response) -> CozeAIResponse:
        """解析流式响应。"""
        events: List[CozeWorkflowEvent] = []
        content_parts: List[str] = []
        debug_url: Optional[str] = None
        conversation_id: Optional[str] = None

        try:
            # 获取响应内容
            response_text = await response.aread()
            response_str = response_text.decode('utf-8')
            
            logger.debug(f"原始响应内容: {response_str}")
            
            # 处理 Server-Sent Events 格式
            lines = response_str.split('\n')
            current_event = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 处理 SSE 事件类型
                if line.startswith("event: "):
                    current_event = line[7:]  # 移除 "event: " 前缀
                    continue
                
                # 处理 SSE 数据
                if line.startswith("data: "):
                    data_str = line[6:]  # 移除 "data: " 前缀
                    
                    if data_str.strip() == "[DONE]":
                        break
                    
                    try:
                        event_data = json.loads(data_str)
                        
                        # 检查是否是错误事件
                        if current_event == "error" or ("code" in event_data and "msg" in event_data):
                            error = CozeErrorResponse(**event_data)
                            logger.error(f"Coze API 错误: {error.code} - {error.msg}")
                            return CozeAIResponse(
                                success=False,
                                error_message=f"API 错误 {error.code}: {error.msg}"
                            )
                        
                        # 处理正常事件
                        event = CozeWorkflowEvent(
                            event=current_event or "unknown",
                            data=event_data
                        )
                        events.append(event)
                        
                        # 提取内容和元数据
                        if current_event == "conversation.message.completed":
                            if "content" in event_data:
                                content = event_data["content"]
                                # 如果内容是 JSON 字符串，尝试解析
                                if isinstance(content, str) and content.startswith("{"):
                                    try:
                                        content_json = json.loads(content)
                                        if "output" in content_json:
                                            content_parts.append(content_json["output"])
                                        else:
                                            content_parts.append(content)
                                    except json.JSONDecodeError:
                                        content_parts.append(content)
                                else:
                                    content_parts.append(str(content))
                        elif current_event == "done":
                            if "debug_url" in event_data:
                                debug_url = event_data["debug_url"]
                            if "conversation_id" in event_data:
                                conversation_id = event_data["conversation_id"]
                                    
                    except json.JSONDecodeError as e:
                        logger.warning(f"解析事件数据失败: {e}, 数据: {data_str}")
                        continue
                    except Exception as e:
                        logger.warning(f"处理事件失败: {e}, 数据: {data_str}")
                        continue
                
                # 处理直接的 JSON 错误响应（不在 SSE 格式中）
                elif line.startswith("{") and line.endswith("}"):
                    try:
                        error_data = json.loads(line)
                        if "code" in error_data and "msg" in error_data:
                            error = CozeErrorResponse(**error_data)
                            logger.error(f"Coze API 错误: {error.code} - {error.msg}")
                            return CozeAIResponse(
                                success=False,
                                error_message=f"API 错误 {error.code}: {error.msg}"
                            )
                    except json.JSONDecodeError:
                        continue

            # 合并所有内容
            full_content = "".join(content_parts) if content_parts else None
            
            # 如果没有内容但也没有错误，可能是配置问题
            if not full_content and not events:
                return CozeAIResponse(
                    success=False,
                    error_message="未收到有效的 AI 响应，请检查 Coze 配置"
                )
            
            return CozeAIResponse(
                success=True,
                content=full_content,
                debug_url=debug_url,
                conversation_id=conversation_id
            )

        except Exception as e:
            logger.error(f"解析流式响应失败: {e}")
            return CozeAIResponse(
                success=False,
                error_message=f"解析响应失败: {str(e)}"
            )

    async def _create_conversation(self) -> Optional[str]:
        """
        创建新的对话。

        Returns:
            Optional[str]: 对话 ID，如果创建失败则返回 None
        """
        url = f"{self.base_url}/v1/conversation/create"
        headers = self._get_headers()

        try:
            async with AsyncClient(timeout=self.timeout) as client:
                logger.info(f"创建 Coze 对话: {url}")
                
                response = await client.post(
                    url,
                    headers=headers,
                    json={}
                )

                if response.status_code == 200:
                    data = response.json()
                    conversation_id = data.get("data", {}).get("id")
                    logger.info(f"成功创建对话: {conversation_id}")
                    return conversation_id
                else:
                    logger.error(f"创建对话失败: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"创建对话异常: {e}")
            return None

    async def chat_with_workflow(
        self,
        user_input: str,
        conversation_name: str = "Answer",
        additional_messages: Optional[List[CozeMessage]] = None
    ) -> CozeAIResponse:
        """
        与 Coze 对话流进行对话。

        Args:
            user_input: 用户输入内容
            conversation_name: 对话名称，默认为 "Answer"
            additional_messages: 附加消息列表

        Returns:
            CozeAIResponse: AI 响应结果
        """
        if not self.access_token:
            return CozeAIResponse(
                success=False,
                error_message="Coze access token 未配置"
            )

        if not self.workflow_id or not self.app_id:
            return CozeAIResponse(
                success=False,
                error_message="Coze workflow_id 或 app_id 未配置"
            )

        # 先创建对话
        conversation_id = await self._create_conversation()
        if not conversation_id:
            return CozeAIResponse(
                success=False,
                error_message="无法创建对话"
            )

        # 构建请求数据
        request_data = CozeWorkflowChatRequest(
            workflow_id=self.workflow_id,
            app_id=self.app_id,
            conversation_id=conversation_id,
            parameters={
                "CONVERSATION_NAME": conversation_name,
                "USER_INPUT": user_input
            },
            additional_messages=additional_messages or [
                CozeMessage(
                    content=user_input,
                    content_type="text",
                    role="user",
                    type="question"
                )
            ]
        )

        url = f"{self.base_url}/v1/workflows/chat"
        headers = self._get_headers()

        try:
            async with AsyncClient(timeout=self.timeout) as client:
                logger.info(f"发送 Coze API 请求: {url}")
                logger.debug(f"请求数据: {request_data.model_dump()}")
                
                response = await client.post(
                    url,
                    headers=headers,
                    json=request_data.model_dump(),
                )

                if response.status_code != 200:
                    return await self._handle_error_response(response)

                return await self._parse_stream_response(response)

        except httpx.TimeoutException:
            logger.error("Coze API 请求超时")
            return CozeAIResponse(
                success=False,
                error_message="API 请求超时"
            )
        except Exception as e:
            logger.error(f"Coze API 请求失败: {e}")
            return CozeAIResponse(
                success=False,
                error_message=f"API 请求失败: {str(e)}"
            )

    async def chat_stream(
        self,
        user_input: str,
        conversation_name: str = "Answer",
        additional_messages: Optional[List[CozeMessage]] = None
    ) -> AsyncGenerator[CozeWorkflowEvent, None]:
        """
        流式对话接口。

        Args:
            user_input: 用户输入内容
            conversation_name: 对话名称
            additional_messages: 附加消息列表

        Yields:
            CozeWorkflowEvent: 流式事件
        """
        if not self.access_token or not self.workflow_id or not self.app_id:
            logger.error("Coze 配置不完整")
            return

        request_data = CozeWorkflowChatRequest(
            workflow_id=self.workflow_id,
            app_id=self.app_id,
            parameters={
                "CONVERSATION_NAME": conversation_name,
                "USER_INPUT": user_input
            },
            additional_messages=additional_messages or [
                CozeMessage(
                    content=user_input,
                    content_type="text",
                    role="user",
                    type="question"
                )
            ]
        )

        url = f"{self.base_url}/v1/workflows/chat"
        headers = self._get_headers()

        try:
            async with AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=request_data.model_dump(),
                ) as response:
                    if response.status_code != 200:
                        logger.error(f"API 请求失败: {response.status_code}")
                        return

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        if line.startswith("data: "):
                            data_str = line[6:]
                            
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                event_data = json.loads(data_str)
                                event = CozeWorkflowEvent(**event_data)
                                yield event
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"流式请求失败: {e}")


# 全局服务实例
coze_service = CozeService()