-- 插入深度兴趣数据(移除created_at字段)
INSERT INTO interest_intensity (child_id, topic, inquiry_count, last_mentioned_at, is_deep_interest, related_conversations)
VALUES 
(1, '编程(Python/C++/Scratch)', 15, datetime('now', 'localtime'), 1, '["想做数学游戏","学习CSP-J"]'),
(1, '数学(奥数/逻辑推理)', 12, datetime('now', 'localtime'), 1, '["自己研究勾股定理","喜欢数学思维题"]'),
(1, '篮球', 10, datetime('now', 'localtime'), 1, '["想进校队","U9业余赛水平"]'),
(1, '钢琴编曲', 8, datetime('now', 'localtime'), 1, '["自弹自唱","组建校乐队"]'),
(1, '英语(演讲/阅读)', 7, datetime('now', 'localtime'), 1, '["KET词汇/PET背诵","RAZ J级"]'),
(1, '科学实验', 5, datetime('now', 'localtime'), 0, '["和爸爸做水沸腾实验"]');

-- 验证插入
SELECT '=== Interest Intensity 表(新增) ===' as 标题;
SELECT id, topic, inquiry_count, is_deep_interest, last_mentioned_at FROM interest_intensity WHERE child_id = 1;
