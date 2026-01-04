import json
from typing import List, AsyncGenerator

from loguru import logger
from openai import OpenAI

from src.config.config import settings
from src.repositories.chat_repository import (
    create_chat_session,
    get_chat_session,
    update_chat_session
)
from src.schemas.chat_schemas import ChatSessionRequest


def get_user_content(user_text: str):
    return {"role": "user", "content": user_text}


def get_assistant_content(assistant_text: str):
    return {"role": "assistant", "content": assistant_text}


def get_system_content(system_text: str):
    return {"role": "system", "content": system_text}


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
            model: str = settings.MODEL_NAME,
            api_key: str = settings.MODEL_API_KEY,
            base_url: str = settings.MODEL_BASE_URL
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.session_id = session_id
        self.user_id = user_id
        self.model = model
        self.messages: List[dict] = []  # 明确类型注解

    # ------------------ 加载会话 ------------------
    async def load_or_create(self):
        """加载或创建会话，初始化 self.messages"""
        try:
            session = await get_chat_session(
                user_id=self.user_id,
                session_id=self.session_id
            )

            if session:
                logger.info(f"Loaded session {self.session_id}")
                self.messages = [dict(m) for m in (session.messages or [])]
            else:
                logger.info(f"Creating new session {self.session_id}")
                # 创建空会话
                await create_chat_session(
                    user_id=self.user_id,
                    session_id=self.session_id,
                )

        except Exception as e:
            logger.error(f"Error loading session: {e}")
            self.messages = []

    # ------------------ 流式对话 ------------------
    async def stream_chat(self, user_text: str) -> AsyncGenerator[str, None]:
        """流式对话并保存完整 messages"""

        # 1. 添加 user 消息到本地内存
        user_message = get_user_content(user_text)
        self.messages.append(user_message)

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

        # 4. 添加 assistant 回复到本地内存
        assistant_message = get_assistant_content(final_answer)
        self.messages.append(assistant_message)
        await self._save_message()

    async def _save_message(self, ) -> bool:

        try:

            res = await update_chat_session(
                user_id=self.user_id,
                session_id=self.session_id,
                messages=self.messages
            )
            if res:
                logger.info(f"Saved message for session {self.session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to save full messages: {e}")
            return False

    async def clear_messages(self):
        """清空消息历史"""
        self.messages = []
        await self._save_full_messages()
        logger.info(f"Cleared messages for session {self.session_id}")

    async def get_message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)

    async def reload_messages(self):
        """从数据库重新加载 messages"""
        await self.load_or_create()


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
