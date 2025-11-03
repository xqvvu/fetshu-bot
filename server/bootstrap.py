"""
应用启动和入口点。

本模块提供运行 FastAPI 应用的主入口点。
处理命令行参数并启动 uvicorn 服务器。
"""

import argparse
import sys

import uvicorn

from .core import get_settings


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数。

    Returns:
        argparse.Namespace: 已解析的命令行参数
    """
    parser = argparse.ArgumentParser(description="飞书机器人 - 集成 Coze 的 AI 机器人")

    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="要绑定的主机地址 (默认: 从设置中读取)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="要绑定的端口 (默认: 从设置中读取)",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用自动重载 (开发模式)",
    )

    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="禁用自动重载 (生产模式)",
    )

    return parser.parse_args()


def main() -> None:
    """
    应用的主入口点。

    加载设置、解析命令行参数并启动 uvicorn 服务器。
    """
    settings = get_settings()
    args = parse_args()

    # 确定配置
    host = args.host or settings.HOST
    port = args.port or settings.PORT

    # 确定重载模式
    if args.no_reload:
        reload = False
    elif args.reload:
        reload = True
    else:
        # 默认：在调试模式下重载
        reload = settings.DEBUG

    print(f"正在启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"服务器: http://{host}:{port}")
    print(f"调试模式: {settings.DEBUG}")
    print(f"自动重载: {reload}")

    if settings.DEBUG:
        print(f"API 文档: http://{host}:{port}/docs")
        print(f"ReDoc: http://{host}:{port}/redoc")

    # 启动 uvicorn 服务器
    try:
        uvicorn.run(
            "server.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="debug" if settings.DEBUG else "info",
        )
    except KeyboardInterrupt:
        print("\n正在优雅地关闭...")
        sys.exit(0)


if __name__ == "__main__":
    main()
