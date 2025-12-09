from fastapi import APIRouter

from src.api.chat import router as chat
from src.api.doc2kb import router as doc

api_router = APIRouter()

api_router.include_router(chat, prefix="/chat", tags=["chat"])
api_router.include_router(doc, prefix="/doc", tags=["doc"])
