#!/bin/bash
# SRC 自动化信息收集脚本
# 使用方法: ./scripts/src-recon-auto.sh example.com

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE_DIR="$SCRIPT_DIR/core"
WORDLISTS_DIR="$SCRIPT_DIR/wordlists"
OUTPUT_DIR="$SCRIPT_DIR/output/recon/$TARGET"

TARGET=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$OUTPUT_DIR/report_${TIMESTAMP}.md"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查参数
if [ -z "$TARGET" ]; then
    echo -e "${RED}[-] 请输入目标域名${NC}"
    echo "使用方法: $0 example.com"
    exit 1
fi

echo -e "${GREEN}[+] 开始 SRC 信息收集${NC}"
echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 输出目录: $OUTPUT_DIR${NC}"

# 创建输出目录
mkdir -p $OUTPUT_DIR

# ... 其余脚本内容保持不变 ...
