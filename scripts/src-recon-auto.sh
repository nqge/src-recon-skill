#!/bin/bash
# SRC 自动化信息收集脚本
# 使用方法: ./scripts/src-recon-auto.sh example.com

set -e

# 获取脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置变量
TARGET="$1"
OUTPUT_DIR="${PROJECT_ROOT}/output/recon/${TARGET}"

# 初始化变量
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="${OUTPUT_DIR}/report_${TIMESTAMP}.md"

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
mkdir -p "$OUTPUT_DIR"

# 1. 子域名枚举
echo -e "\n${YELLOW}[*] 阶段 1: 子域名枚举${NC}"
if command -v python3 &> /dev/null; then
    if [ -n "$FOFA_EMAIL" ] && [ -n "$FOFA_KEY" ]; then
        echo "[*] 使用 FOFA 收集子域名"
        cd "$PROJECT_ROOT"
        python3 core/fofa_subs.py "$TARGET"
        if [ -f "fofa_subs.txt" ]; then
            mv fofa_subs.txt "${OUTPUT_DIR}/all_subs.txt"
            SUB_COUNT=$(wc -l < "${OUTPUT_DIR}/all_subs.txt" 2>/dev/null || echo "0")
            echo -e "${GREEN}[+] FOFA 发现 $SUB_COUNT 个子域名${NC}"
        fi
        cd - > /dev/null
    else
        echo -e "${YELLOW}[*] FOFA API 未配置，跳过${NC}"
    fi
else
    echo -e "${RED}[-] Python3 未安装${NC}"
fi

# 2. HTTP/HTTPS 服务扫描
echo -e "\n${YELLOW}[*] 阶段 2: HTTP/HTTPS 服务扫描${NC}"
if [ -f "${OUTPUT_DIR}/all_subs.txt" ] && command -v python3 &> /dev/null; then
    echo "[*] 正在扫描 HTTP/HTTPS 服务..."
    cd "$PROJECT_ROOT"
    python3 core/http_scanner_enhanced.py "${OUTPUT_DIR}/all_subs.txt" "${OUTPUT_DIR}/http_services.txt"
    
    # 提取 URL
    if [ -f "${OUTPUT_DIR}/http_services.txt" ]; then
        grep -E "^\[200\]|^\[30[0-9]\]|^\[403\]" "${OUTPUT_DIR}/http_services.txt" | awk '{print $2}' > "${OUTPUT_DIR}/http_urls.txt" 2>/dev/null || true
        HTTP_COUNT=$(wc -l < "${OUTPUT_DIR}/http_urls.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $HTTP_COUNT 个 HTTP 服务${NC}"
    fi
    cd - > /dev/null
else
    echo -e "${YELLOW}[*] 无子域名列表，跳过 HTTP 扫描${NC}"
fi

# 3. 端口扫描
echo -e "\n${YELLOW}[*] 阶段 3: 端口扫描${NC}"
if [ -f "${OUTPUT_DIR}/resolved_ips.txt" ]; then
    SCAN_MODE="${SCAN_MODE:-fast}"
    echo "[*] 扫描模式: $SCAN_MODE"
    
    if [ "$SCAN_MODE" = "full" ]; then
        echo "[*] 全端口扫描 (1-65535)"
        nmap -iL "${OUTPUT_DIR}/resolved_ips.txt" -p- -T4 --open -oG "${OUTPUT_DIR}/port_scan_full.gnmap" 2>/dev/null || true
    else
        echo "[*] 快速扫描 (Top 1000 + Web 端口)"
        nmap -iL "${OUTPUT_DIR}/resolved_ips.txt" -p 80,443,8080,8443,3000,5000,8888,9000,9443 --top-ports 1000 -T4 --open -oG "${OUTPUT_DIR}/port_scan.gnmap" 2>/dev/null || true
    fi
    
    if [ -f "${OUTPUT_DIR}/port_scan.gnmap" ]; then
        PORT_COUNT=$(grep -c "open" "${OUTPUT_DIR}/port_scan.gnmap" || echo "0")
        echo -e "${GREEN}[+] 发现 $PORT_COUNT 个开放端口${NC}"
    fi
fi

# 4. 生成报告
echo -e "\n${YELLOW}[*] 生成报告${NC}"

# 统计
SUB_COUNT=$(wc -l < "${OUTPUT_DIR}/all_subs.txt" 2>/dev/null || echo "0")
HTTP_COUNT=$(wc -l < "${OUTPUT_DIR}/http_urls.txt" 2>/dev/null || echo "0")

cat > "$REPORT_FILE" << EOFREPORT
# SRC 信息收集报告

**目标**: $TARGET
**时间**: $(date +%Y-%m-%d\ %H:%M:%S)
**扫描模式**: ${SCAN_MODE:-快速扫描}

---

## 📊 统计信息

| 项目 | 数量 |
|------|------|
| 子域名 | $SUB_COUNT |
| HTTP 服务 | $HTTP_COUNT |

---

## 📁 输出文件

- all_subs.txt - 子域名列表
- http_services.txt - HTTP 扫描结果
- http_urls.txt - HTTP URL 列表
- resolved_ips.txt - IP 地址列表
- port_scan.gnmap - 端口扫描结果

---

**生成工具**: 小牛的 SRC 信息收集技能 🦞
EOFREPORT

echo -e "${GREEN}[+] 报告已生成: $REPORT_FILE${NC}"

echo -e "\n${GREEN}[+] 信息收集完成！${NC}"
echo -e "${YELLOW}[+] 结果目录: $OUTPUT_DIR${NC}"
echo -e "${YELLOW}[+] 查看报告: cat $REPORT_FILE${NC}"
