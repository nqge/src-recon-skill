#!/bin/bash
# SRC 自动化信息收集脚本（优化版 - 三阶段流程）
# 使用方法: ./scripts/src-recon-auto-optimized.sh example.com

set -e

# 获取脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置变量
TARGET="$1"
OUTPUT_DIR="${PROJECT_ROOT}/output/recon/${TARGET}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="${OUTPUT_DIR}/report_${TIMESTAMP}.md"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查参数
if [ -z "$TARGET" ]; then
    echo -e "${RED}[-] 请输入目标域名${NC}"
    echo "使用方法: $0 example.com"
    exit 1
fi

echo -e "${GREEN}[+] 开始 SRC 信息收集（优化版）${NC}"
echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 输出目录: $OUTPUT_DIR${NC}"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "${OUTPUT_DIR}/stage1"

# ============================================
# 阶段 1: 子域名收集（多工具并行）
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 阶段 1: 子域名收集${NC}"
echo -e "${BLUE}========================================${NC}"

# 初始化子域名列表
> "${OUTPUT_DIR}/stage1/all_subs.txt"
> "${OUTPUT_DIR}/stage1/all_ips.txt"
> "${OUTPUT_DIR}/stage1/all_urls.txt"

# 方法 1: FOFA 收集
if [ -n "$FOFA_EMAIL" ] && [ -n "$FOFA_KEY" ]; then
    echo -e "\n${YELLOW}[*] 方法 1: FOFA 子域名收集${NC}"
    cd "$PROJECT_ROOT"
    python3 core/fofa_subs.py "$TARGET"
    
    if [ -f "fofa_subs.txt" ]; then
        # 提取子域名、IP、URL
        while IFS= read -r line; do
            # 子域名
            echo "$line" >> "${OUTPUT_DIR}/stage1/all_subs.txt"
            
            # 生成 URL
            echo "http://$line" >> "${OUTPUT_DIR}/stage1/all_urls.txt"
            echo "https://$line" >> "${OUTPUT_DIR}/stage1/all_urls.txt"
        done < fofa_subs.txt
        
        rm fofa_subs.txt
        echo -e "${GREEN}[+] FOFA 收集完成${NC}"
    fi
    cd - > /dev/null || true
fi

# 方法 2: Subfinder 收集
if command -v subfinder &> /dev/null; then
    echo -e "\n${YELLOW}[*] 方法 2: Subfinder 子域名收集${NC}"
    
    subfinder -d "$TARGET" -silent | tee "${OUTPUT_DIR}/stage1/subfinder_subs.txt" | \
        while IFS= read -r line; do
            echo "$line" >> "${OUTPUT_DIR}/stage1/all_subs.txt"
            echo "http://$line" >> "${OUTPUT_DIR}/stage1/all_urls.txt"
            echo "https://$line" >> "${OUTPUT_DIR}/stage1/all_urls.txt"
        done
    
    echo -e "${GREEN}[+] Subfinder 收集完成${NC}"
else
    echo -e "${YELLOW}[!] Subfinder 未安装，跳过${NC}"
fi

# 方法 3: FuzzDomain 暴力收集
if [ -f "${PROJECT_ROOT}/wordlists/subdomains.txt" ]; then
    echo -e "\n${YELLOW}[*] 方法 3: FuzzDomain 子域名爆破${NC}"
    
    # 使用 FuzzDomain（如果可用）
    if command -v fuzzdomain &> /dev/null; then
        fuzzdomain -d "$TARGET" -w "${PROJECT_ROOT}/wordlists/subdomains.txt" -silent | \
            tee "${OUTPUT_DIR}/stage1/fuzzdomain_subs.txt" | \
            while IFS= read -r line; do
                echo "$line" >> "${OUTPUT_DIR}/stage1/all_subs.txt"
                echo "http://$line" >> "${OUTPUT_DIR}/stage1/all_urls.txt"
                echo "https://$line" >> "${OUTPUT_DIR}/stage1/all_urls.txt"
            done
        
        echo -e "${GREEN}[+] FuzzDomain 收集完成${NC}"
    else
        echo -e "${YELLOW}[!] FuzzDomain 未安装，使用字典爆破${NC}"
        
        # 使用简单的字典爆破
        for word in $(cat "${PROJECT_ROOT}/wordlists/subdomains.txt" | head -100); do
            subdomain="${word}.${TARGET}"
            
            # 测试 DNS 解析
            if host -W 1 "$subdomain" &> /dev/null; then
                echo "$subdomain" >> "${OUTPUT_DIR}/stage1/all_subs.txt"
                echo "http://$subdomain" >> "${OUTPUT_DIR}/stage1/all_urls.txt"
                echo "https://$subdomain" >> "${OUTPUT_DIR}/stage1/all_urls.txt"
            fi
        done
        
        echo -e "${GREEN}[+] 字典爆破完成${NC}"
    fi
else
    echo -e "${YELLOW}[!] 字典文件不存在，跳过 FuzzDomain${NC}"
fi

# 去重和统计
echo -e "\n${YELLOW}[*] 整合和去重${NC}"

# 子域名去重
sort -u "${OUTPUT_DIR}/stage1/all_subs.txt" -o "${OUTPUT_DIR}/stage1/all_subs_unique.txt"
SUB_COUNT=$(wc -l < "${OUTPUT_DIR}/stage1/all_subs_unique.txt" 2>/dev/null || echo "0")
echo -e "${GREEN}[+] 收集到 $SUB_COUNT 个唯一子域名${NC}"

# URL 去重
sort -u "${OUTPUT_DIR}/stage1/all_urls.txt" -o "${OUTPUT_DIR}/stage1/all_urls_unique.txt"
URL_COUNT=$(wc -l < "${OUTPUT_DIR}/stage1/all_urls_unique.txt" 2>/dev/null || echo "0")
echo -e "${GREEN}[+] 生成 $URL_COUNT 个唯一 URL${NC}"

# ============================================
# 阶段 2: 服务探测和 IP 解析
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 阶段 2: 服务探测和 IP 解析${NC}"
echo -e "${BLUE}========================================${NC}"

mkdir -p "${OUTPUT_DIR}/stage2"

# HTTP/HTTPS 服务扫描
echo -e "\n${YELLOW}[*] HTTP/HTTPS 服务扫描${NC}"
cd "$PROJECT_ROOT"
python3 core/http_scanner_enhanced.py \
  "${OUTPUT_DIR}/stage1/all_subs_unique.txt" \
  "${OUTPUT_DIR}/stage2/http_services.txt"

# 提取可访问的 URL
if [ -f "${OUTPUT_DIR}/stage2/http_services.txt" ]; then
    grep -E "^\[200\]|^\[30[0-9]\]|^\[403\]" "${OUTPUT_DIR}/stage2/http_services.txt" | \
        awk '{print $2}' > "${OUTPUT_DIR}/stage2/http_accessible_urls.txt"
    
    HTTP_COUNT=$(wc -l < "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" 2>/dev/null || echo "0")
    echo -e "${GREEN}[+] 发现 $HTTP_COUNT 个可访问的 HTTP 服务${NC}"
fi

# 提取阶段 2 解析的 IP
if [ -f "${OUTPUT_DIR}/stage2/resolved_ips.txt" ]; then
    cp "${OUTPUT_DIR}/stage2/resolved_ips.txt" "${OUTPUT_DIR}/stage2/stage2_ips.txt"
    echo -e "${GREEN}[+] 阶段 2 解析的 IP 已保存${NC}"
fi

# 合并阶段 1 和阶段 2 的 IP
echo -e "\n${YELLOW}[*] 合并和去重 IP${NC}"

# 收集所有 IP
> "${OUTPUT_DIR}/stage2/all_ips.txt"

# 从阶段 1 的域名解析 IP（如果还没有）
if [ -f "${OUTPUT_DIR}/stage2/resolved_ips.txt" ]; then
    cat "${OUTPUT_DIR}/stage2/resolved_ips.txt" >> "${OUTPUT_DIR}/stage2/all_ips.txt"
fi

# 从域名解析 IP
echo "[*] 从子域名解析 IP..."
while IFS= read -r subdomain; do
    # 获取 A 记录
    host -t A "$subdomain" 2>/dev/null | grep "has address" | awk '{print $4}' >> "${OUTPUT_DIR}/stage2/all_ips.txt"
done < "${OUTPUT_DIR}/stage1/all_subs_unique.txt"

# IP 去重
sort -u "${OUTPUT_DIR}/stage2/all_ips.txt" -o "${OUTPUT_DIR}/stage2/all_ips_unique.txt"
IP_COUNT=$(wc -l < "${OUTPUT_DIR}/stage2/all_ips_unique.txt" 2>/dev/null || echo "0")
echo -e "${GREEN}[+] 汇总去重后得到 $IP_COUNT 个唯一 IP${NC}"

# 连接错误改进
echo -e "\n${YELLOW}[*] 连接错误改进${NC}"
if [ -f "${OUTPUT_DIR}/stage2/http_services.txt" ]; then
    grep "\[ERROR\]" "${OUTPUT_DIR}/stage2/http_services.txt" | awk '{print $2}' > "${OUTPUT_DIR}/stage2/error_urls.txt"
    ERROR_COUNT=$(wc -l < "${OUTPUT_DIR}/stage2/error_urls.txt" 2>/dev/null || echo "0")
    
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "${BLUE}[*] 发现 $ERROR_COUNT 个有错误的 URL，尝试连接改进...${NC}"
        python3 core/http_access_tester.py \
            "${OUTPUT_DIR}/stage2/error_urls.txt" \
            "${OUTPUT_DIR}/stage2/http_access_improvement.txt"
    fi
fi

cd - > /dev/null || true

# ============================================
# 阶段 3: 端口扫描
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 阶段 3: 端口扫描${NC}"
echo -e "${BLUE}========================================${NC}"

mkdir -p "${OUTPUT_DIR}/stage3"

if [ -f "${OUTPUT_DIR}/stage2/all_ips_unique.txt" ]; then
    SCAN_MODE="${SCAN_MODE:-fast}"
    echo "[*] 扫描模式: $SCAN_MODE"
    
    if [ "$SCAN_MODE" = "full" ]; then
        echo "[*] 全端口扫描 (1-65535)"
        nmap -iL "${OUTPUT_DIR}/stage2/all_ips_unique.txt" \
            -p- -T4 --open \
            -oG "${OUTPUT_DIR}/stage3/port_scan_full.gnmap" 2>/dev/null || true
    else
        echo "[*] 快速扫描 (Top 1000 + Web 端口)"
        nmap -iL "${OUTPUT_DIR}/stage2/all_ips_unique.txt" \
            -p 80,443,8080,8443,3000,5000,8888,9000,9443 \
            --top-ports 1000 -T4 --open \
            -oG "${OUTPUT_DIR}/stage3/port_scan.gnmap" 2>/dev/null || true
    fi
    
    if [ -f "${OUTPUT_DIR}/stage3/port_scan.gnmap" ]; then
        PORT_COUNT=$(grep -c "open" "${OUTPUT_DIR}/stage3/port_scan.gnmap" || echo "0")
        echo -e "${GREEN}[+] 发现 $PORT_COUNT 个开放端口${NC}"
        
        # 提取 Web 端口的 IP
        grep -E "80/tcp|443/tcp|8080/tcp|8443/tcp" "${OUTPUT_DIR}/stage3/port_scan.gnmap" | \
            grep "open" | awk '{print $2}' > "${OUTPUT_DIR}/stage3/web_ips.txt"
        
        WEB_IP_COUNT=$(wc -l < "${OUTPUT_DIR}/stage3/web_ips.txt" 2>/dev/null || echo "0")
        
        if [ "$WEB_IP_COUNT" -gt 0 ]; then
            echo -e "${BLUE}[*] 发现 $WEB_IP_COUNT 个 Web 服务 IP，生成 URL 列表...${NC}"
            
            # 生成端口 URL
            while IFS= read -r ip; do
                echo "http://$ip" >> "${OUTPUT_DIR}/stage3/port_http_urls.txt"
                echo "https://$ip" >> "${OUTPUT_DIR}/stage3/port_http_urls.txt"
            done < "${OUTPUT_DIR}/stage3/web_ips.txt"
            
            # 扫描端口 URL
            echo "[*] 扫描新发现的 Web 服务..."
            cd "$PROJECT_ROOT"
            python3 core/http_scanner_enhanced.py \
                "${OUTPUT_DIR}/stage3/port_http_urls.txt" \
                "${OUTPUT_DIR}/stage3/port_http_services.txt"
            
            # 合并可访问的 URL
            if [ -f "${OUTPUT_DIR}/stage3/port_http_services.txt" ]; then
                grep -E "^\[200\]|^\[30[0-9]\]|^\[403\]" "${OUTPUT_DIR}/stage3/port_http_services.txt" | \
                    awk '{print $2}' >> "${OUTPUT_DIR}/stage2/http_accessible_urls.txt"
                
                # 去重
                sort -u "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" -o "${OUTPUT_DIR}/stage2/http_accessible_urls.txt"
                
                NEW_HTTP_COUNT=$(wc -l < "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" 2>/dev/null || echo "0")
                echo -e "${GREEN}[+] 更新后可访问的 HTTP 服务: $NEW_HTTP_COUNT${NC}"
            fi
            
            cd - > /dev/null || true
        fi
    fi
else
    echo -e "${YELLOW}[!] 没有 IP 列表，跳过端口扫描${NC}"
fi

# ============================================
# 阶段 4-9: 深度分析
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 阶段 4-9: 深度分析${NC}"
echo -e "${BLUE}========================================${NC}"

mkdir -p "${OUTPUT_DIR}/stage4"

# 阶段 4: JS 文件分析
echo -e "\n${YELLOW}[*] 阶段 4: JS 文件分析${NC}"
if [ -f "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" ] && [ -s "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" ]; then
    echo "[*] 分析可访问的 HTTP 服务"
    
    # 创建 jsfind 结果目录
    mkdir -p "${OUTPUT_DIR}/jsfind_results"
    
    # 创建临时 URL 文件
    > "${OUTPUT_DIR}/stage4/js_urls.txt"
    
    cd "$PROJECT_ROOT"
    for url in $(cat "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" 2>/dev/null | head -20); do
        echo "    [*] 检查: $url"
        
        STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
        
        if [ "$STATUS" = "200" ]; then
            echo "$url" >> "${OUTPUT_DIR}/stage4/js_urls.txt"
        fi
    done
    
    # 检查是否有需要分析的 URL
    if [ -s "${OUTPUT_DIR}/stage4/js_urls.txt" ]; then
        URL_COUNT=$(wc -l < "${OUTPUT_DIR}/stage4/js_urls.txt" 2>/dev/null || echo "0")
        echo "[*] 分析 $URL_COUNT 个 200 OK 的 URL"
        
        # 使用 jsfind 分析
        python3 core/jsfind.py "${OUTPUT_DIR}/stage4/js_urls.txt" "${OUTPUT_DIR}/jsfind_results" 2>/dev/null || true
    else
        echo "[*] 无 200 OK 的 URL，跳过 JS 分析"
    fi
    
    if [ -f "${OUTPUT_DIR}/jsfind_results/api_endpoints.txt" ]; then
        API_COUNT=$(wc -l < "${OUTPUT_DIR}/jsfind_results/api_endpoints.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $API_COUNT 个 API 端点${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无可访问的 HTTP 服务，跳过 JS 分析${NC}"
fi

# 阶段 5: Vue.js 检测
echo -e "\n${YELLOW}[*] 阶段 5: Vue.js 应用检测${NC}"
if [ -f "${OUTPUT_DIR}/stage4/js_urls.txt" ] && [ -s "${OUTPUT_DIR}/stage4/js_urls.txt" ]; then
    echo "[*] 检测 Vue.js 应用"
    
    > "${OUTPUT_DIR}/stage4/vuecrack_results.txt"
    
    cd "$PROJECT_ROOT"
    for url in $(cat "${OUTPUT_DIR}/stage4/js_urls.txt" 2>/dev/null | head -20); do
        echo "    [*] 检测: $url"
        
        STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
        
        if [ "$STATUS" = "200" ]; then
            python3 core/vuecrack.py "$url" "${OUTPUT_DIR}/stage4/vuecrack_$(basename $url | tr -d '.').txt" 2>/dev/null || true
        fi
    done
    
    # 合并结果
    cat ${OUTPUT_DIR}/stage4/vuecrack_*.txt 2>/dev/null | grep -v "^$" > "${OUTPUT_DIR}/stage4/vuecrack_combined.txt" || true
    
    if [ -f "${OUTPUT_DIR}/stage4/vuecrack_combined.txt" ] && [ -s "${OUTPUT_DIR}/stage4/vuecrack_combined.txt" ]; then
        VUE_COUNT=$(grep -c "Vue.js" "${OUTPUT_DIR}/stage4/vuecrack_combined.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 检测到 $VUE_COUNT 个 Vue.js 应用${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无可访问的 HTTP 服务，跳过 Vue.js 检测${NC}"
fi

# 阶段 6: Actuator 检测
echo -e "\n${YELLOW}[*] 阶段 6: Spring Boot Actuator 检测${NC}"
if [ -f "${OUTPUT_DIR}/stage4/js_urls.txt" ] && [ -s "${OUTPUT_DIR}/stage4/js_urls.txt" ]; then
    echo "[*] 检测 Spring Boot Actuator"
    
    > "${OUTPUT_DIR}/stage4/actuator_results.txt"
    
    cd "$PROJECT_ROOT"
    for url in $(cat "${OUTPUT_DIR}/stage4/js_urls.txt" 2>/dev/null | head -20); do
        echo "    [*] 检测: $url"
        
        STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
        
        if [ "$STATUS" = "200" ]; then
            python3 core/actuator_scanner.py "$url" "${OUTPUT_DIR}/stage4/actuator_$(basename $url | tr -d '.').txt" 2>/dev/null || true
        fi
    done
    
    # 合并结果
    cat ${OUTPUT_DIR}/stage4/actuator_*.txt 2>/dev/null | grep -v "^$" > "${OUTPUT_DIR}/stage4/actuator_combined.txt" || true
    
    if [ -f "${OUTPUT_DIR}/stage4/actuator_combined.txt" ] && [ -s "${OUTPUT_DIR}/stage4/actuator_combined.txt" ]; then
        ACTUATOR_COUNT=$(grep -c "Actuator" "${OUTPUT_DIR}/stage4/actuator_combined.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 检测到 $ACTUATOR_COUNT 个 Actuator 端点${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无可访问的 HTTP 服务，跳过 Actuator 检测${NC}"
fi

# 阶段 7: 路径爆破测试
echo -e "\n${YELLOW}[*] 阶段 7: 路径爆破测试${NC}"
if [ -f "${OUTPUT_DIR}/stage4/js_urls.txt" ] && [ -s "${OUTPUT_DIR}/stage4/js_urls.txt" ]; then
    echo "[*] 路径拼接与爆破测试"
    
    # 检查是否有提取的路径
    EXTRACTED_PATHS="${OUTPUT_DIR}/stage4/extracted_paths.txt"
    > "${EXTRACTED_PATHS}"
    
    if [ -f "${OUTPUT_DIR}/jsfind_results/paths.txt" ]; then
        cp "${OUTPUT_DIR}/jsfind_results/paths.txt" "${EXTRACTED_PATHS}"
        PATH_COUNT=$(wc -l < "${EXTRACTED_PATHS}" 2>/dev/null || echo "0")
        echo "    [*] 从 JS 文件提取 $PATH_COUNT 个路径"
    fi
    
    # 添加常见管理路径
    cat >> "${EXTRACTED_PATHS}" << 'EOF'
/admin
/admin/login
/admin/dashboard
/api
/api/v1
/api/v2
/config
/settings
/management
/console
/control
/actuator
/actuator/health
/actuator/env
/env
/health
/info
/beans
/mappings
/heapdump
/threaddump
EOF
    
    TOTAL_PATHS=$(wc -l < "${EXTRACTED_PATHS}" 2>/dev/null || echo "0")
    echo "    [*] 总计 $TOTAL_PATHS 个路径待测试"
    
    cd "$PROJECT_ROOT"
    for url in $(cat "${OUTPUT_DIR}/stage4/js_urls.txt" 2>/dev/null | head -10); do
        echo "    [*] 测试: $url"
        
        STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
        
        if [ "$STATUS" = "200" ] || [ "$STATUS" = "403" ]; then
            python3 core/path_bruteforcer.py "$url" \
                "${EXTRACTED_PATHS}" \
                "${OUTPUT_DIR}/stage4/path_bruteforce_$(basename $url | tr -d '.').txt" 2>/dev/null || true
        fi
    done
    
    # 合并结果
    cat ${OUTPUT_DIR}/stage4/path_bruteforce_*.txt 2>/dev/null | grep -v "^$" > "${OUTPUT_DIR}/stage4/path_bruteforce_combined.txt" || true
    
    if [ -f "${OUTPUT_DIR}/stage4/path_bruteforce_combined.txt" ] && [ -s "${OUTPUT_DIR}/stage4/path_bruteforce_combined.txt" ]; then
        ACCESSIBLE_COUNT=$(grep -c "^- \[200\]" "${OUTPUT_DIR}/stage4/path_bruteforce_combined.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $ACCESSIBLE_COUNT 个可访问路径${NC}"
    else
        echo "[*] 路径爆破未发现可访问路径"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无可访问的 HTTP 服务，跳过路径爆破${NC}"
fi

# 阶段 8: 智能漏洞分析
echo -e "\n${YELLOW}[*] 阶段 8: 智能漏洞分析${NC}"
if [ -f "${OUTPUT_DIR}/stage4/path_bruteforce_combined.txt" ]; then
    echo "[*] 智能漏洞分析"
    
    cd "$PROJECT_ROOT"
    
    python3 -c "
import json
from pathlib import Path

output_dir = Path('${OUTPUT_DIR}')
results = []

if (output_dir / 'stage4/path_bruteforce_combined.txt').exists():
    with open(output_dir / 'stage4/path_bruteforce_combined.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('- [200]'):
                parts = line.split()
                url = parts[1] if len(parts) > 1 else ''
                size = int(parts[3].replace('bytes', '').strip()) if len(parts) > 3 else 0
                results.append({'url': url, 'status': 200, 'size': size, 'accessible': True})
            elif line.startswith('- [403]'):
                parts = line.split()
                url = parts[1] if len(parts) > 1 else ''
                results.append({'url': url, 'status': 403, 'accessible': False})

with open(output_dir / 'all_scan_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'[+] 整合了 {len(results)} 个扫描结果')
"
    
    if [ -f "${OUTPUT_DIR}/all_scan_results.json" ]; then
        python3 core/vulnerability_analyzer.py \
            "${OUTPUT_DIR}/all_scan_results.json" \
            "${OUTPUT_DIR}/vulnerability_analysis.txt" 2>/dev/null || true
    fi
    
    if [ -f "${OUTPUT_DIR}/vulnerability_analysis.txt" ]; then
        HIGH_RISK=$(grep -c "^### " "${OUTPUT_DIR}/vulnerability_analysis.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $HIGH_RISK 个高风险问题${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无路径爆破结果，跳过智能分析${NC}"
fi

# ============================================
# 阶段 9: API 参数测试
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 阶段 9: API 参数测试${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查 jsfind_results 目录
if [ -d "${OUTPUT_DIR}/jsfind_results" ] && [ -f "${OUTPUT_DIR}/stage4/js_urls.txt" ]; then
    echo "[*] 检测到可访问的 URL 和 JS 分析结果"
    echo "[*] 开始 API 参数测试..."
    
    # 检查 api_endpoints.txt 是否有内容
    API_COUNT=$(wc -l < "${OUTPUT_DIR}/jsfind_results/api_endpoints.txt" 2>/dev/null || echo "0")
    
    if [ "$API_COUNT" -gt 0 ]; then
        echo "[*] 发现 $API_COUNT 个 API 端点，开始测试..."
        
        cd "$PROJECT_ROOT"
        
        # 运行 API 参数测试工具
        python3 core/api_parameter_tester.py \
            "$TARGET" \
            "${OUTPUT_DIR}/jsfind_results" \
            2>&1 | tee "${OUTPUT_DIR}/stage9/api_parameter_test_output.txt"
        
        # 移动报告到输出目录
        if ls api_parameter_test_report_*.md 1> /dev/null 2>&1; then
            mv api_parameter_test_report_*.md "${OUTPUT_DIR}/stage9/" 2>/dev/null || true
            echo -e "${GREEN}[+] API 参数测试报告已生成${NC}"
            
            # 显示高风险问题数量
            HIGH_RISK_API=$(grep -c "🔴 高风险问题" "${OUTPUT_DIR}"/stage9/api_parameter_test_report_*.md 2>/dev/null || echo "0")
            if [ "$HIGH_RISK_API" -gt 0 ]; then
                echo -e "${YELLOW}[!] 发现 $HIGH_RISK_API 个 API 参数测试高风险问题${NC}"
            fi
        fi
        
        cd - > /dev/null || true
    else
        echo "[*] 未发现 API 端点，跳过 API 参数测试"
    fi
else
    echo -e "${YELLOW}[*] 缺少 JS 分析结果，跳过 API 参数测试${NC}"
fi

# ============================================
# 阶段 10: 智能漏洞分析
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 阶段 10: 智能漏洞分析${NC}"
echo -e "${BLUE}========================================${NC}"

if [ -f "${OUTPUT_DIR}/stage4/path_bruteforce_combined.txt" ]; then
    echo "[*] 整合所有扫描结果进行智能分析"
    
    cd "$PROJECT_ROOT"
    
    # 加载路径爆破结果
    python3 -c "
import json
from pathlib import Path

output_dir = Path('${OUTPUT_DIR}')
results = []

if (output_dir / 'stage4/path_bruteforce_combined.txt').exists():
    with open(output_dir / 'stage4/path_bruteforce_combined.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('- [200]'):
                parts = line.split()
                url = parts[1] if len(parts) > 1 else ''
                size = int(parts[3].replace('bytes', '').strip()) if len(parts) > 3 else 0
                results.append({'url': url, 'status': 200, 'size': size, 'accessible': True})
            elif line.startswith('- [403]'):
                parts = line.split()
                url = parts[1] if len(parts) > 1 else ''
                results.append({'url': url, 'status': 403, 'accessible': False})

with open(output_dir / 'all_scan_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'[+] 整合了 {len(results)} 个扫描结果')
"
    
    # 加载 API 参数测试结果
    if [ -f "${OUTPUT_DIR}/stage9/api_parameter_test_report_*.md" ]; then
        echo "[*] 包含 API 参数测试结果"
    fi
    
    # 运行智能漏洞分析
    if [ -f "${OUTPUT_DIR}/all_scan_results.json" ]; then
        python3 core/vulnerability_analyzer.py \
            "${OUTPUT_DIR}/all_scan_results.json" \
            "${OUTPUT_DIR}/vulnerability_analysis.txt" 2>/dev/null || true
    fi
    
    if [ -f "${OUTPUT_DIR}/vulnerability_analysis.txt" ]; then
        HIGH_RISK=$(grep -c "^### " "${OUTPUT_DIR}/vulnerability_analysis.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $HIGH_RISK 个高风险问题${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无路径爆破结果，跳过智能分析${NC}"
fi

# ============================================
# 阶段 11: 最终报告生成
# ============================================
echo -e "\n${YELLOW}[*] 阶段 11: 生成最终报告${NC}"

# 统计
SUB_COUNT=$(wc -l < "${OUTPUT_DIR}/stage1/all_subs_unique.txt" 2>/dev/null || echo "0")
HTTP_COUNT=$(wc -l < "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" 2>/dev/null || echo "0")
IP_COUNT=$(wc -l < "${OUTPUT_DIR}/stage2/all_ips_unique.txt" 2>/dev/null || echo "0")
PORT_COUNT=$(grep -c "open" "${OUTPUT_DIR}/stage3/port_scan.gnmap" 2>/dev/null || echo "0")

API_ENDPOINTS_COUNT=$(wc -l < "${OUTPUT_DIR}/jsfind_results/api_endpoints.txt" 2>/dev/null || echo "0")
PATHS_COUNT=$(wc -l < "${OUTPUT_DIR}/jsfind_results/paths.txt" 2>/dev/null || echo "0")
SECRETS_COUNT=$(wc -l < "${OUTPUT_DIR}/jsfind_results/secrets.txt" 2>/dev/null || echo "0")

# API 参数测试统计
API_TEST_TOTAL=$(grep -c "总测试数" "${OUTPUT_DIR}"/stage9/api_parameter_test_report_*.md 2>/dev/null || echo "0")
API_TEST_HIGH=$(grep -c "🔴 高风险问题" "${OUTPUT_DIR}"/stage9/api_parameter_test_report_*.md 2>/dev/null || echo "0")
API_TEST_MEDIUM=$(grep -c "🟡 中风险问题" "${OUTPUT_DIR}"/stage9/api_parameter_test_report_*.md 2>/dev/null || echo "0")

VUE_DETECTED="否"
if grep -q "Vue.js 检测.*是" "${OUTPUT_DIR}/vuecrack_report.txt" 2>/dev/null || true; then
    VUE_DETECTED="是"
fi

ACTUATOR_DETECTED="否"
if grep -q "Actuator 检测.*是" "${OUTPUT_DIR}/actuator_report.txt" 2>/dev/null || true; then
    ACTUATOR_DETECTED="是"
fi

BRUTEFORCE_COUNT=$(wc -l < "${OUTPUT_DIR}/stage4/path_bruteforce_combined.txt" 2>/dev/null || echo "0")
BRUTEFORCE_ACCESSIBLE=$(grep -c "^- \[200\]" "${OUTPUT_DIR}/stage4/path_bruteforce_combined.txt" 2>/dev/null || echo "0")

VULN_HIGH=$(grep -c "^### " "${OUTPUT_DIR}/vulnerability_analysis.txt" 2>/dev/null || echo "0")

cat > "$REPORT_FILE" << EOF
# SRC 信息收集报告（优化版）

**目标**: $TARGET
**时间**: $(date +%Y-%m-%d\ %H:%M:%S)
**扫描模式**: ${SCAN_MODE:-快速扫描}

---

## 📊 统计信息

| 项目 | 数量 |
|------|------|
| 子域名 | $SUB_COUNT |
| IP 地址 | $IP_COUNT |
| HTTP 服务 | $HTTP_COUNT |
| 开放端口 | $PORT_COUNT |

---

## 🔍 JS 分析结果

### API 端点
- **发现**: $API_ENDPOINTS_COUNT 个

### 发现的路径
- **发现**: $PATHS_COUNT 个

### 敏感信息
- **发现**: $SECRETS_COUNT 个

---

## 🌐 Web 应用检测

### Vue.js 应用
- **检测**: $VUE_DETECTED

### Spring Boot Actuator
- **检测**: $ACTUATOR_DETECTED

---

## 🔍 路径爆破测试结果

### 测试 URL: $BRUTEFORCE_COUNT 个
### 可访问: $BRUTEFORCE_ACCESSIBLE 个

---

## 🧪 API 参数测试结果

### 总测试数: $API_TEST_TOTAL 个
### 高风险问题: $API_TEST_HIGH 个
### 中风险问题: $API_TEST_MEDIUM 个

---

## 🧠 智能漏洞分析

### 高风险问题: $VULN_HIGH 个

---

## 📁 输出文件

### 阶段 1: 子域名收集
- **stage1/all_subs_unique.txt** - 唯一子域名列表
- **stage1/all_urls_unique.txt** - 唯一 URL 列表

### 阶段 2: 服务探测
- **stage2/http_services.txt** - HTTP 服务扫描结果
- **stage2/http_accessible_urls.txt** - 可访问的 URL
- **stage2/all_ips_unique.txt** - 唯一 IP 列表
- **stage2/http_access_improvement.txt** - 连接改进报告

### 阶段 3: 端口扫描
- **stage3/port_scan.gnmap** - 端口扫描结果
- **stage3/port_http_services.txt** - 端口 HTTP 服务

### 阶段 4-9: 深度分析
- **jsfind_results/** - JS 分析结果
- **vuecrack_report.txt** - Vue.js 检测报告
- **actuator_report.txt** - Actuator 检测报告
- **stage4/path_bruteforce_combined.txt** - 路径爆破结果
- **vulnerability_analysis.txt** - 智能漏洞分析报告

---

**生成工具**: 小牛的 SRC 信息收集技能（优化版）🦞
EOF

echo -e "${GREEN}[+] 报告已生成: $REPORT_FILE${NC}"

echo -e "\n${GREEN}[+] 信息收集完成！${NC}"
echo -e "${YELLOW}[+] 结果目录: $OUTPUT_DIR${NC}"
echo -e "${YELLOW}[+] 查看报告: cat $REPORT_FILE${NC}"

if [ "$VULN_HIGH" ] && [ "$VULN_HIGH" -gt 0 ]; then
    echo ""
    echo -e "${RED}[!] 发现 $VULN_HIGH 个高风险问题，请优先验证${NC}"
    echo "    建议: cat ${OUTPUT_DIR}/vulnerability_analysis.txt | grep '^###' | head -10"
fi

# ============================================
# 生成统一报告
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 生成统一分析报告${NC}"
echo -e "${BLUE}========================================${NC}"

if [ -f "${PROJECT_ROOT}/utils/generate_report.sh" ]; then
    bash "${PROJECT_ROOT}/utils/generate_report.sh" "$OUTPUT_DIR" "$TARGET" "full_stage"
else
    echo -e "${YELLOW}[!] 统一报告生成器未找到，跳过${NC}"
fi

