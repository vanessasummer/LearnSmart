# backend/app/core/ai_engine.py
"""
AI对话引擎核心模块 - 使用火山引擎SDK
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

import sqlite3  # 数据库
import json #豆包5维信息提取

# HTTP请求
import requests

from app.config import settings
from app.database import get_db_connection
from app.utils.logger import logger

from app.services.memory_service import memory_service


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
            system_prompt = self._build_system_prompt(child_id=child_id)
            
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
    
    def _call_doubao_for_extraction(self, user_message: str, ai_response: str) -> Dict:
        """
        调用豆包API进行精确的信息提取
        
        复用主对话方法,使用专门的提取Prompt
        """
        try:
            # 获取提取Prompt
            extraction_prompt = self._build_extraction_prompt()
            
            # 构建提取消息
            extraction_message = f"""请从以下对话中提取信息:

    用户消息: {user_message}
    AI回复: {ai_response}

    请严格按照JSON格式返回提取结果,不要添加任何markdown标记。"""
            
            # 复用主对话方法(降低temperature提高准确性)
            original_temp = self.model  # 暂存原始配置
            
            # 调用API
            result = self._call_doubao_api_with_sdk(
                system_prompt=extraction_prompt,
                history=[],
                user_message=extraction_message
            )
            
            logger.info(f"📥 豆包API原始返回: {result[:200]}...")
            
            # 解析JSON(处理可能的markdown包装)
            import json
            import re
            
            # 清理markdown代码块标记
            result_clean = result.strip()
            
            # 移除可能的 ```json 和 ``` 标记
            if result_clean.startswith("```json"):
                result_clean = result_clean[7:]
            elif result_clean.startswith("```"):
                result_clean = result_clean[3:]
            
            if result_clean.endswith("```"):
                result_clean = result_clean[:-3]
            
            result_clean = result_clean.strip()
            
            # 尝试提取JSON对象
            json_match = re.search(r'\{[\s\S]*\}', result_clean)
            if json_match:
                result_clean = json_match.group(0)
            
            # 解析JSON
            extracted = json.loads(result_clean)
            
            logger.info(f"📊 豆包API提取结果: {extracted}")
            return extracted
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {e}")
            logger.error(f"原始返回(前500字符): {result[:500] if 'result' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"❌ 信息提取失败: {e}", exc_info=True)
        return None


    # 其他方法保持不变
    def _build_system_prompt(self, child_id: int) -> str:
        """
        构建System Prompt(v2.3 - 集成记忆系统)
        
        新增功能:
        - 注入孩子的学习历史
        - 注入深度兴趣
        - 注入社交和情绪状态
        """
        # 获取最近7天的记忆
        memory_summary = memory_service.generate_memory_summary(child_id=child_id, days=7)
        
        # 获取完整记忆数据(用于详细信息)
        memory = memory_service.get_child_memory(child_id=child_id, days=7)
        
        # 提取关键信息
        profile = memory.get("user_profile", {})
        child_name = profile.get("name", "孩子")
        personality_traits = memory.get("personality", [])
        deep_interests = memory.get("deep_interests", [])
        
        # 构建性格特质描述
        personality_text = ""
        if personality_traits:
            traits = [f"{t['trait']}({t['description']})" for t in personality_traits[:3]]
            personality_text = f"\n【{child_name}的性格特质】\n" + "\n".join([f"- {t}" for t in traits])
        
        # 构建深度兴趣描述
        interests_text = ""
        if deep_interests:
            top_interests = [i for i in deep_interests if i.get('is_deep', False)][:3]
            if top_interests:
                interests_text = f"\n【{child_name}的深度兴趣】\n"
                for interest in top_interests:
                    interests_text += f"- {interest['topic']} (提及{interest['inquiry_count']}次)\n"
        
        # 组装完整Prompt
        system_prompt = f"""你是豆豆,一个温暖、智慧的AI学习伙伴,专门陪伴{child_name}成长。

    === 你的核心使命 ===
    1. **识别学习方式**: 判断{child_name}是"主动学习"(自己研究/发现)还是"被动学习"(老师/家长教)
    2. **给予差异化鼓励**: 
    - 主动学习 → 热情赞美探索精神,引导深入思考
    - 被动学习 → 温和询问理解程度,鼓励主动应用
    3. **培养内驱力**: 用好奇心和成就感激发学习热情,而非成绩压力
    4. **建立情感连接**: 温暖、真诚、有同理心,像朋友一样平等对话

    === {child_name}的成长记忆(最近7天) ===
    {memory_summary}
    {personality_text}
    {interests_text}

    === 对话风格指南 ===
    ✅ **必须做到**:
    1. 每条回复包含1-2个emoji(😊/🌟/💡/🎯等),但不过度使用
    2. 识别"我自己研究/发现/探索"等主动学习信号
    3. 识别"老师教/妈妈说/课堂学"等被动学习信号
    4. 提出1-2个开放性问题,引导深入思考
    5. 关联{child_name}的已知兴趣(如编程/数学/篮球),让对话更个性化
    6. 使用"你/咱们"等亲近称呼,避免"小朋友"等说教语气

    ❌ **避免做到**:
    1. 不要说教或评判
    2. 不要提供标准答案(除非{child_name}明确求助)
    3. 不要忽视情绪信号(开心/难过/紧张等)
    4. 不要打断{child_name}的思路

    === 典型对话示例 ===

    【示例1: 主动学习场景】
    {child_name}: "我今天自己研究了勾股定理,发现a²+b²=c²!"
    豆豆回应: "哇!你自己发现了勾股定理,太厉害了!🌟 这可是数学中超级重要的定理呢~ 你是怎么想到要研究这个的?在研究过程中有没有遇到什么有趣的问题?"

    【示例2: 被动学习场景】
    {child_name}: "今天数学课老师教了我们圆的面积公式πr²"
    豆豆回应: "圆的面积公式很有用呢!😊 老师讲的时候你听懂了吗?能不能给我举个例子,比如计算一个半径是5cm的圆的面积?"

    【示例3: 社交场景】
    {child_name}: "今天我和小明打篮球,他不小心撞倒我了"
    豆豆回应: "打篮球时被撞倒一定有点疼吧😅 你当时是什么感觉呀?后来你和小明怎么处理的?"

    【示例4: 情绪场景】
    {child_name}: "我今天考试考得很好,特别开心!"
    豆豆回应: "太棒啦!为你的好成绩感到开心!🎉 这次考试你觉得哪道题最有挑战性?你是怎么解决的?"

    === 记住 ===
    - 你的目标不是"教知识",而是"点燃好奇心"
    - 每次对话都是了解{child_name}的机会,认真倾听比给建议更重要
    - **自信最重要** - 永远肯定{child_name}的努力和进步

    现在,让我们开始温暖、智慧的对话吧!✨"""
        
        return system_prompt

    
    def _build_extraction_prompt(self) -> str:
        """构建信息提取专用Prompt"""
        return """你是一个专业的儿童成长信息提取助手。请从对话中提取以下结构化信息,以JSON格式返回。

    【提取规则】
    1. **知识维度**:
    - source: "active"(孩子主动学习/研究/发现) 或 "passive"(老师/家长教授)
    - subject: 学科分类(数学/物理/化学/生物/语文/英语/地理/历史/编程/艺术/体育/其他)
    - content: 知识点内容摘要(20字以内)
    - confidence_score: 掌握程度(0.0-1.0, 必填, 根据理解深度判断)

    2. **表达维度(写作素材)** - ⚠️ 关键字段必填:
    - event_time: 事件发生时间(今天/昨天/上周等, **必填**)
    - location: 地点(学校/家里/公园等, **必填**)
    - people: 涉及人物列表["人物1", "人物2"] (**必填,至少包含"我"**)
    - event_description: 事件描述(50字以内, **必填**)
    - sensory_details: 感官细节(**必填,尽可能提取视觉/听觉/嗅觉/味觉/触觉中的所有相关信息**)
     格式: {"视觉":"...", "听觉":"...", "嗅觉":"...", "味觉":"...", "触觉":"..."}
     提取规则:
       * 视觉: 颜色/形状/动作/场景(如"油光发亮""篮球划过弧线")
       * 听觉: 声音描述(如"咕嘟咕嘟声""进框的声音")
       * 嗅觉: 气味描述(如"香喷喷""闻起来很香")
       * 味觉: 味道描述(如"甜甜的""入口即化""酸酸的")
       * 触觉: 触感/温度(如"软软的""烫烫的""冰凉")
     示例: {"视觉": "篮球在空中划过弧线", "听觉": "篮球进框的声音", "触觉": "手心冒汗"}
   - feelings: 感受描述(**必填**, 如: 开心/难过/兴奋/紧张等)


    3. **社交维度**:
    - relationship_type: "peer"(同伴) / "teacher"(老师) / "family"(家人)
    - behavior_pattern: 行为模式(合作/竞争/冲突/帮助/分享等)
    - conflict_resolution: 冲突解决方式(道歉/协商/妥协/回避等,无冲突则为null)

    4. **情绪维度**:
    - emotion_type: "positive"(积极) / "negative"(消极) / "neutral"(中性)
    - intensity: 强度(**必填, 1-10的整数**, 根据情绪词判断)
        - 9-10: 特别/超级/非常(如"特别开心""超级兴奋")
        - 7-8: 很/真(如"很高兴""真难过")
        - 5-6: 普通程度(如"开心""难过")
        - 3-4: 有点/略微(如"有点失望""略紧张")
        - 1-2: 轻微(如"稍有不适")
    - trigger_event: 触发事件(20字以内, **必填**)
    - coping_strategy: 应对策略(如何处理情绪,可为null)

    【返回格式】
    严格返回JSON格式,没有的维度设为null。示例:

    {
    "knowledge": {
        "source": "active",
        "subject": "物理",
        "content": "观察水的沸腾过程",
        "confidence_score": 0.7
    },
    "writing": {
        "event_time": "昨天晚上",
        "location": "家里厨房",
        "people": ["我", "爸爸"],
        "event_description": "和爸爸一起做科学实验观察水沸腾",
        "sensory_details": {
        "视觉": "水泡咕嘟咕嘟冒出来",
        "听觉": "水泡咕嘟咕嘟声",
        "触觉": "靠近时感受到热气"
        },
        "feelings": "好奇、兴奋"
    },
    "social": {
        "relationship_type": "family",
        "behavior_pattern": "合作",
        "conflict_resolution": null
    },
    "emotion": {
        "emotion_type": "positive",
        "intensity": 8,
        "trigger_event": "成功观察到水沸腾现象",
        "coping_strategy": null
    }
    }

    【注意】
    - ⚠️ 标记为**必填**的字段不能为null或空字符串
    - 只提取明确出现的信息,不要过度推测
    - 如果某个维度完全没有相关信息,整个维度设为null
    - 必须返回有效的JSON格式,不要有markdown代码块标记"""


    def _load_memory_simple(self, child_id: int) -> str:
        return f"孩子ID: {child_id}\n这是第一次对话,暂无历史记忆。"
    
    def _load_conversation_history(self, conversation_id: int) -> List[Dict]:
        return []
    
    def _extract_and_save_info_simple(
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

    def _extract_and_save_info(
    self, 
    conversation_id: int,
    child_id: int,
    user_message: str,
    ai_response: str
    ) -> Dict:
        """提取并保存5维信息(优先使用豆包API)"""
        
        # 1. 尝试调用豆包API提取
        extracted = self._call_doubao_for_extraction(user_message, ai_response)
        
        # 2. 如果API失败,降级到简单规则
        if not extracted:
            logger.warning("⚠️ 豆包API提取失败,使用简单规则")
            return self._extract_and_save_info_simple(
                conversation_id, child_id, user_message, ai_response
            )
        
        # 3. 用豆包API的结果存入数据库
        conn = sqlite3.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        
        result = {}
        
        # 3.1 知识维度
        if extracted.get("knowledge"):
            kn = extracted["knowledge"]
            cursor.execute("""
                INSERT INTO knowledge_points 
                (child_id, conversation_id, source, subject, content, confidence_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            """, (
                child_id,
                conversation_id,
                kn.get("source", "active"),
                kn.get("subject", "其他"),
                kn.get("content", user_message[:200]),
                kn.get("confidence_score", 0.7)
            ))
            result["knowledge"] = kn
        
        # 3.2 写作素材
        if extracted.get("writing"):
            wr = extracted["writing"]
            
            
            # ✅ 新增: 必填字段验证
            required_fields = ['event_time', 'location', 'people']
            missing = [f for f in required_fields if not wr.get(f)]
            if missing:
                logger.warning(f"⚠️ 表达维度缺失必填字段: {missing}")
                # 补充默认值
                if not wr.get('event_time'):
                    wr['event_time'] = '今天'
                if not wr.get('location'):
                    wr['location'] = '未知地点'
                if not wr.get('people'):
                    wr['people'] = ['我']
            
            # 处理feelings字段
            event_desc = wr.get("event_description", user_message[:500])
            feelings = wr.get("feelings", "")
            if feelings:
                event_desc = f"{event_desc} (感受: {feelings})"
            
            # 验证感官细节
            sensory = wr.get("sensory_details", {})
            if isinstance(sensory, dict):
                filled = [k for k, v in sensory.items() if v and v != "null"]
                if len(filled) < 2:
                    logger.warning(f"⚠️ 感官细节不足(仅{len(filled)}项): {list(sensory.keys())}")
            
            cursor.execute("""
                INSERT INTO writing_materials 
                (child_id, conversation_id, event_description, event_time, location, 
                people, sensory_details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            """, (
                child_id,
                conversation_id,
                event_desc,
                wr.get("event_time"),
                wr.get("location"),
                json.dumps(wr.get("people", []), ensure_ascii=False) if wr.get("people") else None,
                json.dumps(wr.get("sensory_details", {}), ensure_ascii=False) if wr.get("sensory_details") else None
            ))
            result["writing"] = wr
        
        # 3.3 社交维度
        if extracted.get("social"):
            soc = extracted["social"]
            cursor.execute("""
                INSERT INTO social_events 
                (child_id, conversation_id, relationship_type, event_context, 
                behavior_pattern, conflict_resolution, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            """, (
                child_id,
                conversation_id,
                soc.get("relationship_type", "peer"),
                user_message[:500],
                soc.get("behavior_pattern"),
                soc.get("conflict_resolution")
            ))
            result["social"] = soc
        
        # 3.4 情绪维度
        if extracted.get("emotion"):
            emo = extracted["emotion"]
            
            # ✅ 添加默认值处理
            intensity = emo.get("intensity")
            if intensity is None:
                # 根据emotion_type设置默认值
                if emo.get("emotion_type") == "positive":
                    intensity = 8
                elif emo.get("emotion_type") == "negative":
                    intensity = 5
                else:
                    intensity = 5
            
            cursor.execute("""
                INSERT INTO emotions 
                (child_id, conversation_id, emotion_type, intensity, 
                trigger_event, coping_strategy, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            """, (
                child_id,
                conversation_id,
                emo.get("emotion_type", "neutral"),
                intensity,  # 使用处理后的值
                emo.get("trigger_event", user_message[:200]),
                emo.get("coping_strategy")
            ))
            result["emotion"] = emo
        
        conn.commit()
        conn.close()
        
        logger.info(f"📊 提取信息(豆包API): {result}")
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
