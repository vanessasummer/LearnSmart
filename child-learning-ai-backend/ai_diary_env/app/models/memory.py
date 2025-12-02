"""Memory模型"""
from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True)
    key = Column(String(100))
    value = Column(Text)
