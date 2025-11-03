"""
飞书 Webhook 端点。

处理来自飞书的 Webhook 事件，包括 URL 验证挑战和消息事件。
"""

import logging
from json import JSONDecodeError

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..models import FeishuWebhookEvent, WebhookChallenge, WebhookResponse
from ..services import handle_feishu_event

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/feishu", response_model=WebhookResponse)
async def feishu_webhook(request: Request) -> JSONResponse:
    """
    飞书 Webhook 端点。

    此端点接收并处理来自飞书的 Webhook 事件。
    它处理两种类型的请求：

    1. URL 验证：注册 Webhook 时，飞书会发送一个挑战值需要回传。
    2. 事件通知：实际的 Webhook 事件（消息、交互等）。

    端点会自动检测请求类型并相应地响应。

    Args:
        request: 包含 Webhook 负载的 FastAPI 请求对象

    Returns:
        JSONResponse: 对于验证请求，返回挑战值。对于事件请求，返回处理状态。

    Example:
        URL 验证：
        ```
        POST / webhook / feishu
        {"challenge": "ajls384kdjx98XX", "token": "xxxxxx", "type": "url_verification"}
        Response: {"challenge": "ajls384kdjx98XX"}
        ```

        事件通知：
        ```
        POST /webhook/feishu
        {
            "schema": "2.0",
            "header": {
                "event_id": "...",
                "event_type": "im.message.receive_v1",
                ...
            },
            "event": {...}
        }
        Response: {"success": true, "message": "..."}
        ```

        错误响应（客户端错误）：
        ```
        POST /webhook/feishu
        (empty body or invalid JSON)
        Response: HTTP 400
        {
            "success": false,
            "message": "请求体不能为空",
            "error": "invalid_request_body"
        }
        ```

        错误响应（服务器错误）：
        ```
        Response: HTTP 500
        {
            "success": false,
            "message": "处理 Webhook 时出错: ...",
            "error": "internal_server_error"
        }
        ```
    """
    # 解析原始 JSON 请求体，捕获验证错误
    try:
        body = await request.json()
    except JSONDecodeError as e:
        logger.warning(
            "JSON 解析失败",
            extra={
                "path": str(request.url),
                "method": request.method,
                "error": str(e),
            },
        )
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "无效的 JSON 格式",
                "error": "invalid_json",
            },
        )
    except ValueError as e:
        # 处理空请求体或其他值错误
        logger.warning(
            "请求体验证失败",
            extra={
                "path": str(request.url),
                "method": request.method,
                "error": str(e),
            },
        )
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "请求体不能为空",
                "error": "invalid_request_body",
            },
        )
    except Exception as e:
        # 捕获其他解析相关的异常
        logger.error(
            "请求解析时发生意外错误",
            extra={
                "path": str(request.url),
                "method": request.method,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "无法解析请求体",
                "error": "request_parsing_error",
            },
        )

    # 检查这是否是 URL 验证挑战
    if "challenge" in body and body.get("type") == "url_verification":
        # 解析为挑战并返回挑战值
        challenge = WebhookChallenge(**body)
        return JSONResponse(content={"challenge": challenge.challenge})

    # 解析为常规 Webhook 事件
    try:
        event = FeishuWebhookEvent(**body)

        # 通过服务层处理事件
        result = await handle_feishu_event(event.model_dump())

        return JSONResponse(
            content=WebhookResponse(
                success=result.get("success", True),
                message=result.get("message", "事件处理成功"),
            ).model_dump()
        )
    except Exception as e:
        # 记录服务器错误
        logger.error(
            "处理 Webhook 时出错",
            extra={
                "path": str(request.url),
                "method": request.method,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"处理 Webhook 时出错: {str(e)}",
                "error": "internal_server_error",
            },
        )
