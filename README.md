# 飞书机器人 (Feishu Bot)

一个基于 FastAPI 的飞书机器人系统，集成 Coze AI 服务，用于处理飞书 Webhook 消息并提供智能回复。

## 项目简介

本项目是一个功能完善的飞书 Webhook 处理服务（Python 3.14+ 和 FastAPI 框架），集成了 Coze AI 服务，可以处理飞书 Webhook 请求并提供智能响应。

## 主要特性

- **FastAPI 框架**：高性能的现代 Web 框架
- **Webhook 处理**：支持飞书 Webhook 接收
  - URL 验证机制
  - 消息事件处理
  - 完善的错误处理
- **配置管理**：基于环境变量的灵活配置
- **数据模型**：使用 Pydantic 进行严格的数据模型验证
- **代码质量**：集成 Ruff 进行 Linting 和格式化
- **CORS 支持**：可配置的跨域资源共享
- **文档生成**：自动生成 API 文档（Swagger UI & ReDoc）

## 技术栈

- **Python**: 3.14+
- **Web 框架**: FastAPI 0.120.4+
- **包管理**: uv (快速的 Python 包管理器)
- **AI 服务**: Coze (cozepy 0.20.0+)
- **代码质量**: Ruff (格式化和 Linting)
- **命令运行**: Just (命令行任务运行器)

## 项目结构

```
feishu-bot/
├── src/
│   ├── api/              # API 路由层
│   │   ├── __init__.py   # 路由模块
│   │   ├── health.py     # 健康检查端点
│   │   └── webhook.py    # 飞书 Webhook 端点
│   ├── core/             # 核心配置
│   │   ├── __init__.py
│   │   └── config.py     # 配置管理
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   ├── health.py     # 健康检查模型
│   │   └── webhook.py    # Webhook 数据模型
│   ├── services/         # 业务逻辑层
│   │   ├── __init__.py
│   │   └── webhook_handler.py  # Webhook 处理器
│   ├── app.py            # FastAPI 应用实例
│   └── bootstrap.py      # 应用启动脚本
├── openspec/             # OpenSpec 变更管理
│   ├── AGENTS.md         # AI 助手指南
│   ├── changes/          # 变更提案
│   ├── project.md        # 项目规范
│   └── specs/            # 规范文档
├── Justfile              # 命令定义
├── pyproject.toml        # 项目配置
├── uv.lock               # 依赖锁定文件
├── AGENTS.md             # 通用 AI 助手指南
├── CLAUDE.md             # Claude AI 项目说明
└── README.md             # 项目说明文档
```

## 快速开始

### 环境要求

- Python 3.14 或更高版本
- [uv](https://github.com/astral-sh/uv) - Python 包管理器
- [Just](https://github.com/casey/just) - 命令行任务运行器（可选）

### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 安装 Just

```bash
# macOS
brew install just

# Linux
cargo install just

# 或者从 GitHub 下载预编译二进制
# https://github.com/casey/just/releases
```

### 安装依赖

```bash
# 使用 Just（推荐）
just install

# 或者直接使用 uv
uv sync
```

### 配置环境变量

创建 `.env` 文件（参考以下配置示例）：

```bash
# 应用配置
APP_NAME=Feishu Bot
APP_VERSION=0.1.0
APP_DESCRIPTION=基于 Coze AI 的飞书机器人

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS 配置
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
```

### 运行应用

```bash
# 开发模式（启用热重载）
just dev

# 或者
uv run python -m src.bootstrap --reload

# 生产模式
just run

# 或者
uv run python -m src.bootstrap --no-reload
```

应用启动后可访问：
- **应用主页**: http://localhost:8000
- **健康检查**: http://localhost:8000/health
- **API 文档 (Swagger UI)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc

## 开发指南

### 可用命令

项目使用 Just 作为命令行任务运行器，查看所有可用命令：

```bash
just
```

#### 运行命令

```bash
just dev          # 启动开发服务器（热重载）
just run          # 启动生产服务器
just start        # 启动服务器（从配置文件读取）
```

#### 代码质量命令

```bash
just fmt          # 格式化代码
just fmt-check    # 检查代码格式（不修改）
just lint         # 运行代码检查
just lint-fix     # 自动修复问题
just check        # 运行所有检查（格式 + Lint）
just fix          # 格式化并自动修复所有问题
```

#### 测试命令

```bash
just test         # 运行测试套件（待实现）
just test-cov     # 运行测试并生成覆盖率报告（待实现）
```

#### 依赖管理

```bash
just install      # 安装依赖
just install-dev  # 安装开发依赖
just update       # 更新依赖
just outdated     # 检查过期依赖
```

#### 清理命令

```bash
just clean        # 清理缓存文件
```

### API 端点

#### 健康检查

```bash
GET /health
```

返回服务健康状态：

```json
{
  "status": "healthy",
  "app_name": "Feishu Bot",
  "version": "0.1.0"
}
```

#### 飞书 Webhook

```bash
POST /webhook/feishu
```

处理飞书 Webhook 请求。

**URL 验证请求：**
```json
{
  "challenge": "ajls384kdjx98XX",
  "token": "xxxxxx",
  "type": "url_verification"
}
```

**响应：**
```json
{
  "challenge": "ajls384kdjx98XX"
}
```

**消息事件请求：**
```json
{
  "schema": "2.0",
  "header": {
    "event_id": "5e3702a84e847582be8db7fb73283c02",
    "event_type": "im.message.receive_v1",
    "create_time": "1608725989000",
    "token": "rvaYgkND1GOiu5MM0E1rncYC6PLtF7JV",
    "app_id": "cli_9f3ca975326d5011",
    "tenant_key": "2ca4d3c5536e3135"
  },
  "event": {
    "sender": {...},
    "message": {...}
  }
}
```

**响应：**
```json
{
  "success": true,
  "message": "消息事件处理成功"
}
```

### 配置飞书 Webhook

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 创建或选择应用
3. 在"事件订阅"中配置 Webhook URL：
   ```
   https://your-domain.com/webhook/feishu
   ```
4. 订阅需要监听的消息事件类型
5. 保存配置并完成验证流程

## 代码风格

项目使用 Ruff 进行代码格式化和检查：

- **行长度**: 88 字符
- **缩进**: 空格
- **缩进大小**: 4 个空格
- **换行符**: LF (Unix 风格)
- **启用规则集**:
  - Pyflakes (F)
  - Pycodestyle (E, W)
  - isort (I001)

## 架构设计

### 分层架构

```
┌─────────────────────────────────────┐
│     API Layer (api/)                │  路由和请求处理层
├─────────────────────────────────────┤
│   Service Layer (services/)         │  业务逻辑层
├─────────────────────────────────────┤
│   Model Layer (models/)             │  数据模型和验证层
├─────────────────────────────────────┤
│       Core (core/)                  │  配置和核心工具
└─────────────────────────────────────┘
```

### 关键组件

- **app.py**: FastAPI 应用实例配置，包含路由注册
- **bootstrap.py**: 应用启动脚本，负责命令行参数解析
- **config.py**: 使用 Pydantic 管理配置项
- **webhook.py**: 飞书 Webhook 端点实现
- **webhook_handler.py**: Webhook 处理业务逻辑

## 错误处理

项目实现了统一的错误处理：

### 标准错误码

- **400 Bad Request**: 请求数据 JSON 格式错误
- **500 Internal Server Error**: 服务器内部错误

### 错误响应格式

所有异常都会被全局异常处理器捕获，并返回统一的错误响应格式：

```json
{
  "success": false,
  "error": "错误描述",
  "path": "/api/path"
}
```

详细的错误信息会记录在应用日志中，便于调试。

## 日志系统

项目使用 Python 标准库 logging 模块：

- 开发模式：DEBUG 级别
- 生产模式：INFO 级别
- 结构化日志输出，便于日志分析和监控

## 待开发功能

- [ ] Coze AI 服务集成
- [ ] 消息处理业务逻辑
- [ ] 单元测试
- [ ] 集成测试
- [ ] 数据库支持
- [ ] 异步任务
- [ ] 消息队列
- [ ] 性能监控和追踪
- [ ] Docker 容器化部署
- [ ] CI/CD 流水线

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某个新特性'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交消息规范

使用约定式提交 (Conventional Commits)：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档变更
- `style:` 代码格式调整（不影响功能逻辑）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

如有问题或建议，请联系：

- 提交 Issue
- 创建 Pull Request

## 相关链接

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Coze](https://www.coze.com/) - AI 服务平台
- [uv](https://github.com/astral-sh/uv) - 快速的 Python 包管理器
- [Ruff](https://github.com/astral-sh/ruff) - 快速的 Python Linter
- [Just](https://github.com/casey/just) - 方便的命令行任务运行器

---

**注意**: 本项目目前处于活跃开发阶段，欢迎贡献和反馈！
