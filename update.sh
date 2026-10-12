#!/bin/bash
# ============================================================
# 家庭点餐系统 - 一键更新脚本
# ============================================================

set -e

echo "🔄 家庭点餐系统更新脚本"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 备份数据
backup_data() {
    echo "📦 备份数据..."
    if [ -f "data/ordering.db" ]; then
        BACKUP_FILE="data/ordering-backup-$(date +%Y%m%d-%H%M%S).db"
        cp data/ordering.db "$BACKUP_FILE"
        echo -e "${GREEN}✓ 数据已备份到 $BACKUP_FILE${NC}"
    else
        echo -e "${YELLOW}⚠ 未找到数据文件，跳过备份${NC}"
    fi
}

# 拉取最新代码
pull_code() {
    echo "📥 拉取最新代码..."
    if [ -d ".git" ]; then
        git pull origin main
        echo -e "${GREEN}✓ 代码已更新${NC}"
    else
        echo -e "${YELLOW}⚠ 不是 Git 仓库，跳过拉取${NC}"
        echo "请手动上传最新代码后继续"
        read -p "按回车键继续..."
    fi
}

# 重新构建
rebuild() {
    echo "🔨 重新构建服务..."
    docker-compose down
    docker-compose up -d --build
    echo -e "${GREEN}✓ 服务已重启${NC}"
}

# 检查状态
check_status() {
    echo "🔍 检查服务状态..."
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}✅ 更新完成！${NC}"
}

# 主流程
main() {
    cd "$(dirname "$0")"
    
    backup_data
    pull_code
    rebuild
    check_status
}

main "$@"
