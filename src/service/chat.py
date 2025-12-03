import json
from typing import List, AsyncGenerator

from loguru import logger
from openai import OpenAI

from src.repositories.chat_repository import (
    get_chat_session_by_session_id,
    create_chat_session,
    update_chat_session
)
from src.schemas.chat import ChatSessionRequest


class ChatSessionManager:
    """
    封装 AI 调用 & 会话存储
    自动：
    - 读取历史
    - 添加 user 消息
    - 调用 openai
    - 添加 assistant 消息
    - 保存回 MongoDB
    """

    def __init__(
            self,
            session_id: str,
            user_id: str,
            model: str = "qwen",
            api_key: str = "zhaokunmingshidashuaibi.",
            base_url: str = "https://cm-vrag.sci-brain.cn/api/v1"

    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.session_id = session_id
        self.user_id = user_id
        self.model = model
        self.messages: List = []

    # ------------------ 1. 初始化加载历史 --------------------

    async def load_or_create(self):
        """加载已有会话，或创建一个新的"""
        session = await get_chat_session_by_session_id(self.session_id)

        if session:
            logger.info(f"Loaded existing session: {self.session_id}")
            self.messages = session.messages
            return

        logger.info(f"No session found. Create new session: {self.session_id}")
        new_session = await create_chat_session(
            user_id=self.user_id,
            session_id=self.session_id,
            messages=[]
        )
        self.messages = new_session.messages

    # ------------------ 2. 增加消息 --------------------

    def add_user_message(self, text: str):
        self.messages.append({"role": "user", "content": text})

    def add_assistant_message(self, text: str):
        self.messages.append({"role": "assistant", "content": text})

    # ------------------ 3. 调用 OpenAI --------------------

    async def chat(self, user_text: str) -> str:
        """主方法：处理对话 & 保存到 MongoDB"""

        # 1. 添加 user 消息
        self.add_user_message(user_text)

        # 2. 调用 openai
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        reply = resp.choices[0].message["content"]

        # 3. 保存 assistant 消息
        self.add_assistant_message(reply)

        # 4. 更新 MongoDB
        await update_chat_session(
            user_id=self.user_id,
            session_id=self.session_id,
            messages=self.messages
        )

        return reply


def get_user_content(user_text: str):
    return {"role": "user", "content": user_text}


def get_assistant_content(assistant_text: str):
    return {"role": "assistant", "content": assistant_text}


class StreamChatSessionManager:
    """
    支持流式输出（yield）的 OpenAI 会话管理器
    自动：
    - 读取历史
    - 追加 user / assistant 消息
    - stream=True 实时输出
    - 记录整体 assistant 回复到 MongoDB
    """

    def __init__(
            self,
            session_id: str,
            user_id: str,
            model: str = "qwen",
            api_key: str = "zhaokunmingshidashuaibi.",
            base_url: str = "https://cm-vrag.sci-brain.cn/api/v1"

    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.session_id = session_id
        self.user_id = user_id
        self.model = model
        self.messages: List = []

    # ------------------ 加载会话 ------------------
    async def load_or_create(self):
        session = await get_chat_session_by_session_id(self.session_id)
        if session:
            logger.info(f"Loaded session {self.session_id}")
            self.messages = session.messages
        else:
            logger.info(f"Creating new session {self.session_id}")
            new_session = await create_chat_session(self.user_id, self.session_id, [])
            self.messages = new_session.messages

    # ------------------ 流式对话 ------------------
    async def stream_chat(self, user_text: str) -> AsyncGenerator[str, None]:
        """
        流式输出的对话流程：
        1. 插入 user 消息
        2. 调用 OpenAI stream=True
        3. yield 每个 chunk
        4. 全部结束后，拼接完整回答并写回 MongoDB
        """

        # 1. 添加 user 消息
        self.messages.append(get_user_content(user_text))

        # 2. 创建 stream 连接
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )

        final_answer = ""

        # 3. 流式读取
        for event in stream:
            delta = event.choices[0].delta
            chunk = delta.content

            if chunk:
                final_answer += chunk
                yield chunk

        # 4. assistant 完整回复写入会话
        self.messages.append(get_assistant_content(final_answer))

        # 5. 保存到 MongoDB
        await update_chat_session(
            user_id=self.user_id,
            session_id=self.session_id,
            messages=self.messages
        )


def get_default_model_stream(session_id: str, user_id: str, chunk: str, event: str = 'add'):
    return {
        'event': event,
        'data': json.dumps({
            'session_id': session_id,
            'user_id': user_id,
            'data': {
                'content': chunk
            },
        }, ensure_ascii=False)
    }


async def return_model_message(chat_request: ChatSessionRequest):
    manager = StreamChatSessionManager(
        session_id=chat_request.session_id,
        user_id=chat_request.user_id
    )
    await manager.load_or_create()

    async for chunk in manager.stream_chat(chat_request.prompt):
        yield get_default_model_stream(chat_request.session_id, chat_request.user_id, chunk)

    yield get_default_model_stream(chat_request.session_id, chat_request.user_id, '\n\n', event='finish')
