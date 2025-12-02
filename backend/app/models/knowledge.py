"""知识点模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
