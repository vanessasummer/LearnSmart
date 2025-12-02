# 儿童学习记录AI系统 - 后端

## 项目简介
基于FastAPI + SQLite的儿童学习对话记录与分析系统。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
sqlite3 data/learning_ai.db < 数据库初始化脚本.sql

# 3. 配置环境变量
# 编辑 .env 文件,填写豆包API密钥

# 4. 启动服务
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看API文档

## 项目结构

详见目录结构
