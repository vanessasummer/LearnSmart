# 智学伙伴AI系统 (LearnSmart)

一个基于AI的儿童学习记录和智能推荐系统。

## 项目结构

```
LearnSmart/
├── .git/
├── .gitignore
├── README.md                    # 项目总览
├── LS_env/                     # 虚拟环境（在根目录）
│
├── backend/                     # 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/                 # API路由
│   │   ├── core/                # 核心功能
│   │   │   ├── ai_engine.py    # AI对话引擎
│   │   │   ├── memory_manager.py
│   │   │   └── ...
│   │   ├── models/              # 数据模型
│   │   ├── schemas/             # Pydantic模式
│   │   └── utils/              # 工具函数
│   ├── data/
│   │   └── learning_ai.db      # SQLite数据库
│   ├── logs/                    # 日志文件
│   ├── tests/                   # 测试文件
│   ├── requirements.txt         # Python依赖
│   ├── .env                     # 环境变量配置
│   └── README.md                # 后端文档
│
└── frontend/                    # 前端（未来创建）
    ├── lib/
    ├── assets/
    ├── pubspec.yaml
    └── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- 虚拟环境已配置（LS_env）

### 安装步骤

1. **激活虚拟环境**
   ```bash
   source LS_env/bin/activate
   ```

2. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   # 编辑 backend/.env 文件，填入你的API密钥等信息
   ```

4. **启动服务**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **访问API文档**
   - Swagger UI: http://localhost:8000/docs
   - 健康检查: http://localhost:8000/health

## 技术栈

### 后端
- **FastAPI** - 现代、快速的Web框架
- **SQLAlchemy** - ORM数据库工具
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI服务器

### 前端（计划中）
- **Flutter** - 跨平台移动应用框架

## 开发指南

### 代码提交

```bash
git add .
git commit -m "描述你的改动"
git push
```

### 运行测试

```bash
cd backend
pytest
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

