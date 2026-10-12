#!/bin/bash
# ============================================================
# 家庭点餐系统 - 飞牛 NAS 一键部署脚本
# ============================================================

set -e

echo "🏠 家庭点餐系统部署脚本"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
check_docker() {
    echo "🔍 检查 Docker..."
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker 未安装${NC}"
        echo "请先在飞牛 NAS 上安装 Docker 应用"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}错误: Docker Compose 未安装${NC}"
        echo "请先安装 Docker Compose"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker 已就绪${NC}"
}

# 创建数据目录
create_data_dir() {
    echo "📁 创建数据目录..."
    mkdir -p data
    echo -e "${GREEN}✓ 数据目录已创建${NC}"
}

# 构建并启动服务
build_services() {
    echo "🔨 构建 Docker 镜像..."
    docker-compose build --no-cache
    
    echo "🚀 启动服务..."
    docker-compose up -d
    
    echo -e "${GREEN}✓ 服务已启动${NC}"
}

# 检查服务状态
check_status() {
    echo "🔍 检查服务状态..."
    docker-compose ps
    
    echo ""
    echo "================================"
    echo "📋 访问地址"
    echo "================================"
    echo ""
    echo "🔐 登录页:     http://NAS_IP:8080/login"
    echo "📊 管理后台:   http://NAS_IP:8080/admin"
    echo "🍳 后厨大屏:   http://NAS_IP:8080/kitchen"
    echo "📚 API 文档:   http://NAS_IP:8000/docs"
    echo ""
    echo "================================"
    echo "📝 首次使用步骤"
    echo "================================"
    echo ""
    echo "1. 打开登录页，切换到"注册"标签"
    echo "2. 注册管理员账号（勾选"设为管理员"）"
    echo "3. 登录进入管理后台"
    echo "4. 添加菜单（选择餐段：早餐/午餐/晚餐/夜宵）"
    echo "5. 开始点餐！"
    echo ""
    echo -e "${GREEN}✅ 部署完成！${NC}"
}

# 主流程
main() {
    cd "$(dirname "$0")"
    
    check_docker
    create_data_dir
    build_services
    check_status
}

main "$@"
