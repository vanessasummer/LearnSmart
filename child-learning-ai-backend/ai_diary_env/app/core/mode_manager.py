"""对话模式管理"""
from enum import Enum

class ConversationMode(str, Enum):
    FREE = "free"
    KNOWLEDGE = "knowledge"

class ModeManager:
    """模式管理器（待实现）"""
    def __init__(self):
        self.mode = ConversationMode.KNOWLEDGE
