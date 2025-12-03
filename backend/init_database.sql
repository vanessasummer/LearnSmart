-- ===========================================
-- 🎯 儿童学习成长档案数据库 - 最终修复版
-- 核心修复: 将保留字values表重命名为value_insights
-- SQLite兼容版 | 支持5维成长画像
-- ===========================================

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- --------------------------------------------
-- 1. 儿童基础信息表(核心主体)
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              -- 儿童姓名
    birth_date TEXT NOT NULL,        -- 出生日期(ISO格式)
    gender TEXT,                     -- 性别
    grade_level TEXT,                -- 年级
    parent_relation TEXT,            -- 与家长关系
    health_notes TEXT,               -- 健康备注
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- --------------------------------------------
-- 2. 对话会话表(记录每次对话的元信息)
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,           -- 关联儿童
    conversation_mode TEXT NOT NULL,     -- 对话模式: knowledge/life
    start_time TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    end_time TEXT,
    topic TEXT,                          -- 主题标签
    is_active INTEGER NOT NULL DEFAULT 1,  -- 是否活跃(0/1)
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- 3. 对话消息表(记录完整对话内容)
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,    -- 关联对话
    role TEXT NOT NULL,                  -- user/assistant/system
    content TEXT NOT NULL,               -- 消息内容
    audio_url TEXT,                      -- 语音文件URL(可选)
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- 4. 知识维度: 知识点表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    conversation_id INTEGER,             -- 关联对话
    source TEXT NOT NULL,                -- active/passive
    subject TEXT NOT NULL,               -- 学科领域
    content TEXT NOT NULL,               -- 知识内容
    confidence_score REAL,               -- 掌握程度(0-1)
    keywords TEXT,                       -- 关键词(JSON数组)
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- --------------------------------------------
-- 5. 表达维度: 写作素材表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS writing_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    conversation_id INTEGER,
    event_description TEXT NOT NULL,     -- 事件描述
    event_time TEXT,                     -- 事件发生时间
    location TEXT,                       -- 地点
    people TEXT,                         -- 涉及人物(JSON数组)
    sensory_details TEXT,                -- 感官细节(JSON对象)
    suitable_genres TEXT,                -- 适用文体(JSON数组)
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- --------------------------------------------
-- 6. Memory系统表(跨对话信息提取)
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS user_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    info_type TEXT NOT NULL,             -- 信息类型: parent/child/preference等
    content TEXT NOT NULL,               -- 记忆内容
    source_conversations TEXT,           -- 来源对话ID列表(JSON数组)
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- 7. 社交维度: 社交事件表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS social_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    conversation_id INTEGER,
    relationship_type TEXT NOT NULL,     -- 关系类型: peer/teacher/family
    event_context TEXT NOT NULL,         -- 事件场景
    behavior_pattern TEXT,               -- 行为模式
    conflict_resolution TEXT,            -- 冲突解决方式
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- --------------------------------------------
-- 8. 情绪维度: 情绪记录表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    conversation_id INTEGER,
    emotion_type TEXT NOT NULL,          -- 情绪类型: positive/negative/neutral
    intensity INTEGER,                   -- 强度(1-10)
    trigger_event TEXT,                  -- 触发事件
    coping_strategy TEXT,                -- 应对策略
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- --------------------------------------------
-- 9. 个性维度: 性格特质表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS personality_traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    trait_category TEXT NOT NULL,       -- 特质类别
    trait_description TEXT NOT NULL,    -- 特质描述
    evidence_examples TEXT,             -- 证据示例(JSON数组)
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- 10. 价值观洞察表(重命名后的表)
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS value_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    value_dimension TEXT NOT NULL,      -- 价值观维度
    decision_context TEXT NOT NULL,     -- 决策场景
    choice_pattern TEXT,                -- 选择模式
    priority_analysis TEXT,             -- 优先级分析
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- 11. 兴趣深度追踪表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS interest_intensity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    topic TEXT NOT NULL,                -- 兴趣话题
    inquiry_count INTEGER DEFAULT 1,    -- 追问次数
    last_mentioned_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    is_deep_interest INTEGER DEFAULT 0,   -- 是否深度兴趣(0/1)
    related_conversations TEXT,         -- 相关对话ID(JSON数组)
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- 12. 系统配置表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ===========================================
-- 📊 视图定义(综合成长画像)
-- ===========================================
CREATE VIEW IF NOT EXISTS user_growth_profile AS
SELECT 
    c.id as child_id,
    c.name,
    -- 知识维度统计
    COUNT(DISTINCT kp.id) as total_knowledge_points,
    SUM(CASE WHEN kp.source = 'active' THEN 1 ELSE 0 END) as active_learning_count,
    SUM(CASE WHEN kp.source = 'passive' THEN 1 ELSE 0 END) as passive_learning_count,
    -- 社交维度统计
    COUNT(DISTINCT se.id) as social_events_count,
    -- 情绪维度统计
    COUNT(DISTINCT em.id) as emotion_records_count,
    AVG(em.intensity) as avg_emotion_intensity
FROM children c
LEFT JOIN knowledge_points kp ON c.id = kp.child_id
LEFT JOIN social_events se ON c.id = se.child_id
LEFT JOIN emotions em ON c.id = em.child_id
GROUP BY c.id;

-- ===========================================
-- 🔧 触发器(自动更新时间戳)
-- ===========================================
CREATE TRIGGER IF NOT EXISTS update_children_timestamp
AFTER UPDATE ON children
BEGIN
    UPDATE children SET updated_at = datetime('now', 'localtime')
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_memory_timestamp
AFTER UPDATE ON user_memory
BEGIN
    UPDATE user_memory SET updated_at = datetime('now', 'localtime')
    WHERE id = NEW.id;
END;

-- ===========================================
-- 📇 索引创建(优化查询性能)
-- ===========================================
CREATE INDEX IF NOT EXISTS idx_conversations_child_id ON conversations(child_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_child_id ON knowledge_points(child_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_points(source);
CREATE INDEX IF NOT EXISTS idx_writing_child_id ON writing_materials(child_id);
CREATE INDEX IF NOT EXISTS idx_memory_child_id ON user_memory(child_id);
CREATE INDEX IF NOT EXISTS idx_social_child_id ON social_events(child_id);
CREATE INDEX IF NOT EXISTS idx_emotions_child_id ON emotions(child_id);
CREATE INDEX IF NOT EXISTS idx_personality_child_id ON personality_traits(child_id);
CREATE INDEX IF NOT EXISTS idx_values_child_id ON value_insights(child_id);
CREATE INDEX IF NOT EXISTS idx_interest_child_id ON interest_intensity(child_id);

-- ===========================================
-- 🌟 初始数据(示例芋圆档案)
-- ===========================================
INSERT OR IGNORE INTO children (id, name, birth_date, gender, grade_level, parent_relation, health_notes)
VALUES (1, '芋圆', '2016-07-01', '男', '四年级', '母子关系', '先天性甲减,规律服药');

INSERT OR IGNORE INTO user_memory (child_id, info_type, content, source_conversations)
VALUES 
(1, 'parent_info', '妈妈:中科院儿童心理学硕士,全职陪伴,重视科学育儿', '[]'),
(1, 'child_strengths', '数学思维强,编程Scratch/Python,绝对音感,英语演讲全国一等奖', '[]'),
(1, 'health_concern', '身高125cm偏矮,希望追高;清嗓抖动疑似抽动症', '[]');

INSERT OR IGNORE INTO personality_traits (child_id, trait_category, trait_description, evidence_examples)
VALUES 
(1, '核心特质', '自信突出,敢于公众发言', '["中文演讲校一等奖","英文演讲全国一等奖"]'),
(1, '学习风格', '好奇心强,主动探索,重要场合超常发挥', '["韦氏智力140分","挫折承受力强"]');

INSERT OR IGNORE INTO system_config (key, value, description)
VALUES 
('prompt_version', 'v2.2', '当前Prompt版本'),
('extraction_mode', 'auto', '信息提取模式:auto/manual'),
('deep_interest_threshold', '3', '深度兴趣判定阈值(追问次数)');

-- ===========================================
-- ✅ 数据库初始化完成！
-- ===========================================
