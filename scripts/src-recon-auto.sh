#!/bin/bash
# SRC 自动化信息收集脚本（完整版）
# 使用方法: ./scripts/src-recon-auto.sh example.com

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

# ============================================
# 阶段 1-3: 基础信息收集（已修复）
# ============================================

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

    # 提取 IP 列表（如果 http_scanner_enhanced.py 没有生成）
    if [ ! -f "${OUTPUT_DIR}/resolved_ips.txt" ]; then
        if [ -f "${OUTPUT_DIR}/domain_ip_mapping.json" ]; then
            # 从映射中提取 IP
            python3 << EOF
import json

with open('${OUTPUT_DIR}/domain_ip_mapping.json', 'r') as f:
    mapping = json.load(f)

ips = set()
for domain, ips_list in mapping.items():
    if isinstance(ips_list, list):
        ips.update(ips_list)

with open('${OUTPUT_DIR}/resolved_ips.txt', 'w') as f:
    for ip in sorted(ips):
        f.write(ip + '\n')

print(f"[+] 从域名映射提取 {len(ips)} 个 IP")
EOF
            python3 core/connection_improver.py "${OUTPUT_DIR}/http_services.txt" "${OUTPUT_DIR}/connection_improvement.txt"
        fi
    fi
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无子域名列表，跳过 HTTP 扫描${NC}"
fi

# ============================================
# 阶段 4-12: 深度分析（新增）
# ============================================

# 4. JS 文件分析
echo -e "\n${YELLOW}[*] 阶段 4: JS 文件分析${NC}"
if [ -f "${OUTPUT_DIR}/http_urls.txt" ] && [ -s "${OUTPUT_DIR}/http_urls.txt" ] && command -v python3 &> /dev/null; then
    echo "[*] 分析可访问的 HTTP 服务"
    
    # 对 200 状态的服务进行 JS 分析
    cd "$PROJECT_ROOT"
    for url in $(cat "${OUTPUT_DIR}/http_urls.txt" 2>/dev/null || true); do
        echo "    [*] 分析: $url"
        
        # 只分析 200 状态的服务
        STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
        
        if [ "$STATUS" = "200" ]; then
            python3 core/jsfind.py "$url" 2>/dev/null || true
        fi
    done
    
    # 合并所有 JS 分析结果
    if ls ${OUTPUT_DIR}/jsfind_results/api_endpoints.txt 2>/dev/null; then
        API_COUNT=$(wc -l < ${OUTPUT_DIR}/jsfind_results/api_endpoints.txt 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $API_COUNT 个 API 端点${NC}"
    fi
    
    if ls ${OUTPUT_DIR}/jsfind_results/paths.txt 2>/dev/null; then
        PATH_COUNT=$(wc -l < ${OUTPUT_DIR}/jsfind_results/paths.txt 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $PATH_COUNT 个路径${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无可访问的 HTTP 服务，跳过 JS 分析${NC}"
fi

# 5. Vue.js 检测
echo -e "\n${YELLOW}[*] 阶段 5: Vue.js 应用检测${NC}"
if [ -f "${OUTPUT_DIR}/http_urls.txt" ] && [ -s "${OUTPUT_DIR}/http_urls.txt" ] && command -v python3 &> /dev/null; then
    echo "[*] 检测 Vue.js 应用"
    
    cd "$PROJECT_ROOT"
    for url in $(cat "${OUTPUT_DIR}/http_urls.txt" 2>/dev/null || true); do
        STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
        
        if [ "$STATUS" = "200" ]; then
            python3 core/vuecrack.py "$url" 2>/dev/null || true
        fi
    done
    
    # 检查是否有结果
    if [ -f "${OUTPUT_DIR}/vuecrack_report.txt" ]; then
        if grep -q "Vue.js 检测" "${OUTPUT_DIR}/vuecrack_report.txt"; then
            echo -e "${GREEN}[+] 检测到 Vue.js 应用${NC}"
        else
            echo -e "${YELLOW}[*] 未检测到 Vue.js 应用${NC}"
        fi
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无可访问的 HTTP 服务，跳过 Vue.js 检测${NC}"
fi

# 6. Spring Boot Actuator 检测
echo -e "\n${YELLOW}[*] 阶段 6: Spring Boot Actuator 检测${NC}"
if [ -f "${OUTPUT_DIR}/http_urls.txt" ] && [ -s "${OUTPUT_DIR}/http_urls.txt" ] && command -v python3 &> /dev/null; then
    echo "[*] 检测 Spring Boot Actuator"
    
    cd "$PROJECT_ROOT"
    for url in $(cat "${OUTPUT_DIR}/http_urls.txt" 2>/dev/null || true); do
        STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
        
        if [ "$STATUS" = "200" ]; then
            python3 core/actuator_scanner.py "$url" 2>/dev/null || true
        fi
    done
    
    # 检查是否有结果
    if [ -f "${OUTPUT_DIR}/actuator_report.txt" ]; then
        if grep -q "Actuator 检测" "${OUTPUT_DIR}/actuator_report.txt"; then
            echo -e "${GREEN}[+] 检测到 Spring Boot Actuator${NC}"
        else
            echo -e "${YELLOW}[*] 未检测到 Actuator${NC}"
        fi
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无可访问的 HTTP 服务，跳过 Actuator 检测${NC}"
fi

# 7. 路径爆破测试
echo -e "\n${YELLOW}[*] 阶段 7: 路径爆破测试${NC}"
if [ -f "${OUTPUT_DIR}/http_urls.txt" ] && [ -s "${OUTPUT_DIR}/http_urls.txt" ] && command -v python3 &> /dev/null; then
    echo "[*] 路径拼接与爆破测试"
    
    # 生成路径列表（如果有）
    if [ -f "${OUTPUT_DIR}/jsfind_results/paths.txt" ]; then
        cp "${OUTPUT_DIR}/jsfind_results/paths.txt" "${OUTPUT_DIR}/extracted_paths.txt"
        PATH_COUNT=$(wc -l < "${OUTPUT_DIR}/extracted_paths.txt" 2>/dev/null || echo "0")
        echo "    [*] 提取 $PATH_COUNT 个路径"
    fi
    
    # 对每个 URL 进行路径爆破
    cd "$PROJECT_ROOT"
    for url in $(cat "${OUTPUT_DIR}/http_urls.txt" 2>/dev/null || true); do
        echo "    [*] 测试: $url"
        
        STATUS=$(curl -Isk "$url" 2>/dev/null | grep "HTTP/" | awk '{print $2}' | head -1)
        
        if [ "$STATUS" = "200" ] || [ "$STATUS" = "403" ]; then
            python3 core/path_bruteforcer.py "$url" "${OUTPUT_DIR}/extracted_paths.txt" "${OUTPUT_DIR}/path_bruteforce_$(basename $url | tr -d '.').txt" 2>/dev/null || true
        fi
    done
    
    # 合并结果
    cat ${OUTPUT_DIR}/path_bruteforce_*.txt 2>/dev/null | grep -v "^$" > "${OUTPUT_DIR}/path_bruteforce_combined.txt" || true
    
    # 统计结果
    if [ -f "${OUTPUT_DIR}/path_bruteforce_combined.txt" ]; then
        ACCESSIBLE_COUNT=$(grep -c "^- \[200\]" "${OUTPUT_DIR}/path_bruteforce_combined.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $ACCESSIBLE_COUNT 个可访问 URL${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无可访问的 HTTP 服务，跳过路径爆破${NC}"
fi

# 8. 智能漏洞分析
echo -e "\n${YELLOW}[*] 阶段 8: 智能漏洞分析${NC}"
if [ -f "${OUTPUT_DIR}/path_bruteforce_combined.txt" ] && command -v python3 &> /dev/null; then
    echo "[*] 智能漏洞分析"
    
    # 生成 JSON 格式的扫描结果
    cd "$PROJECT_ROOT"
    
    # 创建扫描结果 JSON
    python3 << EOF
import json
import re
from pathlib import Path

output_dir = Path("${OUTPUT_DIR}")
results = []

# 从路径爆破结果提取
if (output_dir / "path_bruteforce_combined.txt").exists():
    with open(output_dir / "path_bruteforce_combined.txt", 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('- [200]'):
                parts = line.split()
                url = parts[1]
                size = int(parts[3].replace('bytes', '').strip()) if len(parts) > 3 else 0
                results.append({
                    'url': url,
                    'status': 200,
                    'size': size,
                    'accessible': True
                })
            elif line.startswith('- [403]'):
                parts = line.split()
                url = parts[1]
                results.append({
                    'url': url,
                    'status': 403,
                    'accessible': False
                })

# 保存 JSON
with open(output_dir / "all_scan_results.json", 'w') as f:
    json.dump(results, f, indent=2)

print(f"[+] 整合了 {len(results)} 个扫描结果")
EOF
    
    # 运行智能分析
    python3 core/vulnerability_analyzer.py "${OUTPUT_DIR}/all_scan_results.json" "${OUTPUT_DIR}/vulnerability_analysis.txt" 2>/dev/null || true
    
    # 查看结果
    if [ -f "${OUTPUT_DIR}/vulnerability_analysis.txt" ]; then
        HIGH_RISK=$(grep -c "^### " "${OUTPUT_DIR}/vulnerability_analysis.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $HIGH_RISK 个高风险问题${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[*] 无路径爆破结果，跳过智能分析${NC}"
fi

# 9. 最终报告生成
echo -e "\n${YELLOW}[*] 阶段 9: 生成最终报告${NC}"

# 统计
SUB_COUNT=$(wc -l < "${OUTPUT_DIR}/all_subs.txt" 2>/dev/null || echo "0")
HTTP_COUNT=$(wc -l < "${OUTPUT_DIR}/http_urls.txt"  2>/dev/null || echo "0")
RESOLVED_IPS=$(wc -l < "${OUTPUT_DIR}/resolved_ips.txt" 2>/dev/null || echo "0")

# JS 分析统计
API_ENDPOINTS_COUNT=$(wc -l < "${OUTPUT_DIR}/jsfind_results/api_endpoints.txt" 2>/dev/null || echo "0")
PATHS_COUNT=$(wc -l < "${OUTPUT_DIR}/jsfind_results/paths.txt"  2>/dev/null || echo "0")
SECRETS_COUNT=$(wc -l < "${OUTPUT_DIR}/jsfind_results/secrets.txt"  2>/dev/null || echo "0")

# Vue.js 检测
VUE_DETECTED="否"
if grep -q "Vue.js 检测.*是" "${OUTPUT_DIR}/vuecrack_report.txt" 2>/dev/null || true; then
    VUE_DETECTED="是"
fi

# Actuator 检测
ACTUATOR_DETECTED="否"
if grep -q "Actuator 检测.*是" "${OUTPUT_DIR}/actuator_report.txt"  2>/dev/null || true; then
    ACTUATOR_DETECTED="是"
fi

# 路径爆破统计
BRUTEFORCE_COUNT=$(wc -l < "${OUTPUT_DIR}/path_bruteforce_combined.txt" 2>/dev/null || echo "0")
BRUTEFORCE_ACCESSIBLE=$(grep -c "^- \[200\]" "${OUTPUT_DIR}/path_bruteforce_combined.txt" 2>/dev/null || echo "0")

# 智能分析统计
VULN_HIGH=$(grep -c "^### " "${OUTPUT_DIR}/vulnerability_analysis.txt" 2>/dev/null || echo "0")

cat > "$REPORT_FILE" << EOF
# SRC 信息收集报告

**目标**: $TARGET
**时间**: $(date +%Y-%m-%d\ %H:%M:%S)
**扫描模式**: ${SCAN_MODE:-快速扫描}

---

## 📊 统计信息

| 项目 | 数量 |
|------|------|
| 子域名 | $SUB_COUNT |
| 解析的 IP | $RESOLVED_IPS |
| HTTP 服务 | $HTTP_COUNT |
| 开放端口 | $(grep -c "open" "${OUTPUT_DIR}/port_scan.gnmap" 2>/dev/null || echo "0") |

---

## 🔍 JS 分析结果

### API 端点
- **发现**: $API_ENDPOINTS_COUNT 个

### 发现的路径
- **发现**: $PATHS_COUNT 个

### 敏感信息
- **发现**: $SECRETS_COUNT 个

### 可访问的 Chunk 文件
- **发现**: $(grep -c "^-" "${OUTPUT_DIR}/jsfind_results/accessible_chunks.txt" 2>/dev/null || echo "0") 个

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

### 基础信息
- **all_subs.txt** - 子域名列表
- **http_services.txt** - HTTP 服务扫描结果
- **http_urls.txt** - HTTP URL 列表
- **resolved_ips.txt** - IP 地址列表

### JS 分析
- **jsfind_results/****
  - api_endpoints.txt - API 端点
  - paths.txt - 提取的路径
  - secrets.txt - 敏感信息

### Web 应用检测
- **vuecrack_report.txt** - Vue.js 检测结果
- **actuator_report.txt** - Actuator 检测结果

### 路径爆破
- **path_bruteforce_combined.txt** - 合并的测试结果

### 智能分析
- **vulnerability_analysis.txt** - 智能漏洞分析报告

---

**生成工具**: 小牛的 SRC 信息收集技能 🦞
EOFREPORT

echo -e "${GREEN}[+] 报告已生成: $REPORT_FILE${NC}"

echo -e "\n${GREEN}[+] 信息收集完成！${NC}"
echo -e "${YELLOW}[+] 结果目录: $OUTPUT_DIR${NC}"
echo -e "${YELLOW}[+] 查看报告: cat $REPORT_FILE${NC}"

# 如果有高风险问题，提醒用户
if [ "$VULN_HIGH" ] && [ "$VULN_HIGH" -gt 0 ]; then
    echo ""
    echo -e "${RED}[!] 发现 $VULN_HIGH 个高风险问题，请优先验证${NC}"
    echo "    建议: cat ${OUTPUT_DIR}/vulnerability_analysis.txt | grep '^###' | head -10"
fi
