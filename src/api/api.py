from fastapi import APIRouter

from src.api import chat

api_router = APIRouter()

api_router.include_router(chat, prefix="/chat", tags=["chat"])
