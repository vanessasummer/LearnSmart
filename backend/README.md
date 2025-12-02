# 后端服务文档

## 项目说明

智学伙伴AI系统的后端服务，基于 FastAPI 构建。

## API 端点

### 对话相关
- `POST /api/chat` - 发送对话消息
- `GET /api/chat/history` - 获取对话历史

### 记忆管理
- `GET /api/memory` - 获取记忆列表
- `POST /api/memory` - 创建新记忆
- `PUT /api/memory/{id}` - 更新记忆
- `DELETE /api/memory/{id}` - 删除记忆

### 素材管理
- `GET /api/materials` - 获取素材列表
- `POST /api/materials` - 上传新素材

### 分析功能
- `GET /api/analysis` - 获取学习分析报告

### 用户管理
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建新用户

## 环境变量配置

在 `.env` 文件中配置以下变量：

```env
# 豆包API配置
DOUBAO_API_KEY=your_api_key
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions
DOUBAO_MODEL=your_model_id

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/learning_ai.db

# 应用配置
APP_NAME=智学伙伴AI系统
DEBUG=True
LOG_LEVEL=INFO

# 安全配置
SECRET_KEY=your_secret_key
```

## 数据库

使用 SQLite 数据库，数据文件位于 `data/learning_ai.db`。

初始化数据库：
```bash
# 运行数据库初始化脚本（如果存在）
python -m app.database
```

## 开发

### 启动开发服务器

```bash
# 激活虚拟环境
source ../LS_env/bin/activate

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 运行测试

```bash
pytest
```

## 部署

生产环境建议使用：
- Gunicorn + Uvicorn workers
- 或 Docker 容器化部署
