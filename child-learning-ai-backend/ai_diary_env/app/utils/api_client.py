"""豆包API客户端"""
import httpx
from app.config import settings

class DouBaoClient:
    """豆包API客户端（待实现）"""
    def __init__(self):
        self.api_key = settings.DOUBAO_API_KEY
    
    async def chat(self, message: str):
        return "AI回复"
