#!/bin/bash
# 运行测试脚本的便捷方式

cd "$(dirname "$0")"
source ../LS_env/bin/activate
python tests/test_ai_simple.py

