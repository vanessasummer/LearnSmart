import sys
sys.path.insert(0, '/Users/liufeng/tt_workspace/LearnSmart/backend')

from app.services.memory_service import memory_service

# 测试获取芋圆的记忆
print("=== 测试Memory服务 ===\n")

# 获取最近7天的记忆
memory = memory_service.get_child_memory(child_id=1, days=7)

print("📚 知识维度:")
print(f"  学习统计: {memory['knowledge']['learning_stats']}")
print(f"  主要学科: {memory['knowledge']['subjects']}")

print("\n📝 表达维度:")
print(f"  写作素材数: {len(memory['writing']['recent_materials'])}")
print(f"  常去地点: {memory['writing']['frequent_locations']}")

print("\n🤝 社交维度:")
print(f"  关系类型: {memory['social']['relationships']}")
print(f"  行为模式: {memory['social']['behaviors']}")

print("\n😊 情绪维度:")
print(f"  情绪统计: {memory['emotion']['emotion_stats']}")

print("\n=== 记忆摘要 ===")
summary = memory_service.generate_memory_summary(child_id=1, days=7)
print(summary)
