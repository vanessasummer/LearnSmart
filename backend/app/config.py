"""应用配置管理"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# 获取backend目录的绝对路径
_backend_dir = Path(__file__).parent.parent
_env_file = _backend_dir / ".env"

class Settings(BaseSettings):
    APP_NAME: str = "儿童学习记录AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # ✅ 修改:使用绝对路径
    DATABASE_URL: str = str(_backend_dir / "data" / "learning_ai.db")
    
    DOUBAO_API_KEY: str = ""
    DOUBAO_API_URL: str = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    DOUBAO_MODEL: str = ""
    DOUBAO_MODEL_ID: str = ""
    DOUBAO_API_SECRET: str = ""
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = ""
    
    class Config:
        env_file = str(_env_file) if _env_file.exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
