# backend/app/core/ai_engine.py
"""
AI对话引擎核心模块 - 使用火山引擎SDK
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

import sqlite3  # 数据库


# HTTP请求
import requests

from app.config import settings
from app.database import get_db_connection
from app.utils.logger import logger

class AIEngine:
    """AI对话引擎"""
    
    def __init__(self):
        self.api_url = settings.DOUBAO_API_URL
        self.api_key = settings.DOUBAO_API_KEY
        self.model = settings.DOUBAO_MODEL
    
    async def chat(
        self, 
        child_id: int, 
        message: str, 
        conversation_id: Optional[int] = None,
        mode: str = "knowledge"
    ) -> Dict[str, Any]:
        """核心对话方法（与之前相同）"""
        try:
            logger.info(f"🚀 开始对话 - Child:{child_id}, Mode:{mode}")
            
            # 1-4步骤与之前相同
            if conversation_id is None:
                conversation_id = self._create_conversation(child_id, mode)
                logger.info(f"📝 创建新对话会话: {conversation_id}")
            
            memory_context = self._load_memory_simple(child_id)
            history = self._load_conversation_history(conversation_id)
            system_prompt = self._build_system_prompt(memory_context, mode)
            
            # 5. 调用豆包API（使用新方法）
            logger.info(f"🤖 调用豆包API...")
            ai_response = self._call_doubao_api_with_sdk(
                system_prompt=system_prompt,
                history=history,
                user_message=message
            )
            logger.info(f"✅ AI回复成功: {ai_response[:50]}...")
            
            # 6-8步骤与之前相同
            extracted_info = self._extract_and_save_info(
                conversation_id=conversation_id,
                child_id=child_id,
                user_message=message,
                ai_response=ai_response
            )
            self._save_message(conversation_id, "user", message)
            self._save_message(conversation_id, "assistant", ai_response)
            turn_count = self._get_turn_count(conversation_id)
            
            logger.info(f"🎉 对话完成 - Conv:{conversation_id}, Turns:{turn_count}")
            
            return {
                "success": True,  # 添加
                "response": ai_response,  # 改字段名
                "mode": mode,
                "turn_count": turn_count,
                "extracted_info": extracted_info
            }
            
        except Exception as e:
            logger.error(f"❌ 对话失败: {e}", exc_info=True)
            # ✅ 添加错误返回
            return {
                "success": False,
                "error": str(e)
            }
    
    def _call_doubao_api_with_sdk(
        self, 
        system_prompt: str, 
        history: List[Dict], 
        user_message: str
    ) -> str:
        """
        调用豆包API（使用Bearer Token认证）
        """
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        # 请求体
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        # 设置请求头（使用Bearer Token）
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 调试信息
        logger.debug(f"API URL: {self.api_url}")
        logger.debug(f"API Key: {self.api_key[:20]}..." if self.api_key else "API Key: EMPTY")
        logger.debug(f"Model: {self.model}")
        
        # 发送请求
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"API请求失败: {e}")
            logger.error(f"响应状态码: {response.status_code}")
            logger.error(f"响应内容: {response.text[:200]}")
            raise
        
        # 解析响应
        data = response.json()
        ai_reply = data['choices'][0]['message']['content']
        return ai_reply
    
    # 其他方法保持不变
    def _build_system_prompt(self, memory_context: str, mode: str) -> str:
        """构建System Prompt（与之前相同）"""
        base_prompt = f"""
你是豆豆,一个温暖有爱的AI学习伙伴,专门陪伴孩子记录每天的学习与成长。

【Memory注入】
{memory_context}

【当前模式】: {mode}
- knowledge模式: 需确保提取2-3个知识点,引导多维度话题
- free模式: 深度探讨感兴趣话题,无知识点要求

【核心任务】
1. 用自然、亲切的语气与孩子对话
2. 了解孩子今天的学习和生活
3. 引导孩子分享更多细节
4. 适时给予鼓励和肯定

【对话风格】
- 称呼孩子的名字,让对话更亲切
- 使用简单、生动的语言
- 适当使用emoji增加趣味性
- 避免说教,多倾听

现在开始对话吧！记住,你是孩子的好朋友豆豆 🌟
"""
        return base_prompt
    
    def _load_memory_simple(self, child_id: int) -> str:
        return f"孩子ID: {child_id}\n这是第一次对话,暂无历史记忆。"
    
    def _load_conversation_history(self, conversation_id: int) -> List[Dict]:
        return []
    
    def _extract_and_save_info(
    self, 
    conversation_id: int,
    child_id: int,
    user_message: str,
    ai_response: str
    ) -> Dict:
        """提取并保存5维信息"""
        
        conn = sqlite3.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        
        result = {}
        
        # 1. 知识维度 - 学习来源
        source = "active"
        if any(word in user_message for word in ["老师", "爸妈", "上课", "教了", "讲了"]):
            source = "passive"
        
        # 2. 知识维度 - 学科分类
        subject = "其他"
        subject_keywords = {
            "数学": ["数学", "几何", "代数", "勾股定理", "方程", "立方体", "体积", "面积", "计算"],
            "物理": ["物理", "力", "惯性", "密度", "速度", "能量", "摩擦", "运动"],
            "化学": ["化学", "反应", "元素", "分子", "酸碱"],
            "生物": ["生物", "光合作用", "细胞", "DNA", "植物", "动物"],
            "语文": ["语文", "作文", "古诗", "成语", "阅读", "写作"],
            "英语": ["英语", "单词", "语法", "句子"],
            "地理": ["地理", "经纬度", "地图", "气候"],
            "历史": ["历史", "朝代", "事件"]
        }
        
        for subj, keywords in subject_keywords.items():
            if any(kw in user_message or kw in ai_response for kw in keywords):
                subject = subj
                break
        
        # 存入knowledge_points
        cursor.execute("""
            INSERT INTO knowledge_points 
            (child_id, conversation_id, source, subject, content, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
        """, (child_id, conversation_id, source, subject, user_message[:200]))
        
        result["knowledge"] = {"source": source, "subject": subject}
        
        # 3. 社交维度
        social_keywords = ["同学", "朋友", "老师", "爸妈", "打架", "吵架", "一起", "帮助", "玩"]
        if any(kw in user_message for kw in social_keywords):
            relationship_type = "peer"
            if "老师" in user_message:
                relationship_type = "teacher"
            elif any(w in user_message for w in ["爸", "妈", "家人"]):
                relationship_type = "family"
            
            cursor.execute("""
                INSERT INTO social_events 
                (child_id, conversation_id, relationship_type, event_context, created_at)
                VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
            """, (child_id, conversation_id, relationship_type, user_message[:500]))
            
            result["social"] = {"relationship_type": relationship_type}
        
        # 4. 情绪维度
        emotion_keywords = {
            "positive": ["开心", "高兴", "快乐", "兴奋", "满意", "喜欢", "棒", "好"],
            "negative": ["难过", "伤心", "生气", "害怕", "紧张", "担心", "疼"],
            "neutral": ["还好", "一般", "平静"]
        }
        
        detected_emotion = None
        emotion_type = "neutral"
        
        for emo_type, keywords in emotion_keywords.items():
            if any(kw in user_message for kw in keywords):
                emotion_type = emo_type
                detected_emotion = next((kw for kw in keywords if kw in user_message), None)
                break
        
        if detected_emotion:
            intensity = 7 if emotion_type == "positive" else 5
            
            cursor.execute("""
                INSERT INTO emotions 
                (child_id, conversation_id, emotion_type, intensity, trigger_event, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
            """, (child_id, conversation_id, emotion_type, intensity, user_message[:200]))
            
            result["emotion"] = {"type": emotion_type, "intensity": intensity}
        
        # 5. 表达维度 - 写作素材
        event_indicators = ["今天", "昨天", "刚才", "下午", "放学", "在", "和"]
        if any(ind in user_message for ind in event_indicators) and len(user_message) > 15:
            cursor.execute("""
                INSERT INTO writing_materials 
                (child_id, conversation_id, event_description, created_at)
                VALUES (?, ?, ?, datetime('now', 'localtime'))
            """, (child_id, conversation_id, user_message[:500]))
            
            result["writing"] = True
        
        conn.commit()
        conn.close()
        
        logger.info(f"📊 提取信息: {result}")
        return result

    
    def _create_conversation(self, child_id: int, mode: str) -> int:
        """创建新对话会话"""
        import os
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"DATABASE_URL: {settings.DATABASE_URL}")
        logger.info(f"数据库文件存在? {os.path.exists(settings.DATABASE_URL)}")
        conn = sqlite3.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (child_id, conversation_mode, start_time, is_active)
            VALUES (?, ?, datetime('now', 'localtime'), 1)
        """, (child_id, mode))  # 改为conversation_mode
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✅ 创建对话会话 - ID:{conversation_id}, Mode:{mode}")
        return conversation_id

    
    def _save_message(self, conversation_id: int, role: str, content: str):
        """保存消息"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, timestamp)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        """, (conversation_id, role, content))
        
        conn.commit()
        conn.close()

    
    def _get_turn_count(self, conversation_id: int) -> int:
        """获取对话轮次（与之前相同）"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE conversation_id = ? AND role = 'user'
        """, (conversation_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count

# 全局实例
ai_engine = AIEngine()
