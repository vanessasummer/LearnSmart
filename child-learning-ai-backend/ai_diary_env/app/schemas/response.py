"""通用响应Schema"""
from pydantic import BaseModel
from typing import Optional, Any

class BaseResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
