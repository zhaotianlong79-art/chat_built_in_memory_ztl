# 快速参考手册

> 常用命令、代码片段和配置的速查表

---

## 📋 目录

- [启动命令](#启动命令)
- [API 接口](#api-接口)
- [数据库操作](#数据库操作)
- [常用代码片段](#常用代码片段)
- [配置参考](#配置参考)
- [故障排查](#故障排查)

---

## 启动命令

### 开发环境启动

```bash
# 1. 进入项目目录
cd d:\pythonWorkspace\chat_built_in_memory_ztl

# 2. 激活虚拟环境（如果使用）
venv\Scripts\activate

# 3. 启动项目
uvicorn src.main:app --reload --port 8000

# 4. 启动（指定 host）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境启动

```bash
# 使用多进程
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# 使用 Gunicorn + Uvicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 依赖安装

```bash
# 安装依赖
pip install -r requirements.txt

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 升级 pip
python -m pip install --upgrade pip

# 导出依赖
pip freeze > requirements.txt
```

---

## API 接口

### 健康检查

```bash
# GET /health
curl http://localhost:8000/health

# 返回
{"status":"ok"}
```

### 聊天接口

```bash
# POST /chat/stream
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "session_001",
    "prompt": "你好"
  }'
```

### API 文档

```
# Swagger UI（推荐）
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc

# OpenAPI JSON
http://localhost:8000/openapi.json
```

---

## 数据库操作

### MongoDB 命令

```bash
# 连接数据库
mongo

# 或指定主机和端口
mongo --host localhost --port 27017

# 切换到项目数据库
use chat_agent_db

# 查看所有集合
show collections

# 查看聊天记录
db.chat_history.find().pretty()

# 查询特定用户的记录
db.chat_history.find({"user_id": "user_001"}).pretty()

# 查询特定会话
db.chat_history.find({"session_id": "session_001"}).pretty()

# 删除特定会话
db.chat_history.deleteOne({"session_id": "session_001"})

# 清空集合
db.chat_history.deleteMany({})

# 统计记录数
db.chat_history.countDocuments()

# 查看最新 5 条记录
db.chat_history.find().sort({_id: -1}).limit(5).pretty()
```

### MongoEngine 操作（Python）

```python
# 查询所有记录
sessions = ChatHistory.objects.all()

# 根据条件查询
session = ChatHistory.objects(session_id="s1", user_id="u1").first()

# 创建记录
session = ChatHistory(
    session_id="new_session",
    user_id="user123",
    messages=[]
)
session.save()

# 更新记录
session.messages.append({"role": "user", "content": "你好"})
session.save()

# 删除记录
session.delete()

# 批量查询
sessions = ChatHistory.objects(user_id="user123")
for s in sessions:
    print(s.session_id)
```

---

## 常用代码片段

### 1. 添加新的 API 接口

**在 `src/api/chat.py` 中添加：**

```python
@router.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """获取用户的所有会话"""
    from src.models.mongo import ChatHistory
    
    sessions = ChatHistory.objects(user_id=user_id)
    return {
        "count": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "message_count": len(s.messages),
                "create_time": s.create_time.isoformat()
            }
            for s in sessions
        ]
    }
```

### 2. 添加请求参数验证

```python
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=50)
    session_id: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1, max_length=2000)
    
    @validator('prompt')
    def prompt_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('提示词不能为空')
        return v
```

### 3. 添加错误处理

```python
from fastapi import HTTPException

@router.post("/stream")
async def chat_stream(chat_request: ChatSessionRequest):
    try:
        # 业务逻辑
        return EventSourceResponse(...)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
```

### 4. 添加日志记录

```python
from loguru import logger

# 记录信息
logger.info(f"用户 {user_id} 发起聊天请求")

# 记录警告
logger.warning(f"会话 {session_id} 未找到")

# 记录错误
logger.error(f"数据库连接失败: {str(e)}")

# 记录调试信息
logger.debug(f"消息内容: {message}")
```

### 5. 异步数据库操作

```python
import asyncio

async def batch_create_sessions(user_id: str, count: int):
    """批量创建会话"""
    tasks = []
    for i in range(count):
        task = create_chat_session(
            user_id=user_id,
            session_id=f"session_{i}"
        )
        tasks.append(task)
    
    # 并发执行
    results = await asyncio.gather(*tasks)
    return results
```

### 6. 添加依赖注入

```python
from fastapi import Depends

async def get_current_user(token: str = Header(...)):
    """依赖注入：验证用户"""
    # 验证 token
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="未授权")
    return user

@router.post("/stream")
async def chat_stream(
    chat_request: ChatSessionRequest,
    user = Depends(get_current_user)  # 自动注入
):
    # user 已经验证通过
    return EventSourceResponse(...)
```

### 7. 使用 Milvus 向量检索

```python
from src.db_conn.milvus import milvus_client
from src.service.embed_service import embed_text

# 1. 插入向量数据
async def insert_document(text: str, metadata: dict):
    """将文档向量化并存储到 Milvus"""
    # 获取文本向量
    embedding = await embed_text("text", text)
    
    # 准备数据
    data = {
        "embedding": embedding,
        "file_name": metadata.get("file_name"),
        "file_page": metadata.get("page", 0),
        **metadata  # 动态字段
    }
    
    # 插入到 Milvus
    ids = milvus_client.insert(data)
    return ids[0]

# 2. 搜索相似文档
async def search_similar(query: str, top_k: int = 5):
    """根据查询文本检索相似文档"""
    # 向量化查询
    query_vector = await embed_text("text", query)
    
    # 搜索参数
    search_params = {
        "metric_type": "IP",  # 内积相似度
        "params": {"ef": 128}
    }
    
    # 执行搜索
    results = milvus_client.search(
        query_vectors=[query_vector],
        search_params=search_params,
        limit=top_k,
        output_fields=["file_name", "file_page"]
    )
    
    return results[0]  # 返回第一个查询的结果
```

### 8. 多模态嵌入（文本和图片）

```python
from src.service.embed_service import embed_text, embed_image

# 文本嵌入
async def process_text():
    vector = await embed_text("text", "A beautiful sunset")
    print(f"向量维度: {len(vector)}")

# 图片嵌入（URL）
async def process_image():
    vector = await embed_image(
        "image_url",
        "https://example.com/image.jpg"
    )
    print(f"图片向量维度: {len(vector)}")

# 跨模态检索：用文本搜图片
async def search_images_by_text(text: str):
    """用文本描述搜索相似图片"""
    text_vector = await embed_text("text", text)
    
    results = milvus_client.search(
        query_vectors=[text_vector],
        search_params={"metric_type": "IP"},
        limit=10,
        filter="image_url != ''",  # 只搜索有图片的记录
        output_fields=["image_url", "image_width"]
    )
    return results[0]
```

### 9. RAG 检索增强生成

```python
from src.third_party_service.jina import get_embeddings_async
from src.db_conn.milvus import milvus_client
from openai import OpenAI

async def rag_chat(user_question: str):
    """RAG 流程：检索 + 生成"""
    
    # 1. 向量化用户问题
    question_vector = await embed_text("text", user_question)
    
    # 2. 从 Milvus 检索相关文档
    search_results = milvus_client.search(
        query_vectors=[question_vector],
        search_params={"metric_type": "IP"},
        limit=3,
        output_fields=["text_content", "file_name"]
    )
    
    # 3. 构建上下文
    context = "\n\n".join([
        f"文档：{r['entity']['file_name']}\n{r['entity']['text_content']}"
        for r in search_results[0]
    ])
    
    # 4. 构建提示词
    prompt = f"""参考以下文档回答问题：

{context}

问题：{user_question}

请基于上述文档回答，如果文档中没有相关信息，请说明。"""
    
    # 5. 调用 OpenAI 生成答案
    client = OpenAI(api_key="...", base_url="...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个helpful助手"},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content
```

---

## 配置参考

### .env 文件模板

```env
# 应用配置
DEBUG=True

# MongoDB 配置（聊天记录存储）
MONGO_DB=chat_agent_db
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=
MONGO_PASSWORD=
MONGO_AUTH_SOURCE=admin
MONGO_CONN_NAME=default

# Milvus 配置（向量数据库）
MILVUS_DB_HOST=localhost
MILVUS_DB_PORT=19530
MILVUS_DB_NAME=default
MILVUS_DB_USER=
MILVUS_DB_PASS=
MILVUS_DB_TIMEOUT=30
MILVUS_DB_COLLECTION_NAME=document_vectors

# Jina AI 嵌入服务配置
EMBED_SERVER_URL=https://api.jina.ai/v1/embeddings
EMBED_SERVER_TOKEN=your_jina_api_key_here

# OpenAI 配置（可选，也可以在代码中配置）
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 日志配置
LOG_LEVEL=INFO
LOG_ROTATION=100 MB
LOG_RETENTION=7 days
```

### config.py 配置项说明

#### MongoDB 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DEBUG` | bool | True | 调试模式 |
| `MONGO_DB` | str | chat_agent_db | 数据库名 |
| `MONGO_HOST` | str | localhost | MongoDB 地址 |
| `MONGO_PORT` | int | 27017 | MongoDB 端口 |
| `MONGO_USER` | str | "" | 数据库用户名 |
| `MONGO_PASSWORD` | str | "" | 数据库密码 |
| `MONGO_AUTH_SOURCE` | str | admin | 认证数据库 |
| `MONGO_CONN_NAME` | str | default | 连接别名 |

#### Milvus 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `MILVUS_DB_HOST` | str | localhost | Milvus 地址 |
| `MILVUS_DB_PORT` | int | 19530 | Milvus 端口 |
| `MILVUS_DB_NAME` | str | default | 数据库名 |
| `MILVUS_DB_USER` | str | "" | 用户名（可选） |
| `MILVUS_DB_PASS` | str | "" | 密码（可选） |
| `MILVUS_DB_TIMEOUT` | int | 30 | 连接超时（秒） |
| `MILVUS_DB_COLLECTION_NAME` | str | - | 集合名称 |

#### 嵌入服务配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `EMBED_SERVER_URL` | str | jina api | Jina AI 嵌入服务地址 |
| `EMBED_SERVER_TOKEN` | str | - | Jina AI API Token |

#### 搜索配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `SEARCH_CONFIG` | dict | {"metric_type": "IP"} | 向量检索配置 |

#### 日志配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `log_rotation` | str | 100 MB | 日志轮转大小 |
| `log_retention` | str | 7 days | 日志保留时间 |

---

## 故障排查

### 1. ModuleNotFoundError: No module named 'xxx'

**原因：** 依赖包未安装

**解决：**
```bash
pip install -r requirements.txt
```

---

### 2. MongoDB 连接失败

**错误信息：**
```
ServerSelectionTimeoutError: localhost:27017: [WinError 10061]
```

**解决：**
```bash
# 检查 MongoDB 是否启动
# Windows: 打开服务管理器，查看 MongoDB Server 服务

# 手动启动 MongoDB
mongod --dbpath "C:\data\db"

# 检查端口
netstat -ano | findstr 27017
```

---

### 3. 端口被占用

**错误信息：**
```
Address already in use
```

**解决：**
```bash
# 查找占用端口的进程
netstat -ano | findstr 8000

# 杀死进程（Windows）
taskkill /PID <进程ID> /F

# 或更换端口
uvicorn src.main:app --reload --port 8001
```

---

### 4. OpenAI API 调用失败

**错误信息：**
```
AuthenticationError / RateLimitError
```

**解决：**
1. 检查 API Key 是否正确
2. 确认账户有余额
3. 检查网络连接
4. 查看 `chat_service.py` 中的 `base_url` 是否正确

---

### 5. 流式响应不显示

**原因：** 客户端未正确处理 SSE

**解决：**
```javascript
// 前端使用 EventSource
const source = new EventSource('http://localhost:8000/chat/stream');

source.addEventListener('add', (e) => {
  const data = JSON.parse(e.data);
  console.log(data.data.content);
});

source.addEventListener('finish', (e) => {
  source.close();
});
```

---

### 6. CORS 跨域问题

**错误信息：**
```
Access-Control-Allow-Origin
```

**解决：**

在 `main.py` 中确保已添加 CORS 中间件：
```python
if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境改为具体域名
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

---

## 性能优化建议

### 1. 数据库索引

```python
# 在 models/mongo.py 中
class ChatHistory(BaseDocument):
    meta = {
        'collection': 'chat_history',
        'indexes': [
            'session_id',           # 单字段索引
            'user_id',
            ('user_id', 'session_id')  # 复合索引
        ]
    }
```

### 2. 连接池配置

```python
# db_conn/mongo.py
connect(
    db=settings.MONGO_DB,
    host=settings.MONGO_HOST,
    port=settings.MONGO_PORT,
    minPoolSize=10,    # 最小连接数
    maxPoolSize=100,   # 最大连接数
    maxIdleTimeMS=30000  # 空闲超时
)
```

### 3. 日志级别调整

```python
# 生产环境建议
LOG_LEVEL=WARNING  # 只记录警告和错误
```

---

## 测试命令

### 单元测试（示例）

```python
# tests/test_chat.py
import pytest
from src.repositories.chat_repository import create_chat_session

@pytest.mark.asyncio
async def test_create_session():
    session = await create_chat_session("u1", "s1")
    assert session.user_id == "u1"
    assert session.session_id == "s1"
```

运行测试：
```bash
# 安装 pytest
pip install pytest pytest-asyncio

# 运行测试
pytest tests/

# 查看覆盖率
pytest --cov=src tests/
```

---

## Git 常用命令

```bash
# 查看状态
git status

# 添加文件
git add .

# 提交
git commit -m "feat: 添加新功能"

# 推送
git push origin main

# 拉取
git pull origin main

# 查看日志
git log --oneline

# 创建分支
git checkout -b feature/new-feature

# 合并分支
git merge feature/new-feature
```

---

## Docker 部署（可选）

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGO_HOST=mongodb
    depends_on:
      - mongodb
  
  mongodb:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### 启动命令

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

---

## 监控和日志

### 查看实时日志

```bash
# Linux/Mac
tail -f logs/stdout.log

# Windows PowerShell
Get-Content logs\stdout.log -Wait
```

### 日志格式

```
2024-12-09 13:00:00.123456 | INFO | pid=12345 | trace_id=abc123 | main.py:48 | Starting up
```

---

## 常用的环境变量

```bash
# Windows CMD
set DEBUG=True

# Windows PowerShell
$env:DEBUG="True"

# Linux/Mac
export DEBUG=True

# Python 中读取
import os
debug = os.getenv("DEBUG", "False") == "True"
```

---

## 有用的链接

- **FastAPI 文档**: https://fastapi.tiangolo.com/zh/
- **MongoDB 文档**: https://www.mongodb.com/docs/
- **OpenAI API**: https://platform.openai.com/docs/
- **Pydantic 文档**: https://docs.pydantic.dev/
- **Python 异步编程**: https://docs.python.org/zh-cn/3/library/asyncio.html

---

**最后更新：** 2025-12-09  
**版本：** v1.0
