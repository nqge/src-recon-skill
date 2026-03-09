#!/bin/bash
# 快速深度分析脚本（从 URL 直接开始）
# 使用方法: ./scripts/quick_deep_analysis.sh <url>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGET="$1"
OUTPUT_DIR="${PROJECT_ROOT}/output/recon/quick_analysis/$(echo $1 | tr -d '/:')"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$TARGET" ]; then
    echo -e "${RED}[-] 请输入目标 URL${NC}"
    echo "使用方法: $0 <url>"
    exit 1
fi

echo -e "${GREEN}[+] 快速深度分析${NC}"
echo -e "${GREEN}[+] 目标 URL: $TARGET${NC}"

mkdir -p "$OUTPUT_DIR"

echo -e "\n${BLUE}[*] 提取基础信息...${NC}"

if echo "$TARGET" | grep -qE '^https?://'; then
    DOMAIN=$(echo "$TARGET" | sed -e 's|^[^/]*//||' -e 's|/.*$||' | head -1)
    echo "[*] 域名: $DOMAIN"
else
    DOMAIN="$TARGET"
fi

> "${OUTPUT_DIR}/urls.txt"
echo "$TARGET" >> "${OUTPUT_DIR}/urls.txt"

if echo "$TARGET" | grep -q '^https://'; then
    HTTP_URL=$(echo "$TARGET" | sed 's|https://|http://|')
    echo "$HTTP_URL" >> "${OUTPUT_DIR}/urls.txt"
    echo "[*] 添加 HTTP 版本: $HTTP_URL"
fi

echo -e "${GREEN}[+] URL 已准备就绪${NC}"

echo -e "\n${BLUE}[*] JS 文件分析...${NC}"

cd "$PROJECT_ROOT"
python3 core/jsfind.py "$TARGET" 2>/dev/null || true

echo -e "${GREEN}[+] 分析完成！${NC}"
echo -e "${YELLOW}[+] 结果: ${OUTPUT_DIR}${NC}"
