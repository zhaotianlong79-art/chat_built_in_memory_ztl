from pydantic import BaseModel, Field


class ChatSessionRequest(BaseModel):
    """Schema for chat session request"""
    user_id: str = Field(default="XXX", description="User ID")
    session_id: str = Field(default="XXX", description="Session ID")
    prompt: str = Field(default="XXX", description="Prompt")
