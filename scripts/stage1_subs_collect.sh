#!/bin/bash
# 阶段 1: 子域名收集脚本
# 使用方法: ./scripts/stage1_subs_collect.sh <target>

set -e

# 获取脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置变量
TARGET="$1"
OUTPUT_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage1"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查参数
if [ -z "$TARGET" ]; then
    echo -e "${RED}[-] 请输入目标域名${NC}"
    echo "使用方法: $0 <target>"
    exit 1
fi

echo -e "${GREEN}[+] 阶段 1: 子域名收集${NC}"
echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 输出目录: $OUTPUT_DIR${NC}"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# ============================================
# 方法 1: FOFA 收集
# ============================================
echo -e "\n${YELLOW}[*] 方法 1: FOFA 子域名收集${NC}"
if [ -n "$FOFA_EMAIL" ] && [ -n "$FOFA_KEY" ]; then
    cd "$PROJECT_ROOT"
    python3 core/fofa_subs.py "$TARGET"
    
    if [ -f "fofa_subs.txt" ]; then
        > "${OUTPUT_DIR}/all_subs.txt"
        > "${OUTPUT_DIR}/all_ips.txt"
        > "${OUTPUT_DIR}/all_urls.txt"
        
        sub_count=0
        while IFS= read -r subdomain; do
            echo "$subdomain" >> "${OUTPUT_DIR}/all_subs.txt"
            echo "http://$subdomain" >> "${OUTPUT_DIR}/all_urls.txt"
            echo "https://$subdomain" >> "${OUTPUT_DIR}/all_urls.txt"
            
            # 尝试解析 IP
            if host -W 1 "$subdomain" &> /dev/null; then
                ip=$(host -t A "$subdomain" | grep "has address" | awk '{print $4}' | head -1)
                if [ -n "$ip" ]; then
                    echo "$ip" >> "${OUTPUT_DIR}/all_ips.txt"
                fi
            fi
            
            ((sub_count++))
        done < fofa_subs.txt
        
        rm fofa_subs.txt
        
        echo -e "${GREEN}[+] FOFA 发现 $sub_count 个子域名${NC}"
    fi
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[!] FOFA API 未配置，跳过${NC}"
fi

# ============================================
# 方法 2: Simple Subfinder 收集
# ============================================
echo -e "\n${YELLOW}[*] 方法 2: Certificate Transparency + DNSdumpster 收集${NC}"
cd "$PROJECT_ROOT"
python3 core/simple_subfinder.py "$TARGET" 2>/dev/null | \
    while IFS= read -r subdomain; do
        # 避免重复
        if ! grep -q "^${subdomain}$" "${OUTPUT_DIR}/all_subs.txt" 2>/dev/null; then
            echo "$subdomain" >> "${OUTPUT_DIR}/all_subs.txt"
            echo "http://$subdomain" >> "${OUTPUT_DIR}/all_urls.txt"
            echo "https://subdomain" >> "${OUTPUT_DIR}/all_urls.txt"
            
            # 尝试解析 IP
            if host -W 1 "$subdomain" &> /dev/null; then
                ip=$(host -t A "$subdomain" | grep "has address" | awk '{print $4}' | head -1)
                if [ -n "$ip" ]; then
                    # 避免重复
                    if ! grep -q "^${ip}$" "${OUTPUT_DIR}/all_ips.txt" 2>/dev/null; then
                        echo "$ip" >> "${OUTPUT_DIR}/all_ips.txt"
                    fi
                fi
            fi
        fi
done
cd - > /dev/null || true

# ============================================
# 方法 3: 字典爆破
# ============================================
echo -e "\n${YELLOW}[*] 方法 3: 子域名字典爆破${NC}"
if [ -f "${PROJECT_ROOT}/wordlists/subdomains.txt" ]; then
    word_count=$(wc -l < "${PROJECT_ROOT}/wordlists/subdomains.txt")
    echo "[*] 字典大小: $word_count 个"
    
    found_count=0
    while IFS= read -r word; do
        subdomain="${word}.${TARGET}"
        
        # 测试 DNS 解析
        if host -W 1 "$subdomain" &> /dev/null; then
            # 避免重复
            if ! grep -q "^${subdomain}$" "${OUTPUT_DIR}/all_subs.txt" 2>/dev/null; then
                echo "$subdomain" >> "${OUTPUT_DIR}/all_subs.txt"
                echo "http://$subdomain" >> "${OUTPUT_DIR}/all_urls.txt"
                echo "https://subdomain" >> "${OUTPUT_DIR}/all_urls.txt"
                
                echo "[+] 发现: $subdomain"
                ((found_count++))
                
                # 解析 IP
                ip=$(host -t A "$subdomain" | grep "has address" | awk '{print $4}' | head -1)
                if [ -n "$ip" ]; then
                    if ! grep -q "^${ip}$" "${OUTPUT_DIR}/all_ips.txt" 2>/dev/null; then
                        echo "$ip" >> "${OUTPUT_DIR}/all_ips.txt"
                    fi
                fi
            fi
        fi
    done < "${PROJECT_ROOT}/wordlists/subdomains.txt"
    
    echo -e "${GREEN}[+] 字典爆破发现 $found_count 个子域名${NC}"
else
    echo -e "${YELLOW}[!] 字典文件不存在，跳过${NC}"
fi

# ============================================
# 整合和去重
# ============================================
echo -e "\n${YELLOW}[*] 整合和去重${NC}"

# 子域名去重
sort -u "${OUTPUT_DIR}/all_subs.txt" -o "${OUTPUT_DIR}/all_subs_unique.txt"
SUB_COUNT=$(wc -l < "${OUTPUT_DIR}/all_subs_unique.txt" 2>/dev/null || echo "0")
echo -e "${GREEN}[+] 总计: $SUB_COUNT 个唯一子域名${NC}"

# URL 去重
sort -u "${OUTPUT_DIR}/all_urls.txt" -o "${OUTPUT_DIR}/all_urls_unique.txt"
URL_COUNT=$(wc -l < "${OUTPUT_DIR}/all_urls_unique.txt" 2>/dev/null || echo "0")
echo -e "${GREEN}[+] 生成 $URL_COUNT 个唯一 URL${NC}"

# IP 去重
sort -u "${OUTPUT_DIR}/all_ips.txt" -o "${OUTPUT_DIR}/all_ips_unique.txt"
IP_COUNT=$(wc -l < "${OUTPUT_DIR}/all_ips_unique.txt" 2>/dev/null || echo "0")
echo -e "${GREEN}[+] 解析 $IP_COUNT 个唯一 IP${NC}"

# 生成 IP 映射
echo "[*] 生成域名到 IP 映射..."
python3 << EOF
import json
import socket
from pathlib import Path

mapping = {}
output_dir = Path("${OUTPUT_DIR}")
subs_file = output_dir / "all_subs_unique.txt"
mapping_file = output_dir / "domain_ip_mapping.json"

with open(subs_file, 'r') as f:
    for line in f:
        subdomain = line.strip()
        if not subdomain:
            continue
        
        try:
            # 获取 A 记录
            answers = socket.getaddrinfo(subdomain, None)
            ips = set()
            for answer in answers:
                if answer[0] == socket.AF_INET:
                    ips.add(answer[4][0])
            
            if ips:
                mapping[subdomain] = list(ips)
        except:
            pass

with open(mapping_file, 'w') as f:
    json.dump(mapping, f, indent=2)

print(f"[+] 生成映射: {len(mapping)} 个域名")
EOF

# ============================================
# 输出摘要
# ============================================
echo -e "\n${GREEN}[+] 阶段 1 完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 子域名统计${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  唯一子域名: $SUB_COUNT 个"
echo -e "  唯一 IP: $IP_COUNT 个"
echo -e "  唯一 URL: $URL_COUNT 个"
echo ""
echo -e "${YELLOW}[+] 下一阶段: 运行 ./scripts/stage2_service_scan.sh $TARGET"
echo -e "${YELLOW}[+] 或继续执行: ./scripts/stage1_subs_collect.sh $TARGET"
echo -e "${YELLOW}[+] 完整流程: ./scripts/src-recon-auto-optimized.sh $TARGET"
echo -e "${BLUE}========================================${NC}"
