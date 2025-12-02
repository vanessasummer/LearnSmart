"""分析报告API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/{child_id}")
async def get_analysis(child_id: int, db: AsyncSession = Depends(get_db)):
    """获取分析报告"""
    return {"child_id": child_id, "report": {}}
