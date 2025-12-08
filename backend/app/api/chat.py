"""对话API"""
# ai_diary_backend/api/chat.py
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.ai_engine import AIEngine

router = APIRouter()
# 创建实例
ai_engine = AIEngine()

@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """发送消息"""
    try:
        # 调用AI引擎
        result = await ai_engine.chat(
            child_id=request.child_id,
            message=request.message,
            mode=request.mode
        )
        
        # 检查结果
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "AI对话失败"))
        
        # 返回响应
        return ChatResponse(
            message=result.get("response", ""),
            conversation_id=result.get("conversation_id", 0)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

