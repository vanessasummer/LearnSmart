"""用户模型"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
