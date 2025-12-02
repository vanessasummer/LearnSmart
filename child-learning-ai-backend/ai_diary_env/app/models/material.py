"""作文素材模型"""
from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class WritingMaterial(Base):
    __tablename__ = "writing_materials"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
