from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from src.schemas.chat_schemas import ChatSessionRequest
from src.service.chat_service import return_model_message

router = APIRouter()


@router.post("/stream")
async def chat_stream(chat_request: ChatSessionRequest):
    return EventSourceResponse(return_model_message(chat_request), media_type="text/event-stream")

@router.post("/ai/coder")
async def chat_stream(chat_request: ChatSessionRequest):
    return EventSourceResponse(return_model_message(chat_request), media_type="text/event-stream")
