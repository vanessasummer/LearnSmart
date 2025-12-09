"""
记忆服务 - 聚合5维成长数据
用于为AI对话提供孩子的历史记忆和成长画像
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.config import settings
import logging

logger = logging.getLogger("LearnSmart")


class MemoryService:
    """记忆服务 - 管理孩子的成长记忆"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_URL
    
    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def get_child_memory(
        self, 
        child_id: int, 
        days: Optional[int] = 7
    ) -> Dict[str, Any]:
        """
        获取孩子的综合记忆
        
        Args:
            child_id: 孩子ID
            days: 查询最近N天的数据(None=全部)
        
        Returns:
            包含5维度数据的记忆字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 计算时间过滤条件
        time_filter = ""
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            time_filter = f"AND created_at >= '{cutoff_date}'"
        
        memory = {
            "knowledge": self._get_knowledge_memory(cursor, child_id, time_filter),
            "writing": self._get_writing_memory(cursor, child_id, time_filter),
            "social": self._get_social_memory(cursor, child_id, time_filter),
            "emotion": self._get_emotion_memory(cursor, child_id, time_filter),
            "personality": self._get_personality_traits(cursor, child_id),
            "user_profile": self._get_user_profile(cursor, child_id),
            "deep_interests": self._get_deep_interests(cursor, child_id),
        }
        
        conn.close()
        return memory
    
    def _get_knowledge_memory(
        self, 
        cursor: sqlite3.Cursor, 
        child_id: int, 
        time_filter: str
    ) -> Dict[str, Any]:
        """获取知识维度记忆"""
        # 统计主动/被动学习
        cursor.execute(f"""
            SELECT 
                source,
                COUNT(*) as count
            FROM knowledge_points
            WHERE child_id = ? {time_filter}
            GROUP BY source
        """, (child_id,))
        learning_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 学科分布
        cursor.execute(f"""
            SELECT 
                subject,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence
            FROM knowledge_points
            WHERE child_id = ? {time_filter}
            GROUP BY subject
            ORDER BY count DESC
            LIMIT 5
        """, (child_id,))
        subjects = [
            {
                "subject": row[0],
                "count": row[1],
                "avg_confidence": round(row[2], 2) if row[2] else 0
            }
            for row in cursor.fetchall()
        ]
        
        # 最近学习内容(最近3条)
        cursor.execute(f"""
            SELECT 
                subject,
                content,
                source,
                created_at
            FROM knowledge_points
            WHERE child_id = ? {time_filter}
            ORDER BY created_at DESC
            LIMIT 3
        """, (child_id,))
        recent_learning = [
            {
                "subject": row[0],
                "content": row[1],
                "source": row[2],
                "date": row[3][:10]  # 只取日期部分
            }
            for row in cursor.fetchall()
        ]
        
        return {
            "learning_stats": learning_stats,
            "subjects": subjects,
            "recent_learning": recent_learning
        }
    
    def _get_writing_memory(
        self, 
        cursor: sqlite3.Cursor, 
        child_id: int, 
        time_filter: str
    ) -> Dict[str, Any]:
        """获取表达维度记忆"""
        # 最近的写作素材
        cursor.execute(f"""
            SELECT 
                event_description,
                event_time,
                location,
                people,
                created_at
            FROM writing_materials
            WHERE child_id = ? {time_filter}
            ORDER BY created_at DESC
            LIMIT 5
        """, (child_id,))
        
        materials = []
        for row in cursor.fetchall():
            try:
                people = json.loads(row[3]) if row[3] else []
            except:
                people = []
            
            materials.append({
                "description": row[0][:50] + "..." if len(row[0]) > 50 else row[0],
                "event_time": row[1],
                "location": row[2],
                "people_count": len(people),
                "date": row[4][:10]
            })
        
        # 常去地点统计
        cursor.execute(f"""
            SELECT 
                location,
                COUNT(*) as count
            FROM writing_materials
            WHERE child_id = ? AND location IS NOT NULL {time_filter}
            GROUP BY location
            ORDER BY count DESC
            LIMIT 3
        """, (child_id,))
        
        locations = [{"location": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "recent_materials": materials,
            "frequent_locations": locations
        }
    
    def _get_social_memory(
        self, 
        cursor: sqlite3.Cursor, 
        child_id: int, 
        time_filter: str
    ) -> Dict[str, Any]:
        """获取社交维度记忆"""
        # 关系类型统计
        cursor.execute(f"""
            SELECT 
                relationship_type,
                COUNT(*) as count
            FROM social_events
            WHERE child_id = ? {time_filter}
            GROUP BY relationship_type
        """, (child_id,))
        relationships = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 行为模式统计
        cursor.execute(f"""
            SELECT 
                behavior_pattern,
                COUNT(*) as count
            FROM social_events
            WHERE child_id = ? AND behavior_pattern IS NOT NULL {time_filter}
            GROUP BY behavior_pattern
            ORDER BY count DESC
        """, (child_id,))
        behaviors = [{"pattern": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # 最近社交事件
        cursor.execute(f"""
            SELECT 
                relationship_type,
                behavior_pattern,
                substr(event_context, 1, 50) as context,
                created_at
            FROM social_events
            WHERE child_id = ? {time_filter}
            ORDER BY created_at DESC
            LIMIT 3
        """, (child_id,))
        recent_events = [
            {
                "relationship": row[0],
                "behavior": row[1],
                "context": row[2],
                "date": row[3][:10]
            }
            for row in cursor.fetchall()
        ]
        
        return {
            "relationships": relationships,
            "behaviors": behaviors,
            "recent_events": recent_events
        }
    
    def _get_emotion_memory(
        self, 
        cursor: sqlite3.Cursor, 
        child_id: int, 
        time_filter: str
    ) -> Dict[str, Any]:
        """获取情绪维度记忆"""
        # 情绪类型统计
        cursor.execute(f"""
            SELECT 
                emotion_type,
                COUNT(*) as count,
                AVG(intensity) as avg_intensity
            FROM emotions
            WHERE child_id = ? {time_filter}
            GROUP BY emotion_type
        """, (child_id,))
        emotion_stats = [
            {
                "type": row[0],
                "count": row[1],
                "avg_intensity": round(row[2], 1) if row[2] else 0
            }
            for row in cursor.fetchall()
        ]
        
        # 最近情绪记录
        cursor.execute(f"""
            SELECT 
                emotion_type,
                intensity,
                substr(trigger_event, 1, 50) as trigger,
                created_at
            FROM emotions
            WHERE child_id = ? {time_filter}
            ORDER BY created_at DESC
            LIMIT 5
        """, (child_id,))
        recent_emotions = [
            {
                "type": row[0],
                "intensity": row[1],
                "trigger": row[2],
                "date": row[3][:10]
            }
            for row in cursor.fetchall()
        ]
        
        return {
            "emotion_stats": emotion_stats,
            "recent_emotions": recent_emotions
        }
    
   
    def _get_personality_traits(
    self, 
    cursor: sqlite3.Cursor, 
    child_id: int
    ) -> List[Dict[str, Any]]:
        """获取性格特质"""
        try:
            cursor.execute("""
                SELECT 
                    trait_category,
                    trait_description,
                    evidence_examples
                FROM personality_traits
                WHERE child_id = ?
                ORDER BY created_at DESC
            """, (child_id,))
            
            return [
                {
                    "trait": row[0],
                    "description": row[1],
                    "evidence": row[2]
                }
                for row in cursor.fetchall()
            ]
        except Exception as e:
            logger.error(f"获取性格特质失败: {e}")
            return []

    def _get_user_profile(
        self, 
        cursor: sqlite3.Cursor, 
        child_id: int
    ) -> Dict[str, str]:
        """获取用户画像基础信息"""
        try:
            cursor.execute("""
                SELECT 
                    info_type,
                    content
                FROM user_memory
                WHERE child_id = ?
            """, (child_id,))
            
            profile = {}
            for row in cursor.fetchall():
                profile[row[0]] = row[1]
            
            # 如果没有用户画像,从children表获取基础信息
            if not profile:
                cursor.execute("""
                    SELECT 
                        name,
                        grade_level,
                        health_notes
                    FROM children
                    WHERE id = ?
                """, (child_id,))
                row = cursor.fetchone()
                if row:
                    profile = {
                        "name": row[0],
                        "grade": row[1],
                        "health": row[2]
                    }
            
            return profile
        except Exception as e:
            logger.error(f"获取用户画像失败: {e}")
            return {}

    def _get_deep_interests(
        self, 
        cursor: sqlite3.Cursor, 
        child_id: int
    ) -> List[Dict[str, Any]]:
        """获取深度兴趣"""
        try:
            cursor.execute("""
                SELECT 
                    topic,
                    inquiry_count,
                    is_deep_interest,
                    last_mentioned_at
                FROM interest_intensity
                WHERE child_id = ?
                ORDER BY inquiry_count DESC
                LIMIT 5
            """, (child_id,))
            
            return [
                {
                    "topic": row[0],
                    "inquiry_count": row[1],
                    "is_deep": bool(row[2]),
                    "last_mentioned": row[3]
                }
                for row in cursor.fetchall()
            ]
        except Exception as e:
            logger.error(f"获取深度兴趣失败: {e}")
            return []

    
    def generate_memory_summary(self, child_id: int, days: int = 7) -> str:
        """
        生成记忆摘要文本(供System Prompt使用)
        
        Args:
            child_id: 孩子ID
            days: 统计最近N天
        
        Returns:
            格式化的记忆摘要文本
        """
        memory = self.get_child_memory(child_id, days)
        
        summary_parts = []
        
        # 1. 用户基础信息
        profile = memory["user_profile"]
        if profile:
            summary_parts.append(f"【基础信息】")
            if "name" in profile:
                summary_parts.append(f"孩子姓名: {profile['name']}")
            if "grade" in profile:
                summary_parts.append(f"年级: {profile['grade']}")
        
        # 2. 最近学习情况
        knowledge = memory["knowledge"]
        if knowledge["learning_stats"]:
            active = knowledge["learning_stats"].get("active", 0)
            passive = knowledge["learning_stats"].get("passive", 0)
            total = active + passive
            summary_parts.append(f"\n【最近{days}天学习】")
            summary_parts.append(f"共学习{total}个知识点, 主动学习{active}次, 被动学习{passive}次")
            
            if knowledge["subjects"]:
                top_subjects = ", ".join([s["subject"] for s in knowledge["subjects"][:3]])
                summary_parts.append(f"主要学科: {top_subjects}")
        
        # 3. 最近兴趣和活动
        if knowledge["recent_learning"]:
            summary_parts.append(f"\n【最近学习内容】")
            for item in knowledge["recent_learning"][:2]:
                summary_parts.append(f"- {item['subject']}: {item['content']}")
        
        # 4. 社交情况
        social = memory["social"]
        if social["relationships"]:
            summary_parts.append(f"\n【社交情况】")
            rel_text = ", ".join([f"{k}互动{v}次" for k, v in social["relationships"].items()])
            summary_parts.append(rel_text)
        
        # 5. 情绪状态
        emotion = memory["emotion"]
        if emotion["emotion_stats"]:
            summary_parts.append(f"\n【情绪状态】")
            for stat in emotion["emotion_stats"]:
                summary_parts.append(
                    f"{stat['type']}情绪{stat['count']}次(平均强度{stat['avg_intensity']})"
                )
        
        # 6. 深度兴趣
        if memory["deep_interests"]:
            summary_parts.append(f"\n【深度兴趣】")
            interests = ", ".join([i["topic"] for i in memory["deep_interests"][:3]])
            summary_parts.append(interests)
        
        return "\n".join(summary_parts)


# 单例模式
memory_service = MemoryService()
