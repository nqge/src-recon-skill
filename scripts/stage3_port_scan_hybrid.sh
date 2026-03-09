#!/bin/bash
# 阶段 3: 端口扫描（混合策略 - Nmap + 魔改 Fscan）
# 使用方法: ./scripts/stage3_port_scan_hybrid.sh <target>

set -e

# 获取脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置变量
TARGET="$1"
STAGE2_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage2"
STAGE3_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage3"

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

echo -e "${GREEN}[+] 阶段 3: 端口扫描（混合策略）${NC}"
echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 输出目录: $STAGE3_DIR${NC}"

# 检查前置阶段
if [ ! -d "$STAGE2_DIR" ]; then
    echo -e "${RED}[-] 阶段 2 结果不存在，请先运行: ./scripts/stage2_service_scan.sh $TARGET${NC}"
    exit 1
fi

# 创建输出目录
mkdir -p "$STAGE3_DIR"/{nmap,fscan,combined}

# ============================================
# 方法 1: Nmap 精准扫描（标准端口）
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 方法 1: Nmap 精准扫描（标准端口）${NC}"
echo -e "${BLUE}========================================${NC}"

# 标准端口
STANDARD_PORTS="80,443,8080,8443,3000,5000,8888,9000,9443"

if [ -f "${STAGE2_DIR}/all_ips_unique.txt" ]; then
    IP_COUNT=$(wc -l < "${STAGE2_DIR}/all_ips_unique.txt" 2>/dev/null || echo "0")
    echo "[*] 待扫描 IP: $IP_COUNT 个"
    echo "[*] 标准端口: $STANDARD_PORTS"
    
    # 魔改 nmap 参数（去除特征）
    echo "[*] 开始 Nmap 精准扫描..."
    
    nmap -iL "${STAGE2_DIR}/all_ips_unique.txt" \
        -p "$STANDARD_PORTS" \
        -T4 \
        --open \
        -Pn \
        --nmap-cli-opts="-D RND:10" \
        --source-port 53 \
        -oG "${STAGE3_DIR}/nmap/standard_ports.gnmap" \
        2>/dev/null || true
    
    # 检查扫描结果
    if [ -f "${STAGE3_DIR}/nmap/standard_ports.gnmap" ]; then
        NMAP_OPEN=$(grep -c "open" "${STAGE3_DIR}/nmap/standard_ports.gnmap" || echo "0")
        echo -e "${GREEN}[+] Nmap 扫描完成，发现 $NMAP_OPEN 个开放端口${NC}"
    else
        echo -e "${YELLOW}[!] Nmap 扫描未生成结果文件${NC}"
        NMAP_OPEN=0
    fi
else
    echo -e "${YELLOW}[!] IP 列表不存在，跳过 Nmap 扫描${NC}"
    NMAP_OPEN=0
fi

# ============================================
# 方法 2: 魔改 Fscan 快速扫描（Top 1000）
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 方法 2: 魔改 Fscan 快速扫描（Top 1000）${NC}"
echo -e "${BLUE}========================================${NC}"

if [ -f "${STAGE2_DIR}/all_ips_unique.txt" ]; then
    echo "[*] 使用魔改版扫描器（避免特征识别）"
    echo "[*] 端口范围: 1-1000"
    echo "[*] 线程数: 100"
    
    # 使用魔改版扫描器
    cd "$PROJECT_ROOT"
    python3 core/port_scanner_custom.py \
        "${STAGE2_DIR}/all_ips_unique.txt" \
        -p 1-1000 \
        -o "${STAGE3_DIR}/fscan/top1000_ports.gnmap" \
        -f gnmap \
        -t 100 \
        --timeout 3
    
    # 检查扫描结果
    if [ -f "${STAGE3_DIR}/fscan/top1000_ports.gnmap" ]; then
        FCAN_OPEN=$(grep -c "open" "${STAGE3_DIR}/fscan/top1000_ports.gnmap" || echo "0")
        echo -e "${GREEN}[+] Fscan 扫描完成，发现 $FCAN_OPEN 个开放端口${NC}"
    else
        echo -e "${YELLOW}[!] Fscan 扫描未生成结果文件${NC}"
        FCAN_OPEN=0
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[!] IP 列表不存在，跳过 Fscan 扫描${NC}"
    FCAN_OPEN=0
fi

# ============================================
# 结果整合
# ============================================
echo -e "\n${YELLOW}[*] 整合扫描结果${NC}"

> "${STAGE3_DIR}/combined/port_scan_combined.gnmap"

# 合并 Nmap 结果
if [ -f "${STAGE3_DIR}/nmap/standard_ports.gnmap" ]; then
    cat "${STAGE3_DIR}/nmap/standard_ports.gnmap" >> "${STAGE3_DIR}/combined/port_scan_combined.gnmap"
    echo "[*] 已合并 Nmap 扫描结果"
fi

# 合并 Fscan 结果
if [ -f "${STAGE3_DIR}/fscan/top1000_ports.gnmap" ]; then
    cat "${STAGE3_DIR}/fscan/top1000_ports.gnmap" >> "${STAGE3_DIR}/combined/port_scan_combined.gnmap"
    echo "[*] 已合并 Fscan 扫描结果"
fi

# 去重（同一 IP:端口 只保留一次）
if [ -f "${STAGE3_DIR}/combined/port_scan_combined.gnmap" ]; then
    # 临时文件
    temp_file="${STAGE3_DIR}/combined/temp.gnmap"
    
    # 提取 IP:端口 组合并去重
    grep -oP 'Host: \K[\d.]+' "${STAGE3_DIR}/combined/port_scan_combined.gnmap" | sort -u > "${temp_file}.ips"
    
    TOTAL_UNIQUE=$(wc -l < "${temp_file}.ips" 2>/dev/null || echo "0")
    echo -e "${GREEN}[+] 整合完成：$TOTAL_UNIQUE 个唯一 IP${NC}"
    
    # 统计总开放端口数
    TOTAL_OPEN=$(grep -c "open" "${STAGE3_DIR}/combined/port_scan_combined.gnmap" || echo "0")
    echo -e "${GREEN}[+] 总计发现 $TOTAL_OPEN 个开放端口${NC}"
fi

# ============================================
# 提取 Web 端口 IP
# ============================================
echo -e "\n${YELLOW}[*] 提取 Web 服务 IP${NC}"

if [ -f "${STAGE3_DIR}/combined/port_scan_combined.gnmap" ]; then
    # 提取开放 80/443/8080/8443 端口的主机
    grep -E "80/open|443/open|8080/open|8443/open" "${STAGE3_DIR}/combined/port_scan_combined.gnmap" | \
        awk '{print $2}' > "${STAGE3_DIR}/web_ips.txt" 2>/dev/null || \
        touch "${STAGE3_DIR}/web_ips.txt"
    
    WEB_IP_COUNT=$(wc -l < "${STAGE3_DIR}/web_ips.txt" 2>/dev/null || echo "0")
    echo -e "${GREEN}[+] 发现 $WEB_IP_COUNT 个 Web 服务 IP${NC}"
    
    if [ "$WEB_IP_COUNT" -gt 0 ]; then
        echo "[*] 前 10 个 Web 服务 IP:"
        head -10 "${STAGE3_DIR}/web_ips.txt" | nl
    fi
else
    echo -e "${YELLOW}[!] 合并结果不存在，跳过 Web IP 提取${NC}"
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
        
        PORT_HTTP_COUNT=$(wc -l < "${STAGE3_DIR}/port_accessible_urls.txt" 2>/dev/null || echo "0")
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
if [ -f "${STAGE3_DIR}/combined/port_scan_combined.gnmap" ]; then
    echo "[*] 测试常见三方服务端口: $COMMON_PORTS"
    
    > "${STAGE3_DIR}/other_service_ips.txt"
    for port in ${COMMON_PORTS//,/ }; do
        grep -E "${port}/open" "${STAGE3_DIR}/combined/port_scan_combined.gnmap" | \
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
echo -e "${BLUE}[*] 端口扫描统计（混合策略）${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  Nmap 精准扫描: $NMAP_OPEN 个开放端口"
echo -e "  Fscan 快速扫描: $FCAN_OPEN 个开放端口"
echo -e "  总计开放端口: $TOTAL_OPEN 个"
echo -e "  Web 服务 IP: $WEB_IP_COUNT 个"
echo -e "  端口服务可访问: $PORT_HTTP_COUNT 个"
echo -e "  其他端口可访问: $OTHER_ACCESSIBLE_COUNT 个"
echo -e "  总计可访问 URL: $TOTAL_ACCESSIBLE 个"
echo ""
echo -e "${YELLOW}[+] 下一阶段: 运行 ./scripts/stage4_deep_analysis.sh $TARGET"
echo -e "${YELLOW}[+] 或继续执行: ./scripts/stage3_port_scan_hybrid.sh $TARGET"
echo -e "${YELLOW}[+] 完整流程: ./scripts/src-recon-auto-hybrid.sh $TARGET"
echo -e "${BLUE}========================================${NC}"

# 如果有可访问的 URL，建议进行深度分析
if [ "$TOTAL_ACCESSIBLE" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}[*] 发现 $TOTAL_ACCESSIBLE 个可访问的 URL，建议运行深度分析${NC}"
    echo -e "    ./scripts/stage4_deep_analysis.sh $TARGET"
fi

# ============================================
# 保存扫描报告
# ============================================
cat > "${STAGE3_DIR}/scan_report.txt" << EOF
端口扫描报告（混合策略）
========================

目标: $TARGET
时间: $(date +%Y-%m-%d\ %H:%M:%S)

扫描策略:
- 方法 1: Nmap 精准扫描（标准端口: $STANDARD_PORTS）
- 方法 2: 魔改 Fscan 快速扫描（Top 1000）

扫描结果:
- Nmap 开放端口: $NMAP_OPEN 个
- Fscan 开放端口: $FCAN_OPEN 个
- 总计开放端口: $TOTAL_OPEN 个
- Web 服务 IP: $WEB_IP_COUNT 个
- 端口服务可访问: $PORT_HTTP_COUNT 个
- 其他端口可访问: $OTHER_ACCESSIBLE_COUNT 个
- 总计可访问 URL: $TOTAL_ACCESSIBLE 个

输出文件:
- Nmap 结果: nmap/standard_ports.gnmap
- Fscan 结果: fscan/top1000_ports.gnmap
- 合并结果: combined/port_scan_combined.gnmap
- Web 服务 IP: web_ips.txt
- 端口 HTTP 服务: port_http_services.txt
- 端口可访问 URL: port_accessible_urls.txt
- 其他服务结果: other_service_results.txt
- 其他可访问 URL: other_accessible_urls.txt
- 总计可访问 URL: all_accessible_urls.txt

魔改特性:
- 随机 User-Agent（6 种浏览器指纹）
- 随机延迟（50-200ms）
- 自定义 HTTP 请求头
- 避免 WAF/防火墙识别

========================
生成工具: 小牛的混合端口扫描器 🦞
EOF

echo -e "${GREEN}[+] 扫描报告已保存: ${STAGE3_DIR}/scan_report.txt${NC}"
