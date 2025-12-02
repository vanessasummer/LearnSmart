"""应用配置管理"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "儿童学习记录AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/learning_ai.db"
    DOUBAO_API_KEY: str = ""
    DOUBAO_API_SECRET: str = ""
    DOUBAO_MODEL_ID: str = ""
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
