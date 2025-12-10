#!/bin/bash
# 数据库管理脚本

set -e

DB_PATH="data/learning_ai.db"
MIGRATIONS_DIR="database/migrations"
SEEDS_DIR="database/seeds"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "  数据库管理工具"
echo "========================================="

# 1. 初始化数据库
init_database() {
    echo -e "${YELLOW}[1/3] 初始化数据库结构...${NC}"
    
    # 备份旧数据库
    if [ -f "$DB_PATH" ]; then
        backup_file="${DB_PATH}.backup_$(date +%Y%m%d_%H%M%S)"
        echo "  备份现有数据库: $backup_file"
        cp "$DB_PATH" "$backup_file"
    fi
    
    # 执行初始化脚本
    sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/001_init_database.sql"
    
    echo -e "${GREEN}✅ 数据库结构创建完成${NC}"
}

# 2. 插入测试数据
seed_database() {
    echo -e "${YELLOW}[2/3] 插入测试数据...${NC}"
    
    # 按顺序执行seed文件
    for seed_file in "$SEEDS_DIR"/*.sql; do
        if [ -f "$seed_file" ]; then
            echo "  执行: $(basename $seed_file)"
            sqlite3 "$DB_PATH" < "$seed_file"
        fi
    done
    
    echo -e "${GREEN}✅ 测试数据插入完成${NC}"
}

# 3. 验证数据库
verify_database() {
    echo -e "${YELLOW}[3/3] 验证数据库...${NC}"
    
    # 检查表数量
    table_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
    echo "  表数量: $table_count"
    
    # 检查children表
    child_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM children;")
    echo "  儿童记录: $child_count"
    
    # 检查知识点
    kp_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM knowledge_points;")
    echo "  知识点: $kp_count"
    
    # 检查对话
    conv_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM conversations;")
    echo "  对话记录: $conv_count"
    
    echo -e "${GREEN}✅ 数据库验证完成${NC}"
}

# 主菜单
case "${1:-all}" in
    init)
        init_database
        ;;
    seed)
        seed_database
        ;;
    verify)
        verify_database
        ;;
    all)
        init_database
        seed_database
        verify_database
        ;;
    *)
        echo "用法: $0 {init|seed|verify|all}"
        echo "  init   - 初始化数据库结构"
        echo "  seed   - 插入测试数据"
        echo "  verify - 验证数据库"
        echo "  all    - 执行全部(默认)"
        exit 1
        ;;
esac

echo "========================================="
echo -e "${GREEN}✨ 完成！${NC}"
echo "========================================="