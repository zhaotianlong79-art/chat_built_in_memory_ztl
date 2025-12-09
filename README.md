# 智能体基本框架

## 项目简介
一个基于 FastAPI 构建的高性能智能体（Agent）框架，支持与 OpenAI 模型集成，并使用 MongoDB 进行数据持久化。该框架提供了灵活的智能体开发基础结构，便于快速构建和部署各类 AI 应用。

## 主要特性
- 🚀 **高性能后端**：基于 FastAPI 构建，支持异步处理，提供高效的 API 服务
- 🤖 **多模型支持**：集成 OpenAI GPT 系列模型，支持灵活的对话管理
- 💾 **数据持久化**：使用 MongoDB 进行数据存储，支持结构化和非结构化数据
- 🔧 **模块化设计**：采用插件化架构，易于扩展和维护
- 📊 **可观测性**：内置日志记录和监控功能，便于调试和性能分析

## 技术架构

### 核心组件
- **API 服务层**：FastAPI 驱动的 RESTful API 接口
- **智能体引擎**：负责对话流程管理和任务调度
- **数据访问层**：MongoDB 数据库操作封装
- **模型集成层**：OpenAI API 调用封装

### 依赖技术栈
- **Web框架**：FastAPI
- **数据库**：MongoDB（聊天记录）、Milvus（向量数据库）
- **AI模型**：OpenAI GPT系列
- **嵌入服务**：Jina AI（多模态向量化）
- **异步支持**：asyncio
- **数据验证**：Pydantic

## 快速开始

### 环境要求
- Python 3.8+
- MongoDB 5.0+
- OpenAI API 密钥

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd chat_built_in_memory_ztl
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
   或使用国内镜像加速：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. **配置数据库**
   
   确保 MongoDB 已安装并运行，修改 `src/config/config.py` 中的数据库配置：
   ```python
   MONGO_DB: str = "chat_agent_db"
   MONGO_HOST: str = "localhost"
   MONGO_PORT: int = 27017
   ```

4. **启动应用**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

5. **访问 API 文档**
   
   打开浏览器访问：`http://localhost:8000/docs`

### 使用示例

**发送聊天请求：**
```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "session_001",
    "prompt": "你好，请介绍一下自己"
  }'
```

## 学习资源

- **[完整学习指南](LEARNING_GUIDE.md)** - 适合初学者的详细教程，包含技术栈讲解、代码详解和学习路线
- **[快速参考手册](QUICK_REFERENCE.md)** - 常用命令、API 接口和配置的速查表

## 项目结构

```
chat_built_in_memory_ztl/
├── src/
│   ├── main.py                    # 应用入口
│   ├── handlers.py                # 路由注册
│   ├── api/                       # API 接口层
│   │   ├── api.py                 # 路由汇总
│   │   └── chat.py                # 聊天接口
│   ├── service/                   # 业务逻辑层
│   │   ├── chat_service.py        # 对话管理
│   │   └── embed_service.py       # 向量化服务
│   ├── third_party_service/       # 第三方服务集成
│   │   └── jina.py                # Jina AI 嵌入服务
│   ├── repositories/              # 数据访问层
│   │   └── chat_repository.py     # 聊天数据操作
│   ├── models/                    # 数据模型
│   │   └── mongo.py               # MongoDB 模型定义
│   ├── schemas/                   # 请求/响应模型
│   │   └── chat_schemas.py        # 聊天相关模型
│   ├── config/                    # 配置管理
│   │   ├── config.py              # 配置类
│   │   └── openapi_docs.py        # API 文档配置
│   ├── db_conn/                   # 数据库连接
│   │   ├── mongo.py               # MongoDB 连接
│   │   └── milvus.py              # Milvus 连接
│   ├── middleware/                # 中间件
│   │   └── log.py                 # 日志配置
│   └── utils/                     # 工具函数
├── static/                        # 静态文件
├── requirements.txt               # 依赖列表
├── LEARNING_GUIDE.md              # 完整学习指南
├── QUICK_REFERENCE.md             # 快速参考手册
├── README.md                      # 项目说明
└── test_db.py                     # 数据库测试脚本
```

## API 接口

### 健康检查
- **GET** `/health` - 检查服务状态

### 聊天接口
- **POST** `/chat/stream` - 流式聊天对话

详细的 API 文档请访问：`http://localhost:8000/docs`

## 常见问题

### 1. 依赖安装失败
确保使用 Python 3.8 或更高版本，并尝试使用国内镜像源。

### 2. MongoDB 连接失败
检查 MongoDB 服务是否启动，端口是否正确。

### 3. OpenAI API 调用失败
验证 API Key 和 Base URL 配置是否正确（在 `src/service/chat_service.py` 中）。

更多问题请查看 [快速参考手册](QUICK_REFERENCE.md#故障排查)。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---

  ![img_1.png](img_1.png)