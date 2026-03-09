#!/bin/bash
# 阶段 3: 端口扫描脚本（参考 fscan 原理，不使用漏洞 payload）
# 使用方法: ./scripts/stage3_port_scan.sh <target>

set -e

# 获取脚本目录和 project 根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置变量
TARGET="$1"
STAGE2_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage2"
STAGE3_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage3"

# 颜色输出
RED='\033[0;31m'
GREEN='\033 f[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查参数
if [ -z "$TARGET" ]; then
    echo -e "${RED}[-] 请输入目标域名${NC}"
    echo "使用方法: $0 <target>"
    exit 1
fi

echo -e "${GREEN}[+] 阶段 3: 端口扫描${NC}"
echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 输出目录: $STAGE3_DIR${NC}"

# 检查阶段 2 结果
if [ ! -d "$STAGE2_DIR" ]; then
    echo -e "${RED}[-] 阶段 2 结果不存在，请先运行: ./scripts/stage2_service_scan.sh $TARGET${NC}"
    exit 1
fi

# 创建输出目录
mkdir -p "$STAGE3_DIR"

# ============================================
# 端口扫描（参考 fscan 原理）
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 端口扫描（参考 fscan 原理）${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查 IP 列表
if [ ! -f "${STAGE2_DIR}/all_ips_unique.txt" ]; then
    echo -e "${RED}[-] IP 列表不存在: ${STAGE2_DIR}/all_ips_unique.txt${NC}"
    echo -e "${YELLOW}[!] 尝试从 HTTP 扫描结果生成...${NC}"
    
    # 尝试从 HTTP 扫描结果生成 IP 列表
    if [ -f "${STAGE2_DIR}/domain_ip_mapping.json" ]; then
        echo "[*] 从域名映射提取 IP..."
        python3 << EOF
import json
from pathlib import Path

mapping_file = Path("${STAGE2_DIR}/domain_ip_mapping.json")
ips_file = Path("${STAGE2_DIR}/all_ips_unique.txt")

with open(mapping_file, 'r') as f:
    mapping = json.load(f)

ips = set()
for domain, ip_list in mapping.items():
    if isinstance(ip_list, list):
        ips.update(ip_list)

with open(ips_file, 'w') as f:
    for ip in sorted(ips):
        f.write(ip + '\n')

print(f"[+] 提取 {len(ips)} 个 IP")
EOF
    else
        echo -e "${RED}[-] 无法生成 IP 列表${NC}"
        exit 1
    fi
fi

IP_COUNT=$(wc -l < "${STAGE2_DIR}/all_ips_unique.txt" 2>/dev/null || echo "0")
echo "[*] 待扫描 IP: $IP_COUNT 个"

# 扫描模式（快速/全端口）
SCAN_MODE="${SCAN_MODE:-fast}"

if [ "$SCAN_MODE" = "full" ]; then
    echo -e "\n${YELLOW}[*] 全端口扫描 (1-65535)${NC}"
    PORT_RANGE="-p-"
else
    echo -e "\n${YELLOW}[*] 快速扫描 (Top 1000 + Web 端口)${NC}"
    PORT_RANGE="-p 80,443,8080,8443,3000,5000,8888,9000,9443 --top-ports 1000"
fi

# 执行端口扫描
echo "[*] 开始端口扫描..."
nmap -iL "${STAGE2_DIR}/all_ips_unique.txt" \
    $PORT_RANGE \
    -T4 --open \
    -oG "${STAGE3_DIR}/port_scan.gnmap" \
    2>/dev/null || true

# 检查扫描结果
if [ -f "${STAGE3_DIR}/port_scan.gnmap" ]; then
    PORT_COUNT=$(grep -c "open" "${STAGE3_DIR}/port_scan.gnmap" || echo "0")
    echo -e "${GREEN}[+] 端口扫描完成，发现 $PORT_COUNT 个开放端口${NC}"
else
    echo -e "${YELLOW}[!] 端口扫描未生成结果文件${NC}"
    PORT_COUNT=0
fi

# ============================================
# 提取 Web 端口 IP
# ============================================
echo -e "\n${YELLOW}[*] 提取 Web 服务 IP${NC}"

if [ -f "${STAGE3_DIR}/port_scan.gnmap" ]; then
    # 提取开放 80/443/8080/8443 端口的主机
    grep -E "80/tcp|443/tcp|8080/tcp|8443/tcp" "${STAGE3_DIR}/port_scan.gnmap" | \
        grep "open" | \
        awk '{print $2}' > "${STAGE3_DIR}/web_ips.txt" 2>/dev/null || \
        touch "${STAGE3_DIR}/web_ips.txt"
    
    WEB_IP_COUNT=$(wc -l < "${STAGE3}//web_ips.txt" 2>/dev/null || echo "0")
    echo -e "${GREEN}[+] 发现 $WEB_IP_COUNT 个 Web 服务 IP${NC}"
    
    if [ "$WEB_IP_COUNT" -gt 0 ]; then
        echo "[*] 前 10 个 Web 服务 IP:"
        head -10 "${STAGE3_DIR}/web_ips.txt" | nl
    fi
else
    echo -e "${YELLOW}[!] 端口扫描结果不存在，跳过 Web IP 提取${NC}"
    > "${STAGE3_DIR}/web_ips.txt"
    WEB_IP_COUNT=0
fi

# ============================================
# 生成端口 URL 并测试
# ============================================
if [ "$WEB_IP_COUNT" -gt 0 ]; then
    echo -e "\n${YELLOW}[*] 生成端口 URL 并测试 HTTP/HTTPS 服务${NC}"
    
    # 生成端口 URL
    > "${STAGE3_DIR}/port_http_urls.txt"
    while IFS= read -r ip; do
        echo "http://$ip" >> "${STAGE3_DIR}/port_http_urls.txt"
        echo "https://$ip" >> "${STAGE3_DIR}/port_http_urls.txt"
    done < "${STAGE3_DIR}/web_ips.txt"
    
    PORT_URL_COUNT=$(wc -l < "${STAGE3_DIR}/port_http_urls.txt" 2>/dev/null || echo "0")
    echo -e "${GREEN}[+] 生成 $PORT_URL_COUNT 个端口 URL${NC}"
    
    # HTTP/HTTPS 服务扫描
    echo "[*] 扫描端口 URL..."
    cd "$PROJECT_ROOT"
    python3 core/http_scanner_enhanced.py \
        "${STAGE3_DIR}/port_http_urls.txt" \
        "${STAGE3_DIR}/port_http_services.txt" \
        "${STAGE3_DIR}/port_resolved_ips.txt" \
        "${STAGE3_DIR}/port_domain_ip_mapping.json"
    
    # 提取可访问的 URL
    if [ -f "${STAGE3_DIR}/port_http_services.txt" ]; then
        grep -E "^\[200\]|^\[30[0-9]\]|^\[403\]" "${STAGE3_DIR}/port_http_services.txt" | \
            awk '{print $2}' > "${STAGE3_DIR}/port_accessible_urls.txt" 2>/dev/null || \
            touch "${STAGE3_DIR}/port_accessible_urls.txt"
        
        PORT_HTTP_COUNT=$(wc -l < "${STAGE3}/port_accessible_urls.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 端口服务中发现 $PORT_HTTP_COUNT 个可访问的 URL${NC}"
        
        # 显示前 5 个
        if [ "$PORT_HTTP_COUNT" -gt 0 ]; then
            echo "[*] 可访问的端口服务（前 5 个）:"
            head -5 "${STAGE3_DIR}/port_accessible_urls.txt" | nl
        fi
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[!] 没有发现 Web 端口，跳过端口 URL 测试${NC}"
fi

# ============================================
# 其他端口的三方应用测试
# ============================================
echo -e "\n${YELLOW}[*] 测试其他端口的三方应用${NC}"

# 常见的三方应用端口
COMMON_PORTS="22,21,25,110,143,3306,3389,5432,5900,5901,5902,5903,5904,27017,27018,27019"

# 提取这些端口的主机
if [ -f "${STAGE3_DIR}/port_scan.gnmap" ]; then
    echo "[*] 测试常见三方服务端口: $COMMON_PORTS"
    
    > "${STAGE3_DIR}/other_service_ips.txt"
    for port in ${COMMON_PORTS//,/ }; do
        grep -E "${port}/tcp.*open" "${STAGE3_DIR}/port_scan.gnmap" | \
            awk '{print $2}' >> "${STAGE3_DIR}/other_service_ips.txt" 2>/dev/null || true
    done
    
    OTHER_IP_COUNT=$(wc -l < "${STAGE3_DIR}/other_service_ips.txt" 2>/dev/null || echo "0")
    
    if [ "$OTHER_IP_COUNT" -gt 0 ]; then
        echo -e "${GREEN}[+] 发现 $OTHER_IP_COUNT 个其他服务 IP${NC}"
        
        # 生成测试 URL
        > "${STAGE3_DIR}/other_service_urls.txt"
        while IFS= read -r ip; do
            echo "http://$ip:80" >> "${STAGE3_DIR}/other_service_urls.txt"
            echo "https://$ip:443" >> "${STAGE3_DIR}/other_service_urls.txt"
        done < "${STAGE3_DIR}/other_service_ips.txt"
        
        # HTTP 测试
        echo "[*] HTTP 测试其他端口服务..."
        cd "$PROJECT_ROOT"
        python3 core/http_scanner_enhanced.py \
            "${STAGE3_DIR}/other_service_urls.txt" \
            "${STAGE3_DIR}/other_service_results.txt"
        
        # 提取可访问的 URL
        if [ -f "${STAGE3_DIR}/other_service_results.txt" ]; then
            grep -E "^\[200\]|^\[30[0-9]\]" "${STAGE3_DIR}/other_service_results.txt" | \
                awk '{print $2}' > "${STAGE3_DIR}/other_accessible_urls.txt" 2>/dev/null || \
                touch "${STAGE3_DIR}/other_accessible_urls.txt"
            
            OTHER_ACCESSIBLE_COUNT=$(wc -l < "${STAGE3_DIR}/other_accessible_urls.txt" 2>/dev/null || echo "0")
            
            if [ "$OTHER_ACCESSIBLE_COUNT" -gt 0 ]; then
                echo -e "${GREEN}[+] 其他端口中发现 $OTHER_ACCESSIBLE_COUNT 个可访问的 HTTP 服务${NC}"
                
                # 显示前 5 个
                echo "[*] 可访问的其他端口服务（前 5 个）:"
                head -5 "${STAGE3_DIR}/other_accessible_urls.txt" | nl
            fi
        fi
        
        cd - > /dev/null || true
    fi
fi

# ============================================
# 合并所有可访问的 URL
# ============================================
echo -e "\n${YELLOW}[*] 合并所有可访问的 URL${NC}"

> "${STAGE3_DIR}/all_accessible_urls.txt"

# 添加阶段 2 的可访问 URL
if [ -f "${STAGE2_DIR}/http_accessible_urls.txt" ]; then
    cat "${STAGE2_DIR}/http_accessible_urls.txt" >> "${STAGE3_DIR}/all_accessible_urls.txt"
fi

# 添加端口扫描发现的可访问 URL
if [ -f "${STAGE3_DIR}/port_accessible_urls.txt" ]; then
    cat "${STAGE3_DIR}/port_accessible_urls.txt" >> "${STAGE3_DIR}/all_accessible_urls.txt"
fi

# 添加其他端口的可访问 URL
if [ -f "${STAGE3_DIR}/other_accessible_urls.txt" ]; then
    cat "${STAGE3_DIR}/other_accessible_urls.txt" >> "${STAGE3_DIR}/all_accessible_urls.txt"
fi

# 去重
sort -u "${STAGE3_DIR}/all_accessible_urls.txt" -o "${STAGE3_DIR}/all_accessible_urls.txt"

TOTAL_ACCESSIBLE=$(wc -l < "${STAGE3_DIR}/all_accessible_urls.txt" 2>/dev/null || echo "0")
echo -e "${GREEN}[+] 汇总去重后得到 $TOTAL_ACCESSIBLE 个可访问的 URL${NC}"

# ============================================
# 输出摘要
# ============================================
echo -e "\n${GREEN}[+] 阶段 3 完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 端口扫描统计${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  扫描 IP: $IP_COUNT 个"
echo -e "  开放端口: $PORT_COUNT 个"
echo -e "  Web 服务 IP: $WEB_IP_COUNT 个"
echo -e "  端口服务可访问: $PORT_HTTP_COUNT 个"
echo -e "  其他端口可访问: $OTHER_ACCESSIBLE_COUNT 个"
echo -e "  总计可访问 URL: $TOTAL_ACCESSIBLE 个"
echo ""
echo -e "${YELLOW}[+] 下一阶段: 运行 ./scripts/stage4_deep_analysis.sh $TARGET"
echo -e "${YELLOW}[+] 或继续执行: ./scripts/stage3_port_scan.sh $TARGET"
echo -e "${YELLOW}[+] 完整流程: ./scripts/src-recon-auto-optimized.sh $TARGET"
echo -e "${BLUE}========================================${NC}"

# 如果有可访问的 URL，建议进行深度分析
if [ "$TOTAL_ACCESSIBLE" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}[*] 发现 $TOTAL_ACCESS_COUNT 个可访问的 URL，建议运行深度分析${NC}"
    echo -e "    ./scripts/stage4_deep_analysis.sh $TARGET"
fi
