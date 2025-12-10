cat > database/README.md << 'EOF'
# 数据库管理文档

## 📁 目录结构

database/ ├── migrations/ # 数据库迁移脚本 │ └── 001_init_database.sql # 初始化脚本 ├── seeds/ # 测试数据 │ ├── insert_test_data_final.sql │ └── ... ├── archive/ # 归档旧文件 │ └── legacy_init_database.sql ├── db_manager.sh # 管理脚本 └── README.md # 本文档


## 🚀 快速开始

### 初始化数据库
```bash
./database/db_manager.sh init
插入测试数据
Copy./database/db_manager.sh seed
验证数据库
Copy./database/db_manager.sh verify
完整重建
Copy./database/db_manager.sh all
📊 数据库表结构
核心表
children - 儿童基础信息
conversations - 对话会话
messages - 对话消息
5维度表
knowledge_points - 知识维度
writing_materials - 表达维度
social_events - 社交维度
emotions - 情绪维度
personality_traits - 性格维度
辅助表
user_memory - 跨对话记忆
value_insights - 价值观洞察
interest_intensity - 兴趣深度
system_config - 系统配置
🔧 常见操作
备份数据库
Copycp data/learning_ai.db data/learning_ai.db.backup_$(date +%Y%m%d)
查看表结构
Copysqlite3 data/learning_ai.db ".schema children"
导出数据
Copysqlite3 data/learning_ai.db ".dump" > backup.sql
📝 注意事项
✅ 始终使用 001_init_database.sql 初始化
✅ 修改前先备份数据库
✅ 测试数据使用seeds目录
❌ 不要直接修改 migrations/ 中的文件