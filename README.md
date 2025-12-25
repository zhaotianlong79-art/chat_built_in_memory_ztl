这是一个根据你的要求重新生成的 README 文档，包含了详细的架构说明、数据流图以及使用示例。

---

# RAG 智能知识库问答系统

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

本项目是一个基于 **RAG（检索增强生成）** 架构的企业级智能问答系统。系统集成了文档解析、向量化存储、语义检索及大模型对话能力，旨在帮助企业或个人快速构建基于私有数据的 AI 助手。

## 📌 主要特性

- **📚 多模态文档处理**：支持 PDF、TXT、Markdown 等多种格式文档的上传、解析与切片。
- **🔍 高精度语义检索**：利用 Jina AI Embeddings 与 Milvus 向量数据库，实现毫秒级的语义相似度搜索。
- **💬 上下文感知对话**：基于 OpenAI GPT 模型，结合检索到的知识库片段，提供精准、可溯源的回答。
- **🧠 持久化会话管理**：自动保存多轮对话历史，支持断点续聊，确保上下文连贯。
- **🏗️ 分层架构设计**：采用 API、Service、Repository 三层架构，代码解耦，易于维护与扩展。

## 🛠️ 技术栈

| 类别 | 技术选型 |
| :--- | :--- |
| **开发语言** | Python 3.8+ |
| **Web 框架** | FastAPI (高性能异步框架) |
| **文档数据库** | MongoDB (存储元数据、对话历史) |
| **向量数据库** | Milvus (存储向量数据、支持 ANN 搜索) |
| **LLM 模型** | OpenAI API (GPT-3.5/4.0) |
| **Embedding 模型** | Jina AI (高维向量嵌入) |
| **ORM/ODM** | Motor (MongoDB 异步驱动), PyMilvus |

## 📂 项目结构

```text
.
├── api/                        # [API 层] 接口定义
│   ├── api.py                  # 路由聚合入口
│   ├── chat.py                 # 聊天与对话接口
│   ├── doc2kb.py               # 文档上传与处理接口
│   └── knowledge_base.py       # 知识库管理接口
├── service/                    # [Service 层] 业务逻辑
│   ├── chat_service.py         # 对话编排、Prompt 构建
│   ├── doc2kb_service.py       # 文档解析、分块逻辑
│   ├── embed_service.py        # 封装 Jina AI 向量化调用
│   └── save_kb_service.py      # 知识库入库逻辑
├── repository/                 # [Repository 层] 数据访问
│   ├── chat_repository.py      # 聊天记录 CRUD 操作
│   └── knowledge_repository.py # 知识库与向量数据 CRUD
├── models/                     # [Models] 数据模型定义
│   ├── chat_history.py         # 聊天记录模型
│   ├── knowledge_base.py       # 知识库元数据模型
│   └── files.py                # 文件信息模型
├── main.py                     # 应用启动入口
├── requirements.txt            # 项目依赖
└── README.md                   # 项目文档
```

## 🚀 快速开始

### 1. 环境准备

确保本地环境已安装：
- Python 3.8+
- MongoDB
- Milvus (Docker 部署推荐)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件并配置以下关键信息：

```ini
# OpenAI 配置
OPENAI_API_KEY=sk-your-openai-key

# Jina AI 配置
JINA_API_KEY=your-jina-api-key

# 数据库配置
MONGO_URI=mongodb://localhost:27017/
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### 4. 启动服务

```bash
python main.py
```

访问 `http://localhost:8000/docs` 查看 API 文档。

## 💡 使用示例

### 1. 创建知识库并上传文档

通过上传文档，系统会自动解析、切片并向量化存入 Milvus。

```bash
curl -X POST "http://localhost:8000/api/knowledge_base/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "kb_name=company_policy" \
  -F "files=@policy.pdf"
```

### 2. 发起智能问答

基于已上传的知识库内容进行提问。

```bash
curl -X POST "http://localhost:8000/api/chat/completion" \
  -H "Content-Type: application/json" \
  -d '{
    "kb_id": "company_policy",
    "query": "公司的年假制度是怎样的？",
    "session_id": "user_123_session"
  }'
```

**响应示例：**
```json
{
  "answer": "根据公司政策，正式员工每年享有 15 天带薪年假...",
  "reference_docs": ["policy.pdf: page 12"]
}
```

## 🧠 核心功能说明

1. **文档向量化流程 (ETL)**
   - 用户上传文件 -> 解析文本 -> 智能切片 -> 调用 Jina AI 生成向量 -> 存入 Milvus (向量) + MongoDB (元数据)。

2. **智能问答流程 (RAG)**
   - 用户提问 -> 生成 Query 向量 -> Milvus 检索 TopK 相似片段 -> 构建 Prompt (包含检索内容) -> 调用 OpenAI 生成回答 -> 保存对话历史。

3. **会话管理**
   - 利用 MongoDB 存储完整的对话上下文，在生成新回答时自动拉取历史消息，确保多轮对话的逻辑连贯性。

## 📊 数据流图

以下是系统处理“用户提问”这一核心场景的详细数据流向：

```mermaid
flowchart TD
    %% 用户操作
    User((用户提问))

    %% API 层
    subgraph API_Layer [API 接口层]
        ChatRouter[chat.py: 接收提问请求]
    end

    %% Service 层
    subgraph Service_Layer [业务逻辑层]
        ChatService[chat_service.py: 对话编排]
        EmbedService[embed_service.py: 问题向量化]
    end

    %% Repository 层
    subgraph Repository_Layer [数据访问层]
        ChatRepo[chat_repository.py: 获取历史]
        KnowledgeRepo[knowledge_repository.py: 向量检索]
    end

    %% Database 层
    subgraph Database_Layer [数据存储层]
        MongoDB[(MongoDB: 历史记录)]
        MilvusDB[(Milvus: 向量数据)]
    end

    %% 外部服务
    subgraph External_Services [外部服务]
        JinaService[Jina AI: 文本转向量]
        OpenAIService[OpenAI API: 生成回答]
    end

    %% 流程连接
    User -->|提问| ChatRouter
    ChatRouter --> ChatService

    %% 1. 获取历史
    ChatService -->|请求上下文| ChatRepo
    ChatRepo -->|返回历史| MongoDB
    MongoDB --> ChatRepo
    ChatRepo --> ChatService

    %% 2. 问题向量化
    ChatService -->|发送问题文本| EmbedService
    EmbedService -->|请求嵌入| JinaService
    JinaService -->|返回向量| EmbedService
    EmbedService -->|返回向量| ChatService

    %% 3. 知识检索
    ChatService -->|向量搜索| KnowledgeRepo
    KnowledgeRepo -->|相似度搜索| MilvusDB
    MilvusDB -->|返回文档片段| KnowledgeRepo
    KnowledgeRepo --> ChatService

    %% 4. 生成回答
    ChatService -->|组装 Prompt (问题+历史+知识片段)| OpenAIService
    OpenAIService -->|最终回答| ChatService
    ChatService -->|响应| ChatRouter
    ChatRouter --> User
```

**流程解析：**
1. **接收请求**：`chat.py` 接收用户提问。
2. **加载上下文**：`chat_service.py` 调用 `chat_repository.py` 从 MongoDB 获取该 Session 的历史对话。
3. **向量化问题**：`chat_service.py` 调用 `embed_service.py`，通过 Jina AI 将用户问题转为向量。
4. **检索知识**：`chat_service.py` 将向量传给 `knowledge_repository.py`，在 Milvus 中检索最相关的知识片段。
5. **生成回答**：`chat_service.py` 将“问题+历史+知识片段”组合成 Prompt，发送给 OpenAI API 生成最终回答。
6. **返回结果**：API 将生成的答案返回给用户。