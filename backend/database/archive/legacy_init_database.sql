-- 儿童学习记录AI系统 - 数据库初始化脚本
-- 数据库类型: SQLite
-- 创建日期: 2025-11-26（旧版本，已废弃）

-- ============================================
-- 1. 用户表 (users)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_name VARCHAR(50) NOT NULL,
    nickname VARCHAR(50),
    age INTEGER,
    grade VARCHAR(20),
    gender VARCHAR(10),
    school VARCHAR(100),
    interests TEXT,  -- JSON格式: ["篮球", "编程", "钢琴"]
    personality_summary TEXT,  -- 性格摘要
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 示例数据
INSERT INTO users (child_name, nickname, age, grade, gender, school, interests, personality_summary) 
VALUES (
    '芋圆',
    '芋圆',
    9,
    '四年级',
    '男',
    '北京师范大学亚太实验学校',
    '["篮球", "乒乓球", "编程", "钢琴", "数学"]',
    '自信、好奇心强、善良、行动力强、创造性思维'
);

-- ============================================
-- 2. 对话会话表 (conversations)
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    conversation_mode VARCHAR(20) DEFAULT '知识小记模式',  -- 知识小记模式, 自由交流模式
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_turns INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',  -- active, completed, interrupted
    knowledge_count INTEGER DEFAULT 0,  -- 已提取知识点数量
    target_knowledge_count INTEGER DEFAULT 3,  -- 目标知识点数量
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_conv_user_id ON conversations(user_id);
CREATE INDEX idx_conv_session_id ON conversations(session_id);

-- ============================================
-- 3. 对话轮次表 (conversation_turns)
-- ============================================
CREATE TABLE IF NOT EXISTS conversation_turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    turn_number INTEGER NOT NULL,
    speaker VARCHAR(10) NOT NULL,  -- child, ai
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    audio_url VARCHAR(500),  -- 语音文件URL(如有)
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_turn_conv_id ON conversation_turns(conversation_id);

-- ============================================
-- 4. 知识点表 (knowledge_points)
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    turn_id INTEGER,
    type VARCHAR(20) NOT NULL,  -- Type1-Type5
    subject VARCHAR(50),  -- 数学、语文、英语、科学等
    content TEXT NOT NULL,
    mastery_level VARCHAR(20),  -- 已掌握、部分理解、困惑、未知
    source VARCHAR(50),  -- 课堂、自学、课外、生活应用等
    learning_type VARCHAR(20),  -- 主动探索、被动接受
    confidence FLOAT DEFAULT 0.8,  -- 提取置信度 0-1
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (turn_id) REFERENCES conversation_turns(id)
);

CREATE INDEX idx_kp_user_id ON knowledge_points(user_id);
CREATE INDEX idx_kp_subject ON knowledge_points(subject);
CREATE INDEX idx_kp_type ON knowledge_points(type);

-- ============================================
-- 5. 作文素材表 (writing_materials)
-- ============================================
CREATE TABLE IF NOT EXISTS writing_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 人物描写、事件叙事、心理描写、场景描写、哲理感悟
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,  -- 素材主要内容
    scene_description TEXT,  -- 场景描述
    characters TEXT,  -- JSON格式: ["我", "同学XX"]
    emotion_tags TEXT,  -- JSON格式: ["兴奋", "自豪"]
    sensory_details TEXT,  -- JSON格式: 感官细节
    psychological_description TEXT,  -- 心理描写
    writing_angles TEXT,  -- JSON格式: 写作角度建议
    applicable_topics TEXT,  -- JSON格式: 适用作文题目
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_wm_user_id ON writing_materials(user_id);
CREATE INDEX idx_wm_type ON writing_materials(type);

-- ============================================
-- 6. Memory表 (user_memory)
-- ============================================
CREATE TABLE IF NOT EXISTS user_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    memory_type VARCHAR(20) NOT NULL,  -- long_term, short_term
    category VARCHAR(50) NOT NULL,  -- personality, interests, recent_topics, friends, learning_style
    key_name VARCHAR(100) NOT NULL,
    value TEXT NOT NULL,  -- JSON格式存储复杂数据
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,  -- 短期记忆的过期时间(7天后)
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_mem_user_id ON user_memory(user_id);
CREATE INDEX idx_mem_type ON user_memory(memory_type);
CREATE INDEX idx_mem_category ON user_memory(category);

-- ============================================
-- 7. 社交事件表 (social_events)
-- ============================================
CREATE TABLE IF NOT EXISTS social_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    friend_name VARCHAR(100),
    relationship VARCHAR(50),  -- 好朋友、玩伴、同学、竞争对手等
    event_description TEXT NOT NULL,
    interaction_quality VARCHAR(50),  -- 积极、中性、消极
    conflict_situation TEXT,  -- 冲突描述(如有)
    emotion VARCHAR(50),
    observed_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_se_user_id ON social_events(user_id);

-- ============================================
-- 8. 情绪数据表 (emotions)
-- ============================================
CREATE TABLE IF NOT EXISTS emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    primary_emotion VARCHAR(50) NOT NULL,  -- 开心、难过、着急、兴奋等
    intensity INTEGER CHECK(intensity >= 1 AND intensity <= 10),  -- 强度1-10
    trigger_event TEXT,  -- 触发事件
    coping_strategy TEXT,  -- 应对策略
    regulation_success BOOLEAN,  -- 是否成功调节
    observed_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_em_user_id ON emotions(user_id);
CREATE INDEX idx_em_date ON emotions(observed_date);

-- ============================================
-- 9. 性格特质表 (personality_traits)
-- ============================================
CREATE TABLE IF NOT EXISTS personality_traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    trait_name VARCHAR(100) NOT NULL,
    trait_category VARCHAR(50),  -- 认知能力、社交能力、情绪管理等
    evidence TEXT NOT NULL,  -- 支持证据
    confidence FLOAT CHECK(confidence >= 0 AND confidence <= 1),  -- 置信度0-1
    observed_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_pt_user_id ON personality_traits(user_id);
CREATE INDEX idx_pt_trait ON personality_traits(trait_name);

-- ============================================
-- 10. 价值观线索表 (value_insights)
-- ============================================
CREATE TABLE IF NOT EXISTS value_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    value_type VARCHAR(100) NOT NULL,
    core_belief TEXT,  -- 核心信念
    example TEXT NOT NULL,  -- 具体例子
    moral_reasoning TEXT,  -- 道德推理过程
    observed_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_vi_user_id ON value_insights(user_id);

-- ============================================
-- 11. 兴趣强度表 (interest_intensity) ⭐新增
-- ============================================
CREATE TABLE IF NOT EXISTS interest_intensity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic VARCHAR(100) NOT NULL,
    category VARCHAR(50),  -- 体育运动、艺术、科技、学科等
    interest_level VARCHAR(20) NOT NULL,  -- 核心兴趣、潜在兴趣、一般话题
    interest_score FLOAT CHECK(interest_score >= 0 AND interest_score <= 10),
    first_mentioned DATE NOT NULL,
    last_mentioned DATE NOT NULL,
    total_mentions INTEGER DEFAULT 1,
    total_turns INTEGER DEFAULT 0,  -- 累计讨论轮数
    evidence TEXT,  -- JSON格式: 兴趣证据
    knowledge_progression TEXT,  -- JSON格式: 知识进阶记录
    recommended_actions TEXT,  -- JSON格式: 推荐行动
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_ii_user_id ON interest_intensity(user_id);
CREATE INDEX idx_ii_level ON interest_intensity(interest_level);

-- ============================================
-- 12. 系统配置表 (system_config)
-- ============================================
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('default_conversation_mode', '知识小记模式', '默认对话模式'),
('target_knowledge_count', '3', '知识小记模式的目标知识点数量'),
('same_topic_max_turns', '8', '知识小记模式下同一话题最大轮数'),
('short_term_memory_days', '7', '短期记忆保留天数'),
('interest_detection_threshold', '5', '兴趣检测触发阈值(单次对话轮数)');

-- ============================================
-- 视图: 用户成长画像汇总
-- ============================================
CREATE VIEW IF NOT EXISTS user_growth_profile AS
SELECT 
    u.id AS user_id,
    u.child_name,
    u.nickname,
    u.age,
    u.grade,
    COUNT(DISTINCT c.id) AS total_conversations,
    COUNT(DISTINCT kp.id) AS total_knowledge_points,
    COUNT(DISTINCT wm.id) AS total_writing_materials,
    COUNT(DISTINCT pt.id) AS total_personality_traits,
    COUNT(DISTINCT vi.id) AS total_value_insights,
    COUNT(DISTINCT ii.id) FILTER (WHERE ii.interest_level = '核心兴趣') AS core_interests_count
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN knowledge_points kp ON u.id = kp.user_id
LEFT JOIN writing_materials wm ON u.id = wm.user_id
LEFT JOIN personality_traits pt ON u.id = pt.user_id
LEFT JOIN value_insights vi ON u.id = vi.user_id
LEFT JOIN interest_intensity ii ON u.id = ii.user_id
GROUP BY u.id;

-- ============================================
-- 触发器: 自动更新 updated_at 时间戳
-- ============================================
CREATE TRIGGER update_users_timestamp 
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================
-- 完成提示
-- ============================================
SELECT '数据库初始化完成! 表结构创建成功.' AS message;