"""
AI对话引擎简单测试
"""
import asyncio
import sys
from pathlib import Path

# 添加backend目录到Python路径，以便导入app模块
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.ai_engine import ai_engine

async def test_chat():
    print("=== 测试AI对话引擎 ===\n")
    
    # 测试1: 简单对话
    result = await ai_engine.chat(
        child_id=1,
        message="今天我学了经纬度的知识，还打了乒乓球！",
        mode="knowledge"
    )
    
    print(f"对话ID: {result['conversation_id']}")
    print(f"模式: {result['mode']}")
    print(f"轮次: {result['turn_count']}")
    print(f"\nAI回复:\n{result['reply']}\n")
    print(f"提取信息: {result['extracted_info']}")

if __name__ == "__main__":
    asyncio.run(test_chat())
