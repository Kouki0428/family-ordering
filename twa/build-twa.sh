#!/bin/bash
# TWA 构建脚本 - 使用 bubblewrap 或 @bubblewrap/cli
# 使用前需要安装: npm install -g @bubblewrap/cli

set -e

# 配置
APP_NAME="家庭点餐"
WEB_URL="http://YOUR_NAS_IP:8080"  # 替换为你的飞牛 NAS 地址
OUTPUT_DIR="./output"
ICON_DIR="./icons"

# 检查前置条件
if ! command -v bw &> /dev/null; then
    echo "请先安装 bubblewrap: npm install -g @bubblewrap/cli"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 进入 bubblewrap 项目目录
cd "$OUTPUT_DIR"

# 如果已存在，清理
if [ -f "project.config" ]; then
    echo "删除旧项目..."
    bw clean
fi

# 初始化项目
echo "初始化 TWA 项目..."
bw init --manifest="$WEB_URL/manifest.json" --app-name="$APP_NAME"

# 配置 Web 服务器 URL
echo "配置 Web URL..."
bw set-web-server-url "$WEB_URL"

# 生成图标（可选）
echo "生成图标..."
bw generate-icons --source-dir="$ICON_DIR"

# 构建 APK
echo "构建 APK..."
bw build --mode=debug

echo ""
echo "=========================================="
echo "TWA 构建完成！"
echo "APK 文件位于: $OUTPUT_DIR/app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "使用方法:"
echo "1. 修改 WEB_URL 为你的飞牛 NAS 地址"
echo "2. 准备图标文件: $ICON_DIR"
echo "3. 运行: bash build-twa.sh"
echo "=========================================="
