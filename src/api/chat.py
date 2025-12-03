from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.schemas.chat import ChatSessionRequest
from src.service.chat import return_model_message

router = APIRouter()


@router.get("/stream")
async def chat_stream(chat_request: ChatSessionRequest):
    return StreamingResponse(return_model_message(chat_request), media_type="text/plain")
