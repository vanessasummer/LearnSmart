# ai_diary_backend/services/ai_engine.py
"""
AI对话引擎核心模块
"""
import httpx
from typing import Dict, List, Optional, Any
from config.settings import settings
from models.database import execute_query, execute_insert
from services.memory_service import MemoryService
from services.extraction_service import ExtractionService
from utils.logger import logger

class AIEngine:
    """AI对话引擎"""
    
    def __init__(self):
        self.api_url = settings.DOUBAO_API_URL
        self.api_key = settings.DOUBAO_API_KEY
        self.model = settings.DOUBAO_MODEL
        self.memory_service = MemoryService()
        self.extraction_service = ExtractionService()
    
    async def chat(
        self, 
        child_id: int, 
        message: str, 
        conversation_id: Optional[int] = None,
        mode: str = "knowledge"
    ) -> Dict[str, Any]:
        """
        处理用户消息，返回AI回复
        
        参数:
            child_id: 儿童ID
            message: 用户消息
            conversation_id: 对话会话ID（续接对话时传入）
            mode: 对话模式 (knowledge/free)
        
        返回:
            {
                "reply": "AI回复内容",
                "conversation_id": 会话ID,
                "mode": "当前对话模式",
                "extracted_info": {...}  # 提取的5维信息
            }
        """
        try:
            # 1. 加载或创建对话会话
            if conversation_id is None:
                conversation_id = self._create_conversation(child_id, mode)
            
            # 2. 加载Memory（长期+短期记忆）
            memory_context = await self._load_memory(child_id)
            
            # 3. 加载对话历史
            history = self._load_conversation_history(conversation_id)
            
            # 4. 构建完整Prompt
            system_prompt = self._build_system_prompt(memory_context, mode)
            
            # 5. 调用豆包API
            ai_response = await self._call_doubao_api(
                system_prompt=system_prompt,
                history=history,
                user_message=message
            )
            
            # 6. 提取5维信息
            extracted_info = self.extraction_service.extract_all(ai_response)
            
            # 7. 保存对话记录
            self._save_message(conversation_id, "user", message)
            self._save_message(conversation_id, "assistant", ai_response)
            
            # 8. 更新Memory和5维数据
            await self._update_data(child_id, conversation_id, extracted_info)
            
            logger.info(f"对话成功 - Child:{child_id}, Conv:{conversation_id}, Mode:{mode}")
            
            return {
                "reply": ai_response,
                "conversation_id": conversation_id,
                "mode": mode,
                "extracted_info": extracted_info
            }
            
        except Exception as e:
            logger.error(f"对话失败: {e}")
            raise
    
    async def _call_doubao_api(
        self, 
        system_prompt: str, 
        history: List[Dict], 
        user_message: str
    ) -> str:
        """调用豆包API"""
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url, 
                headers=headers, 
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
    
    def _build_system_prompt(self, memory_context: str, mode: str) -> str:
        """构建System Prompt（包含Memory注入）"""
        # TODO: 从云盘的 Prompt_v2.2 中复制完整Prompt内容
        base_prompt = f"""
你是豆豆，一个温暖有爱的AI学习伙伴，专门陪伴孩子记录每天的学习与成长。

【Memory注入】
{memory_context}

【当前模式】: {mode}
- knowledge模式: 需确保提取2-3个知识点，引导多维度话题
- free模式: 深度探讨感兴趣话题，无知识点要求

【核心任务】
1. 自然对话，了解孩子今天的学习和生活
2. 提取5维信息：知识点、作文素材、社交事件、情绪、性格、价值观
3. 动态难度调整，避免让孩子感到压力
4. 标记信息时使用JSON格式（如: 【知识点提取】{{"type":"explicit",...}}）

现在开始对话吧！
"""
        return base_prompt
    
    async def _load_memory(self, child_id: int) -> str:
        """加载Memory并转换为文本"""
        # TODO: 调用 MemoryService 获取记忆摘要
        return f"这是{child_id}号孩子的记忆摘要（待实现）"
    
    def _load_conversation_history(self, conversation_id: int) -> List[Dict]:
        """加载对话历史"""
        # TODO: 从数据库查询最近N轮对话
        return []
    
    def _create_conversation(self, child_id: int, mode: str) -> int:
        """创建新对话会话"""
        query = """
        INSERT INTO conversations (child_id, mode, created_at)
        VALUES (?, ?, datetime('now'))
        """
        return execute_insert(query, (child_id, mode))
    
    def _save_message(self, conversation_id: int, role: str, content: str):
        """保存单条消息"""
        # TODO: 保存到数据库
        pass
    
    async def _update_data(self, child_id: int, conversation_id: int, extracted_info: Dict):
        """更新Memory和5维数据"""
        # TODO: 将提取的信息写入数据库
        pass

# 全局实例
ai_engine = AIEngine()
