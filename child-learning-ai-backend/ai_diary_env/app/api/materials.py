"""作文素材API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/recommend")
async def recommend(child_id: int, db: AsyncSession = Depends(get_db)):
    """推荐素材"""
    return {"materials": []}
