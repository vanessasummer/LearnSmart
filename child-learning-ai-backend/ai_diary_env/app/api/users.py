"""用户API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.post("/children")
async def create_child(db: AsyncSession = Depends(get_db)):
    """创建孩子档案"""
    return {"child_id": 1}

@router.get("/children/{child_id}")
async def get_child(child_id: int, db: AsyncSession = Depends(get_db)):
    """获取孩子信息"""
    return {"child_id": child_id, "name": "芋圆"}
