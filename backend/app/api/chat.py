"""对话API"""
# ai_diary_backend/api/chat.py
from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from services.ai_engine import ai_engine

router = APIRouter()

@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    发送对话消息
    """
    try:
        result = await ai_engine.chat(
            child_id=request.child_id,
            message=request.message,
            conversation_id=request.conversation_id,
            mode=request.mode
        )
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            message=result["reply"],
            mode=result["mode"],
            turn_count=1,  # TODO: 从数据库计算实际轮次
            extracted_info=result["extracted_info"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
