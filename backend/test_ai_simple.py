"""
AI对话引擎简单测试 - 便捷运行脚本
从backend目录直接运行: python test_ai_simple.py
"""
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入并运行测试
from tests.test_ai_simple import test_chat
import asyncio

if __name__ == "__main__":
    asyncio.run(test_chat())

