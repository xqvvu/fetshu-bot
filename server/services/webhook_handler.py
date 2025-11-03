"""
Webhook 事件处理服务。

本模块包含处理飞书 Webhook 事件的业务逻辑，集成 Coze AI 服务。
"""

import json
import logging
from typing import Any, Dict, Optional

from .coze_service import coze_service

logger = logging.getLogger(__name__)


def extract_message_content(event: Dict[str, Any]) -> Optional[str]:
    """
    从飞书事件中提取消息内容。

    Args:
        event: 飞书 Webhook 事件数据

    Returns:
        str: 提取的消息内容，如果无法提取则返回 None
    """
    try:
        # 获取事件数据
        event_data = event.get("event", {})
        message = event_data.get("message", {})

        # 提取消息内容
        content = message.get("content", "")
        if isinstance(content, str):
            try:
                # 尝试解析 JSON 格式的内容
                content_data = json.loads(content)
                return content_data.get("text", "")
            except json.JSONDecodeError:
                # 如果不是 JSON 格式，直接返回内容
                return content

        return None
    except Exception as e:
        logger.warning(f"提取消息内容失败: {e}")
        return None


def extract_user_info(event: Dict[str, Any]) -> Dict[str, str]:
    """
    从飞书事件中提取用户信息。

    Args:
        event: 飞书 Webhook 事件数据

    Returns:
        Dict[str, str]: 用户信息字典
    """
    try:
        event_data = event.get("event", {})
        sender = event_data.get("sender", {})

        return {
            "user_id": sender.get("sender_id", {}).get("user_id", ""),
            "open_id": sender.get("sender_id", {}).get("open_id", ""),
            "union_id": sender.get("sender_id", {}).get("union_id", ""),
        }
    except Exception as e:
        logger.warning(f"提取用户信息失败: {e}")
        return {}


async def handle_feishu_event(event: dict[str, Any]) -> dict[str, Any]:
    """
    处理飞书 Webhook 事件。

    这个函数现在集成了 Coze AI 服务，能够：
    - 解析飞书消息事件
    - 提取用户输入内容
    - 调用 Coze AI 获取智能回复
    - 返回处理结果

    Args:
        event: 已解析的飞书 Webhook 事件数据

    Returns:
        dict: 包含处理结果和 AI 响应的字典

    Example:
        >>> result = await handle_feishu_event({"header": {...}, "event": {...}})
        >>> assert result["success"] is True
        >>> assert "ai_response" in result
    """
    # 提取事件元数据
    header = event.get("header", {})
    event_type = header.get("event_type", "unknown")
    event_id = header.get("event_id", "unknown")

    logger.info(f"正在处理飞书事件: type={event_type}, id={event_id}")

    # 处理消息接收事件
    if event_type == "im.message.receive_v1":
        # 提取消息内容
        message_content = extract_message_content(event)
        if not message_content:
            logger.warning("无法提取消息内容")
            return {
                "success": False,
                "event_type": event_type,
                "event_id": event_id,
                "error": "无法提取消息内容",
            }

        # 提取用户信息
        user_info = extract_user_info(event)
        logger.info(f"收到用户消息: {message_content[:100]}...")

        try:
            # 调用 Coze AI 服务
            ai_response = await coze_service.chat_with_workflow(
                user_input=message_content,
                conversation_name="飞书机器人对话"
            )

            if ai_response.success:
                logger.info("Coze AI 响应成功")
                return {
                    "success": True,
                    "event_type": event_type,
                    "event_id": event_id,
                    "message": "消息已处理，AI 响应已生成",
                    "ai_response": {
                        "content": ai_response.content,
                        "conversation_id": ai_response.conversation_id,
                    },
                }
            else:
                logger.error(f"Coze AI 响应失败: {ai_response.error_message}")
                return {
                    "success": False,
                    "event_type": event_type,
                    "event_id": event_id,
                    "error": f"AI 处理失败: {ai_response.error_message}",
                }

        except Exception as e:
            logger.error(f"处理 AI 响应时发生错误: {e}")
            return {
                "success": False,
                "event_type": event_type,
                "event_id": event_id,
                "error": f"AI 处理异常: {str(e)}",
            }

    # 处理其他类型的事件
    else:
        logger.info(f"收到非消息事件: {event_type}")
        return {
            "success": True,
            "event_type": event_type,
            "event_id": event_id,
            "message": f"事件类型 {event_type} 已接收，暂不处理",
        }
