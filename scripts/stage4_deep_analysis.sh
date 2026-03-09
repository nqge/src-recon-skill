#!/bin/bash
# 阶段 4: 深度分析脚本
# 使用方法: ./scripts/stage4_deep_analysis.sh <target>

set -e

# 获取脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置变量
TARGET="$1"
STAGE2_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage2"
STAGE3_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage3"
STAGE4_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage4"

# 颜色输出
RED='\033[031m'
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

echo -e "${GREEN}[+] 阶段 4: 深度分析${NC}"
echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 输出目录: $STAGE4_DIR${NC}"

# 检查前置阶段
if [ ! -d "$STAGE2_DIR" ] || [ ! -d "$STAGE3_DIR" ]; then
    echo -e "${RED}[-] 前置阶段结果不存在${NC}"
    echo -e "${YELLOW}[*] 请先运行: ./scripts/stage2_service_scan.sh $TARGET${NC}"
    echo -e "${YELLOW}[*] 或: ./scripts/stage3_port_scan.sh $TARGET${NC}"
    exit 1
fi

# 创建输出目录
mkdir -p "$STAGE4_DIR"

# ============================================
# 收集所有可访问的 URL
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 深度分析开始${NC}"
echo -e "${BLUE}========================================${NC}"

> "${STAGE4_DIR}/all_accessible_urls.txt"

# 收集阶段 2 的可访问 URL
if [ -f "${STAGE2_DIR}/http_accessible_urls.txt" ]; then
    cat "${STAGE2_DIR}/http_accessible_urls.txt" >> "${STAGE4_DIR}/all_accessible_urls.txt"
fi

# 添加阶段 3 的可访问 URL
if [ -f "${STAGE3_DIR}/port_accessible_urls.txt" ]; then
    cat "${STAGE3_DIR}/port_accessible_urls.txt" >> "${STAGE4_DIR}/all_accessible_urls.txt"
fi

# 添加其他端口的可访问 URL
if [ -f "${STAGE3_DIR}/other_accessible_urls.txt" ]; then
    cat "${STAGE3_DIR}/other_accessible_urls.txt" >> "${STAGE4_DIR}/all_accessible_urls.txt"
fi

# 去重
sort -u "${STAGE4_DIR}/all_accessible_urls.txt" -o "${STAGE4_DIR}/all_accessible_urls_unique.txt"

TOTAL_URLS=$(wc -l < "${STAGE4_DIR}/all_accessible_urls_unique.txt" 2>/dev/null || echo "0")
echo "[*] 待分析的 URL: $TOTAL_URLS 个"

if [ "$TOTAL_URLS" -eq 0 ]; then
    echo -e "${YELLOW}[!] 没有可访问的 URL，跳过深度分析${NC}"
    exit 0
fi

# ============================================
# JS 文件分析
# ============================================
echo -e "\n${YELLOW}[*] 阶段 4.1: JS 文件分析${NC}"
echo "[*] 分析可访问的 HTTP 服务"

cd "$PROJECT_ROOT"

# 限制分析数量（避免过长时间）
MAX_URLS=50
url_count=0

for url in $(cat "${STAGE4_DIR}/all_accessible_urls_unique.txt" 2>/dev/null | head -$MAX_URLS); do
    echo "    [*] 分析: $url"
    
    STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
    
    if [ "$STATUS" = "200" ]; then
        python3 core/jsfind.py "$url" 2>/dev/null || true
    fi
    
    ((url_count++))
done

if ls ${STAGE4_DIR}/jsfind_results/api_endpoints.txt 2>/dev/null; then
    API_COUNT=$(wc -l < ${STAGE4_DIR}/jsfind_results/api_endpoints.txt 2>/dev/null || echo "0")
    echo -e "${GREEN}[+] 发现 $API_COUNT 个 API 端点${NC}"
fi

if ls ${STAGE4_DIR}/jsfind_results/paths.txt 2>/dev/null; then
    PATH_COUNT=$(wc -l < ${STAGE4_DIR}/jsfind_results/paths.txt  2>/dev/null || echo "0")
    echo -e "${GREEN}[+] 发现 $PATH_COUNT 个路径${NC}"
fi

cd - > /dev/null || true

# ============================================
# Vue.js 检测
# ============================================
echo -e "\n${YELLOW}[*] 阶段 4.2: Vue.js 应用检测${NC}"

for url in $(cat "${STAGE4_DIR}/all_accessible_urls_unique.txt" 2>/dev/null | head -$MAX_URLS); do
    STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
    
    if [ "$STATUS" = "200" ]; then
        python3 core/vuecrack.py "$url" 2>/dev/null || true
    fi
done

if grep -q "Vue.js 检测.*是" "${STAGE4_DIR}/vuecrack_report.txt" 2>/dev/null || true; then
    echo -e "${GREEN}[+] 检测到 Vue.js 应用${NC}"
fi

# ============================================
# Actuator 检测
# ============================================
echo -e "\n${YELLOW}[*] 阶段 4.3: Spring Boot Actuator 检测${NC}"

for url in $(cat "${STAGE4_DIR}/all_accessible_urls_unique.txt" 2>/dev/null | head -$MAX_URLS); do
    STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
    
    if [ "$STATUS" = "200" ]; then
        python3 core/actuator_scanner.py "$url" 2>/dev/null || true
    fi
done

if grep -q "Actuator 检测.*是" "${STAGE4_DIR}/actuator_report.txt" 2>/dev/null || true; then
    echo -e "${GREEN}[+] 检测到 Spring Boot Actuator${NC}"
fi

# ============================================
# 路径爆破测试
# ============================================
echo -e "\n${YELLOW}[*] 阶段 4.4: 路径爆破测试${NC}"

# 复制 JS 提取的路径
if [ -f "${STAGE4_DIR}/jsfind_results/paths.txt" ]; then
    cp "${STAGE4_DIR}/jsfind_results/paths.txt" "${STAGE4_DIR}/extracted_paths.txt"
    PATH_COUNT=$(wc -l < "${STAGE4_DIR}/extracted_paths.txt" 2>/dev/null || echo "0")
    echo "[*] 提取 $PATH_COUNT 个路径"
else
    echo "[*] 没有路径文件，使用默认字典"
    cp "${PROJECT_ROOT}/wordlists/dirs.txt" "${STAGE4_DIR}/extracted_paths.txt" 2>/dev/null || \
        echo "www" > "${STAGE_DIR}/extracted_paths.txt"
fi

for url in $(cat "${STAGE4_DIR}/all_accessible_urls_unique.txt" 2>/dev/null | head -20); do
    echo "    [*] 测试: $url"
    
    STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
    
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "403" ]; then
        python3 core/path_bruteforcer.py "$url" \
            "${STAGE4_DIR}/extracted_paths.txt" \
            "${STAGE4_DIR}/path_bruteforce_$(basename $url | tr -d '.').txt" 2>/dev/null || true
    fi
done

# 合并结果
cat ${STAGE4_DIR}/path_bruteforce_*.txt 2>/dev/null | grep -v "^$" > "${STAGE4_DIR}/path_bruteforce_combined.txt" || touch "${STAGE4_DIR}/path_bruteforce_combined.txt"

if [ -f "${STAGE4_DIR}/path_bruteforce_combined.txt" ]; then
    ACCESSIBLE_COUNT=$(grep -c "^- \[200\]" "${STAGE4_DIR}/path_bruteforce_combined.txt" 2>/dev/null || echo "0")
    echo -e "${GREEN}[+] 发现 $ACCESSIBLE_COUNT 个可访问 URL${NC}"
fi

# ============================================
# 智能漏洞分析
# ============================================
echo -e "\n${YELLOW}[*] 阶段 4.5: 智能漏洞分析${NC}"

if [ -f "${STAGE4_DIR}/path_bruteforce_combined.txt" ]; then
    # 整合扫描结果
    python3 << EOF
import json
from pathlib import Path

output_dir = Path("${STAGE4_DIR}")
results = []

if (output_dir / 'path_bruteforce_combined.txt').exists():
    with open(output_dir / 'path_bruteforce_combined.txt', 'r') as f:
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

print(f"[+] 整合了 {len(results)} 个扫描结果")
EOF

    # 智能分析
    python3 core/vulnerability_analyzer.py \
        "${STAGE4_DIR}/all_scan_results.json" \
        "${STAGE4_DIR}/vulnerability_analysis.txt" 2>/dev/null || true
    
    if [ -f "${STAGE4_DIR}/vulnerability_analysis.txt" ]; then
        HIGH_RISK=$(grep -c "^### " "${STAGE4_DIR}/vulnerability_analysis.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $HIGH_RISK 个高风险问题${NC}"
        
        if [ "$HIGH_RISK" -gt 0 ]; then
            echo ""
            echo -e "${RED}[!] 发现 $HIGH_RISK 个高风险问题，优先验证：${NC}"
            echo "    cat ${STAGE4_DIR}/vulnerability_analysis.txt | grep '^###' | head -10"
        fi
    fi
else
    echo "[-] 没有路径爆破结果，跳过智能分析"
fi

# ============================================
# 生成最终报告
# ============================================
echo -e "\n${YELLOW}[*] 生成最终报告${NC}"

# 统计
SUB_COUNT=$(wc -l < "${STAGE1_DIR}/all_subs_unique.txt" 2>/dev/null || echo "0")
HTTP_COUNT=$(wc -l < "${STAGE4_DIR}/all_accessible_urls_unique.txt" 2>/dev/null || echo "0")
IP_COUNT=$(wc -l < "${STAGE2_DIR}/all_ips_unique.txt" 2>/dev/null || echo "0")
PORT_COUNT=$(grep -c "open" "${STAGE3_DIR}/port_scan.gnmap" 2>/dev/null || echo "0")

API_ENDPOINTS_COUNT=$(wc -l < "${STAGE4_DIR}/jsfind_results/api_endpoints.txt" 2>/dev/null || echo "0")
PATHS_COUNT=$(wc -l < "${STAGE4_DIR}/jsfind_results/paths.txt" 2>/dev/null || echo "0")
SECRETS_COUNT=$(wc -l < "${STAGE4_DIR}/jsfind_results/secrets.txt" 2>/dev/null || echo "0")

VUE_DETECTED="否"
if grep -q "Vue.js 检测.*是" "${STAGE4_DIR}/vuecrack_report.txt" 2>/dev/null || true; then
    VUE_DETECTED="是"
fi

ACTUATOR_DETECTED="否"
if grep -q "Actuator 检测.*是" "${STAGE4_DIR}/actuator_report.txt" 2>/dev/null || true; then
    ACTUATOR_DETECTED="是"
fi

BRUTEFORCE_COUNT=$(wc -l < "${STAGE4_DIR}/path_bruteforce_combined.txt" 2>/dev/null || echo "0")
BRUTEFORCE_ACCESSIBLE=$(grep -c "^- \[200\]" "${STAGE4_DIR}/path_bruteforce_combined.txt" 2>/dev/null || echo "0")

VULN_HIGH=$(grep -c "^### " "${STAGE4_DIR}/vulnerability_analysis.txt" 2>/dev/null || echo "0")

cat > "${STAGE4_DIR}/final_report.md" << EOF
# SRC 深度分析报告

**目标**: $TARGET
**时间**: $(date +%Y-%m-%d\ %H:%M:%S)

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

## 🧠 智能漏洞分析

### 高风险问题: $VULN_HIGH 个

---

## 📁 输出文件

### 阶段 1: 子域名收集
- all_subs_unique.txt - 唯一子域名
- all_urls_unique.txt - 唯一 URL
- all_ips_unique.txt - 唯一 IP

### 阶段 2: 服务探测
- http_services.txt - HTTP 扫描结果
- http_accessible_urls.txt - 可访问的 URL
- all_ips_unique.txt - 唯一 IP（汇总）
- http_access_improvement.txt - 连接改进报告

### 阶段 3: 端口扫描
- port_scan.gnmap - 端口扫描结果
- web_ips.txt - Web 服务 IP
- port_http_services.txt - 端口 HTTP 扫描
- port_accessible_urls.txt - 端口可访问 URL
- other_service_results.txt - 其他端口测试
- other_accessible_urls.txt - 其他端口可访问 URL

### 阶段 4: 深度分析
- jsfind_results/ - JS 分析结果
- vuecrack_report.txt - Vue.js 报告
- actuator_report.txt - Actuator 报告
- path_bruteforce_combined.txt - 路径爆破结果
- vulnerability_analysis.txt - 智能分析
- final_report.md - 最终报告

---

**生成工具**: 小牛的 SRC 信息收集技能（分阶段版）🦞
EOF

echo -e "${GREEN}[+] 报告已生成: ${STAGE4_DIR}/final_report.md${NC}"

echo -e "\n${GREEN}[+] 深度分析完成！${NC}"
echo -e "${YELLOW}[+] 结果目录: ${PROJECT_ROOT}/output/recon/${TARGET}/${NC}"
echo -e "${YELLOW}[+] 查看报告: cat ${STAGE4_DIR}/final_report.md${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 完整流程${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}[+] 下一步: 可以手动运行其他工具进行更深入的分析${NC}"
echo -e "${YELLOW}[+] 或重新运行完整流程: ./scripts/src-recon-auto-optimized.sh $TARGET"
echo -e "${BLUE}========================================${NC}"

# 如果有高风险问题，提醒用户
if [ "$VULN_HIGH" ] && [ "$VULN_HIGH" -gt 0 ]; then
    echo ""
    echo -e "${RED}[!] 发现 $VULN_HIGH 个高风险问题，请优先验证${NC}"
    echo "    建议: cat ${STAGE4_DIR}/vulnerability_analysis.txt | grep '^###' | head -10"
fi
