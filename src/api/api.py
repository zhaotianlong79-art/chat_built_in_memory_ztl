from fastapi import APIRouter

from src.api.chat import router as chat

api_router = APIRouter()

api_router.include_router(chat, prefix="/chat", tags=["chat"])
