"""对话Schema"""
from pydantic import BaseModel

class ChatRequest(BaseModel):
    child_id: int
    message: str

class ChatResponse(BaseModel):
    message: str
    conversation_id: int
