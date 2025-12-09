-- 更新芋圆的基础信息(children表已有数据,更新即可)
UPDATE children 
SET name = '芋圆',
    birth_date = '2016-07-15',
    grade_level = '四年级',
    health_notes = '先天性甲减,规律服药,身高125cm'
WHERE id = 1;

-- 插入用户画像信息(如果不存在才插入)
INSERT OR IGNORE INTO user_memory (id, child_id, info_type, content, created_at, updated_at)
VALUES 
(8, 1, 'learning_style', '主动探索型,好奇心驱动,成就感激励', datetime('now', 'localtime'), datetime('now', 'localtime')),
(9, 1, 'goals', '短期:PET英语/数学宫殿项目; 中期:CSP-J编程竞赛; 梦想:成为科学家发明有用产品', datetime('now', 'localtime'), datetime('now', 'localtime')),
(10, 1, 'challenges', '写作速度慢,审题不细心,拖延习惯,课堂易溜号', datetime('now', 'localtime'), datetime('now', 'localtime'));

-- 插入性格特质数据(使用正确的字段名)
INSERT INTO personality_traits (child_id, trait_category, trait_description, evidence_examples, created_at, updated_at)
VALUES 
(1, '自信表达', '公众场合敢于表达,不怕失败,爱分享', '["中英文演讲获奖","主动举手发言"]', datetime('now', 'localtime'), datetime('now', 'localtime')),
(1, '好奇探索', '经常提问生活现象原理,主动研究新知识', '["自己研究勾股定理","探索物体惯性"]', datetime('now', 'localtime'), datetime('now', 'localtime')),
(1, '善良包容', '乐于助人,共情能力强,孝顺暖心', '["同学摔倒主动扶起","体谅父母辛苦"]', datetime('now', 'localtime'), datetime('now', 'localtime')),
(1, '坚韧毅力', '从失败中学习,挑战自我', '["跳绳从10到210次","仰卧起坐一个月达年级第一"]', datetime('now', 'localtime'), datetime('now', 'localtime'));

-- 插入深度兴趣数据(使用正确的字段名)
INSERT INTO interest_intensity (child_id, topic, inquiry_count, last_mentioned_at, is_deep_interest, related_conversations, created_at)
VALUES 
(1, '编程(Python/C++/Scratch)', 15, datetime('now', 'localtime'), 1, '["想做数学游戏","学习CSP-J"]', datetime('now', 'localtime')),
(1, '数学(奥数/逻辑推理)', 12, datetime('now', 'localtime'), 1, '["自己研究勾股定理","喜欢数学思维题"]', datetime('now', 'localtime')),
(1, '篮球', 10, datetime('now', 'localtime'), 1, '["想进校队","U9业余赛水平"]', datetime('now', 'localtime')),
(1, '钢琴编曲', 8, datetime('now', 'localtime'), 1, '["自弹自唱","组建校乐队"]', datetime('now', 'localtime')),
(1, '英语(演讲/阅读)', 7, datetime('now', 'localtime'), 1, '["KET词汇/PET背诵","RAZ J级"]', datetime('now', 'localtime')),
(1, '科学实验', 5, datetime('now', 'localtime'), 0, '["和爸爸做水沸腾实验"]', datetime('now', 'localtime'));

-- 验证插入
SELECT '=== Children 表(更新后) ===' as 标题;
SELECT id, name, birth_date, grade_level, health_notes FROM children WHERE id = 1;

SELECT '' as 空行;
SELECT '=== User Memory 表(新增) ===' as 标题;
SELECT id, info_type, substr(content, 1, 40) as content_preview FROM user_memory WHERE child_id = 1 AND id >= 8;

SELECT '' as 空行;
SELECT '=== Personality Traits 表(新增) ===' as 标题;
SELECT id, trait_category, trait_description FROM personality_traits WHERE child_id = 1 AND id > 2;

SELECT '' as 空行;
SELECT '=== Interest Intensity 表(新增) ===' as 标题;
SELECT id, topic, inquiry_count, is_deep_interest FROM interest_intensity WHERE child_id = 1;
EOF