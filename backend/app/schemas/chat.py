"""对话Schema"""
from pydantic import BaseModel

class ChatRequest(BaseModel):
    child_id: int
    message: str
    mode: str = "knowledge"  # 添加这行,默认值为knowledge

class ChatResponse(BaseModel):
    message: str
    conversation_id: int
