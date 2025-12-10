-- 插入芋圆的基础信息(如果children表还没有数据)
INSERT OR IGNORE INTO children (id, child_name, birth_date, grade, parent_id, health_status, created_at)
VALUES (1, '芋圆', '2016-07-15', '四年级', 1, '先天甲减,规律服药', datetime('now', 'localtime'));

-- 插入用户画像信息
INSERT OR IGNORE INTO user_memory (child_id, info_type, content, created_at)
VALUES 
(1, 'basic_info', '9岁男孩,北京师范大学亚太实验学校四年级', datetime('now', 'localtime')),
(1, 'strengths', '数学思维强,英语KET水平,编程3年经验,绝对音感', datetime('now', 'localtime')),
(1, 'interests', '编程(想做数学游戏),篮球(想进校队),钢琴编曲,书法', datetime('now', 'localtime')),
(1, 'personality', '自信突出,好奇心强,善良包容,表达能力强', datetime('now', 'localtime'));

-- 插入性格特质数据
INSERT OR IGNORE INTO personality_traits (child_id, trait_category, trait_description, confidence_level, created_at)
VALUES 
(1, '自信', '公众场合敢于表达,不怕失败', 0.95, datetime('now', 'localtime')),
(1, '好奇', '经常提问生活现象原理,探索欲旺盛', 0.90, datetime('now', 'localtime')),
(1, '善良', '乐于助人,共情能力强', 0.85, datetime('now', 'localtime')),
(1, '专注', '对感兴趣内容专注度好', 0.75, datetime('now', 'localtime'));

-- 插入深度兴趣数据
INSERT OR IGNORE INTO interest_intensity (child_id, interest_name, intensity_score, last_mentioned, created_at)
VALUES 
(1, '编程(Python/C++)', 0.95, datetime('now', 'localtime'), datetime('now', 'localtime')),
(1, '数学', 0.90, datetime('now', 'localtime'), datetime('now', 'localtime')),
(1, '篮球', 0.85, datetime('now', 'localtime'), datetime('now', 'localtime')),
(1, '钢琴编曲', 0.80, datetime('now', 'localtime'), datetime('now', 'localtime')),
(1, '英语', 0.75, datetime('now', 'localtime'), datetime('now', 'localtime'));

-- 验证插入
SELECT '=== Children 表 ===' as 表名;
SELECT * FROM children WHERE id = 1;

SELECT '' as 空行;
SELECT '=== User Memory 表 ===' as 表名;
SELECT * FROM user_memory WHERE child_id = 1;

SELECT '' as 空行;
SELECT '=== Personality Traits 表 ===' as 表名;
SELECT * FROM personality_traits WHERE child_id = 1;

SELECT '' as 空行;
SELECT '=== Interest Intensity 表 ===' as 表名;
SELECT * FROM interest_intensity WHERE child_id = 1;
