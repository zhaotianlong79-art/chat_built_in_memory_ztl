import traceback
from typing import List, Optional

from loguru import logger

from src.models.mongo import ChatHistory


async def create_chat_session(
        user_id: str,
        session_id: str,
        messages: Optional[List] = None
) -> ChatHistory:
    """
    创建新的聊天会话

    Args:
        user_id: 用户ID
        session_id: 会话ID
        messages: 消息列表，默认为空列表

    Returns:
        ChatHistory: 创建的会话对象
    """
    if messages is None:
        messages = []

    session = ChatHistory.objects.create(
        session_id=session_id,
        user_id=user_id,
        messages=messages
    )
    return session


async def get_chat_session_by_user_id(user_id: str) -> Optional[ChatHistory]:
    """
    根据用户ID获取聊天会话

    Args:
        user_id: 用户ID

    Returns:
        Optional[ChatHistory]: 会话对象，如果不存在则返回None
    """
    try:
        return ChatHistory.objects.get(user_id=user_id)
    except Exception as e:
        logger.error(f"Error getting chat session by user_id: {traceback.format_exception()}")
        return None


async def get_chat_session_by_session_id(session_id: str) -> Optional[ChatHistory]:
    """
    根据会话ID获取聊天会话

    Args:
        session_id: 会话ID

    Returns:
        Optional[ChatHistory]: 会话对象，如果不存在则返回None
    """
    try:
        return ChatHistory.objects(session_id=session_id).first()
    except Exception as e:
        logger.error(f"Error getting chat session by session_id: {traceback.format_exception(e)}")
        return None


async def update_chat_session(
        user_id: str,
        session_id: str,
        messages: List
) -> Optional[ChatHistory]:
    """
    更新聊天会话的消息

    Args:
        user_id: 用户ID
        session_id: 会话ID
        messages: 新的消息列表

    Returns:
        Optional[ChatHistory]: 更新后的会话对象，如果不存在则返回None
    """
    try:
        session = ChatHistory.objects.get(user_id=user_id, session_id=session_id)
        session.messages = messages
        session.save()
        return session
    except Exception as e:
        logger.error(f"Error updating chat session: {traceback.format_exception()}")
        return None


async def delete_chat_session(user_id: str, session_id: str):
    try:
        # 获取用户的会话
        session = ChatHistory.objects.get(user_id=user_id, session_id=session_id)
        # 删除会话
        session.delete()
        return True
    except Exception as e:
        # 如果会话不存在，返回False
        logger.error(f"Chat session with user_id {user_id} and session_id {session_id} does not exist")
        return False
