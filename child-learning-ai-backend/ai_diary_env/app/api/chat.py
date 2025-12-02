"""对话API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.post("/send")
async def send_message(db: AsyncSession = Depends(get_db)):
    """发送消息"""
    return {"message": "AI回复（待实现）"}

@router.get("/history/{conversation_id}")
async def get_history(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """获取对话历史"""
    return {"conversation_id": conversation_id, "messages": []}
