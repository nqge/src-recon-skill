#!/bin/bash
# 阶段 1: 子域名收集脚本（智能版）
# 使用方法: ./scripts/stage1_subs_collect.sh <target>
# 
# 特性:
# - 自动检测目标类型（域名/IP/URL）
# - 仅当目标是域名时才进行子域名收集
# - 如果目标是 IP/URL，跳过子域名收集，直接生成基础文件

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
    echo -e "${RED}[-] 请输入目标${NC}"
    echo "使用方法: $0 <target>"
    echo ""
    echo "支持的目标类型:"
    echo "  - 域名: example.com"
    echo "  - URL: https://example.com"
    echo "  - IP: 192.168.1.1"
    exit 1
fi

echo -e "${GREEN}[+] 阶段 1: 目标类型检测和子域名收集${NC}"
echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 输出目录: $OUTPUT_DIR${NC}"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# ============================================
# 目标类型检测
# ============================================
echo -e "\n${YELLOW}[*] 检测目标类型...${NC}"

# 检测目标类型
TARGET_TYPE="unknown"
CLEAN_TARGET=""

# 检查是否为 IP 地址
if echo "$TARGET" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
    TARGET_TYPE="ip"
    CLEAN_TARGET="$TARGET"
    echo -e "${GREEN}[+] 检测到目标类型: IP 地址${NC}"
    
# 检查是否为 URL
elif echo "$TARGET" | grep -qE '^https?://'; then
    TARGET_TYPE="url"
    # 从 URL 中提取域名
    CLEAN_TARGET=$(echo "$TARGET" | sed -e 's|^[^/]*//||' -e 's|/.*$||' -e 's|:[0-9]*$||')
    echo -e "${GREEN}[+] 检测到目标类型: URL${NC}"
    echo -e "${YELLOW}[*] 提取的域名: $CLEAN_TARGET${NC}"
    
# 检查是否为域名
else
    # 简单的域名检测（包含点且不以/开头）
    if echo "$TARGET" | grep -qE '^[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'; then
        TARGET_TYPE="domain"
        CLEAN_TARGET="$TARGET"
        echo -e "${GREEN}[+] 检测到目标类型: 域名${NC}"
    else
        echo -e "${RED}[-] 无法识别目标类型: $TARGET${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}[*] 目标类型: $TARGET_TYPE${NC}"
echo -e "${BLUE}[*] 清理后的目标: $CLEAN_TARGET${NC}"

# ============================================
# 根据目标类型执行不同操作
# ============================================

if [ "$TARGET_TYPE" = "ip" ]; then
    # ============================================
    # 目标是 IP：跳过子域名收集
    # ============================================
    echo -e "\n${YELLOW}[*] 目标是 IP 地址，跳过子域名收集${NC}"
    
    # 生成基础文件
    > "${OUTPUT_DIR}/all_subs.txt"
    > "${OUTPUT_DIR}/all_subs_unique.txt"
    
    # 将 IP 写入文件
    echo "$CLEAN_TARGET" > "${OUTPUT_DIR}/all_ips.txt"
    echo "$CLEAN_TARGET" > "${OUTPUT_DIR}/all_ips_unique.txt"
    
    # 生成 URL（HTTP + HTTPS）
    > "${OUTPUT_DIR}/all_urls.txt"
    echo "http://$CLEAN_TARGET" >> "${OUTPUT_DIR}/all_urls.txt"
    echo "https://$CLEAN_TARGET" >> "${OUTPUT_DIR}/all_urls.txt"
    
    # 去重
    sort -u "${OUTPUT_DIR}/all_urls.txt" -o "${OUTPUT_DIR}/all_urls_unique.txt"
    
    # 统计
    SUB_COUNT=0
    IP_COUNT=1
    URL_COUNT=$(wc -l < "${OUTPUT_DIR}/all_urls_unique.txt" 2>/dev/null || echo "0")
    
    echo -e "${GREEN}[+] IP 地址处理完成${NC}"
    echo -e "${GREEN}[+] IP: $CLEAN_TARGET${NC}"
    echo -e "${GREEN}[+] 生成 $URL_COUNT 个 URL${NC}"
    
elif [ "$TARGET_TYPE" = "url" ]; then
    # ============================================
    # 目标是 URL：提取域名后进行子域名收集
    # ============================================
    echo -e "\n${YELLOW}[*] 目标是 URL，提取域名并收集子域名${NC}"
    
    # 使用提取的域名进行子域名收集
    TARGET="$CLEAN_TARGET"
    
    # 继续执行子域名收集（见下方）
    
elif [ "$TARGET_TYPE" = "domain" ]; then
    # ============================================
    # 目标是域名：进行子域名收集
    # ============================================
    echo -e "\n${YELLOW}[*] 目标是域名，开始子域名收集${NC}"
    
    # 继续执行子域名收集（见下方）
else
    echo -e "${RED}[-] 未知目标类型，退出${NC}"
    exit 1
fi

# ============================================
# 子域名收集（仅当目标是域名时）
# ============================================
if [ "$TARGET_TYPE" = "domain" ] || [ "$TARGET_TYPE" = "url" ]; then
    
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
                echo "https://$subdomain" >> "${OUTPUT_DIR}/all_urls.txt"
                
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
                    echo "https://$subdomain" >> "${OUTPUT_DIR}/all_urls.txt"
                    
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
fi

# ============================================
# 输出摘要
# ============================================
echo -e "\n${GREEN}[+] 阶段 1 完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 目标信息${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  原始目标: $1"
echo -e "  目标类型: $TARGET_TYPE"
echo -e "  清理目标: $CLEAN_TARGET"
echo ""
echo -e "${BLUE}[*] 收集统计${NC}"
echo -e "${BLUE}========================================${NC}"
if [ "$TARGET_TYPE" = "ip" ]; then
    echo -e "  唯一子域名: $SUB_COUNT 个"
    echo -e "  唯一 IP: $IP_COUNT 个"
    echo -e "  唯一 URL: $URL_COUNT 个"
elif [ "$TARGET_TYPE" = "domain" ] || [ "$TARGET_TYPE" = "url" ]; then
    echo -e "  唯一子域名: $SUB_COUNT 个"
    echo -e "  唯一 IP: $IP_COUNT 个"
    echo -e "  唯一 URL: $URL_COUNT 个"
fi
echo ""
echo -e "${YELLOW}[+] 下一阶段: 运行 ./scripts/stage2_service_scan.sh $TARGET${NC}"
echo -e "${YELLOW}[+] 或继续执行: ./scripts/stage1_subs_collect.sh $TARGET"
echo -e "${YELLOW}[+] 完整流程: ./scripts/src-recon-auto-optimized.sh $TARGET"
echo -e "${BLUE}========================================${NC}"
