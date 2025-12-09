import sys
sys.path.insert(0, '/Users/liufeng/tt_workspace/LearnSmart/backend')

from app.core.ai_engine import AIEngine

# 创建AI引擎实例
ai_engine = AIEngine()

# 生成System Prompt
print("=== 测试Prompt v2.3 (集成记忆系统) ===\n")
system_prompt = ai_engine._build_system_prompt(child_id=1)

print(system_prompt)
print("\n" + "="*60)
print("✅ Prompt生成成功!")
print(f"Prompt长度: {len(system_prompt)} 字符")
