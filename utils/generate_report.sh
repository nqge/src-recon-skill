#!/bin/bash
# 统一报告生成器 - 自动生成标准格式的分析报告
# 在所有分析脚本的最后调用此脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\33[0;32m'
YELLOW='\33[1;33m'
BLUE='\033[0;34m'
NC='\33[0m'

# 输入参数
OUTPUT_DIR="$1"
TARGET="$2"
ANALYSIS_TYPE="$3"  # full_stage / quick_analysis / port_scan / service_scan

# 检查参数
if [ -z "$OUTPUT_DIR" ] || [ -z "$TARGET" ] || [ -z "$ANALYSIS_TYPE" ]; then
    echo -e "${RED}[-] 参数不完整${NC}"
    exit 1
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 生成统一分析报告${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 分析类型: $ANALYSIS_TYPE${NC}"
echo -e "${GREEN}[+] 输出目录: $OUTPUT_DIR${NC}"

# 根据分析类型生成不同的报告
case "$ANALYSIS_TYPE" in
    "full_stage")
        TITLE="完整 SRC 信息收集报告"
        ;;
    "quick_analysis")
        TITLE="快速深度分析报告"
        ;;
    "port_scan")
        TITLE="端口扫描报告"
        ;;
    "service_scan")
        TITLE="服务探测报告"
        ;;
    *)
        TITLE="信息收集报告"
        ;;
esac

# 检查输出文件并生成报告
echo ""
echo -e "${YELLOW}[*] 正在扫描输出文件...${NC}"

# 初始化统计数据
SUB_COUNT=0
IP_COUNT=0
URL_COUNT=0
ACCESSIBLE_URL_COUNT=0
OPEN_PORT_COUNT=0
VULN_HIGH=0

# 检查各阶段的结果文件
if [ "$ANALYSIS_TYPE" = "full_stage" ] || [ "$ANALYSIS_TYPE" = "quick_analysis" ]; then
    # 检查阶段 1 结果
    if [ -f "${OUTPUT_DIR}/stage1/all_subs_unique.txt" ]; then
        SUB_COUNT=$(wc -l < "${OUTPUT_DIR}/stage1/all_subs_unique.txt" 2>/dev/null || echo "0")
    fi
    
    # 检查阶段 2 结果
    if [ -f "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" ]; then
        ACCESSIBLE_URL_COUNT=$(wc -l < "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" 2>/dev/null || echo "0")
    fi
    
    # 检查阶段 3 结果
    if [ -f "${OUTPUT_DIR}/stage3/standard_ports.gnmap" ]; then
        OPEN_PORT_COUNT=$(grep -c "open" "${OUTPUT_DIR}/stage3/standard_ports.gnmap" 2>/dev/null || echo "0")
    fi
    
    # 检查阶段 4 结果
    if [ -f "${OUTPUT_DIR}/stage4/final_report.md" ]; then
        VULN_HIGH=$(grep -c "^### " "${OUTPUT_DIR}/stage4/final_report.md" 2>/dev/null || echo "0")
    fi
    
elif [ "$ANALYSIS_TYPE" = "port_scan" ]; then
    # 端口扫描
    if [ -f "${OUTPUT_DIR}/port_scan.gnmap" ]; then
        OPEN_PORT_COUNT=$(grep -c "open" "${OUTPUT_DIR}/port_scan.gnmap" 2>/dev/null || echo "0")
    fi
    
elif [ "$ANALYSIS_TYPE" = "service_scan" ]; then
    # 服务探测
    if [ -f "${OUTPUT_DIR}/http_services.txt" ]; then
        ACCESSIBLE_URL_COUNT=$(grep -c "^\[200\]" "${OUTPUT_DIR}/http_services.txt" 2>/dev/null || echo "0")
    fi
fi

# 生成统一报告
cat > "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
# ${TITLE}

**目标**: $TARGET
**时间**: $(date +%Y-%m-%d\ %H:%M:%S)
**类型**: $ANALYSIS_TYPE

---

## 📊 统计摘要

EOF

if [ "$ANALYSIS_TYPE" = "full_stage" ] || [ "$ANALYSIS_TYPE" = "quick_analysis" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
### 阶段 1: 子域名收集
- **发现**: $SUB_COUNT 个子域名

### 阶段 2: 服务探测
- **可访问**: $ACCESSIBLE_URL_COUNT 个 URL

### 阶段 3: 端口扫描
- **开放端口**: $OPEN_PORT_COUNT 个

### 阶段 4: 深度分析
- **高风险问题**: $VULN_HIGH 个

---

EOF
elif [ "$ANALYSIS_TYPE" = "port_scan" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
### 端口扫描结果
- **开放端口**: $OPEN_PORT_COUNT 个

---

EOF
elif [ "$ANALYSIS_TYPE" = "service_scan" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
### 服务探测结果
- **可访问服务**: $ACCESSIBLE_URL_COUNT 个

---
EOF
fi

# 添加文件清单
cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
## 📁 输出文件清单

EOF

# 列出所有文件
find "$OUTPUT_DIR" -type f ! -name "ANALYSIS_REPORT.md" | sort | while read -r file; do
    size=$(wc -c < "$file" 2>/dev/null || echo "0")
    echo "- $(basename "$file") ($size bytes)"
done | head -20

if [ $(find "$OUTPUT_DIR" -type f ! -name "ANALYSIS_REPORT.md" 2>/dev/null | wc -l) -gt 20 ]; then
    echo "- ... 还有其他文件"
fi

# 添加重点文件说明
cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF

## 🎯 重点文件说明

EOF

# 根据分析类型添加重点文件
if [ "$ANALYSIS_TYPE" = "full_stage" ] || [ "$ANALYSIS_TYPE" = "quick_analysis" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
- **stage4/final_report.md** - 最终深度分析报告（包含所有发现）
- **stage2/http_accessible_urls.txt** - 可访问的 URL 列表
- **stage3/web_ips.txt** - Web 服务 IP 列表
- **stage3/all_accessible_urls.txt** - 所有可访问的 URL（汇总）
- **ERROR_ANALYSIS.md** - 错误详情分析（如果有）
- **ERROR_IMPROVEMENT.md** - 错误改进结果（如果有）

EOF
elif [ "$ANALYSIS_TYPE" = "port_scan" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
- **port_scan.gnmap** - 端口扫描详细结果
- **web_ips.txt** - Web 服务 IP 列表
- **all_ips_unique.txt** - 所有发现的 IP

EOF
elif [ "$ANALYSIS_TYPE" = "service_scan" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
- **http_services.txt** - HTTP 扫描结果
- **http_accessible_urls.txt** - 可访问的 URL 列表
- **resolved_ips.txt** - 解析的 IP 列表
- **http_access_improvement.txt** - 连接改进报告（如果有）

EOF
fi

# 添加下一步建议
cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF

## 🚀 下一步建议

EOF

# 根据分析类型添加下一步建议
if [ "$ANALYSIS_TYPE" = "full_stage" ] || [ "$ANALYSIS_TYPE" = "quick_analysis" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
### 1. 查看最终报告
\`\`\`cat stage4/final_report.md\`\`\`

### 2. 测试可访问的 URL
\`\`\`for url in \$(cat stage2/http_accessible_urls.txt | head -10); do
    echo "测试: \$url"
    curl -I "\$url" | head -5
done\`\`\`

### 3. 进行漏洞验证
\`\`\`cat stage4/vulnerability_analysis.txt | grep '^###' | head -10\`\`\`

### 4. 查看 Web 服务 IP
\`\`\`cat stage3/web_ips.txt\`\`\`

EOF

elif [ "$ANALYSIS_TYPE" = "port_scan" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
### 1. Web 服务扫描
\`\`\`nmap -iL web_ips.txt -p 80,443,8080,8443 -T4 --open -oG port_scan.gnmap\`\`\`

### 2. 端口服务分析
\`\`\`nmap -sV -sC <port> <ip>\`\`\`

EOF

elif [ "$ANALYSIS_TYPE" = "service_scan" ]; then
    cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF
### 1. 深度分析
\`\`\`python3 core/jsfind.py <url>\`\`\`

### 2. 端口扫描
\`\`\`nmap -iL resolved_ips.txt -p 80,443,8080,8443 -T4 --open\`\`\`

### 3. 继续完整流程
\`\`\`./scripts/stage3_port_scan_hybrid.sh <domain>\`\`\`

EOF
fi

# 添加生成时间
cat >> "${OUTPUT_DIR}/ANALYSIS_REPORT.md" << EOF

---

**生成时间**: $(date +%Y-%m-%d\ %H:%M:%S)
**生成工具**: 小牛的 SRC 信息收集技能 v2.1 🦞

---

_自动生成 - 快速定位分析结果！🦞_
EOF

echo -e "${GREEN}[+] 统一报告已生成: ${OUTPUT_DIR}/ANALYSIS_REPORT.md${NC}"
echo -e "${GREEN}[+] 报告包含: 统计摘要 + 文件清单 + 下一步建议${NC}"

# 显示报告摘要
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 分析结果摘要${NC}"
echo -e "${BLUE}========================================${NC}"

if [ "$ANALYSIS_TYPE" = "full_stage" ] || [ "$ANALYSIS_TYPE" = "quick_analysis" ]; then
    echo -e "  发现子域名: $SUB_COUNT 个"
    echo -e "  可访问 URL: $ACCESSIBLE_URL_COUNT 个"
    echo -e "  开放端口: $OPEN_PORT_COUNT 个"
    echo -e "  高风险问题: $VULN_HIGH 个"
    echo ""
    echo -e "${YELLOW}[*] 重点文件:${NC}"
    if [ -f "${OUTPUT_DIR}/stage4/final_report.md" ]; then
        echo "  - 阶段 4 最终报告: ${OUTPUT_DIR}/stage4/final_report.md"
    fi
    if [ -f "${OUTPUT_DIR}/stage2/http_accessible_urls.txt" ]; then
        echo "  - 可访问 URL: ${OUTPUT_DIR}/stage2/http_accessible_urls.txt"
    fi
    if [ -f "${OUTPUT_DIR}/stage3/all_accessible_urls.txt" ]; then
        echo "  - 所有可访问 URL: ${OUTPUT_DIR}/stage3/all_accessible_urls.txt"
    fi

elif [ "$ANALYSIS_TYPE" = "port_scan" ]; then
    echo -e "  开放端口: $OPEN_PORT_COUNT 个"
    echo ""
    echo -e "${YELLOW}[*] 重点文件:${NC}"
    if [ -f "${OUTPUT_DIR}/port_scan.gnmap" ]; then
        echo "  - 端口扫描结果: ${OUTPUT_DIR}/port_scan.gnmap"
    fi
    if [ -f "${OUTPUT_DIR}/web_ips.txt" ]; then
        echo "  - Web 服务 IP: ${OUTPUT_DIR}/web_ips.txt"
    fi

elif [ "$ANALYSIS_TYPE" = "service_scan" ]; then
    echo -e "  可访问服务: $ACCESSIBLE_URL_COUNT 个"
    echo ""
    echo -e "${YELLOW}[*] 重点文件:${NC}"
    if [ -f "${OUTPUT_DIR}/http_services.txt" ]; then
        echo "  - HTTP 扫描结果: ${OUTPUT_DIR}/http_services.txt"
    fi
    if [ -f "${OUTPUT_DIR}/http_accessible_urls.txt" ]; then
        echo "  - 可访问 URL: ${OUTPUT_DIR}/http_accessible_urls.txt"
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 报告位置: ${OUTPUT_DIR}/ANALYSIS_REPORT.md${NC}"
echo -e "${BLUE}========================================${NC}"

# 显示下一步建议
echo ""
echo -e "${YELLOW}[!] 下一步建议:${NC}"
echo "    1. 查看完整报告: cat ${OUTPUT_DIR}/ANALYSIS_REPORT.md"
echo "    2. 查看文件清单: 查看报告中的 '输出文件清单' 部分"
echo "    3. 按照报告中的 '下一步建议' 继续操作"

---

echo -e "\n${GREEN}[+] 分析完成！${NC}"
echo -e "${GREEN}[+] 结果文档已生成${NC}"
echo ""
echo -e "${YELLOW}[*] 报告位置: ${OUTPUT_DIR}/ANALYSIS_REPORT.md${NC}"
echo -e "${YELLOW}[*] 文件清单: 查看报告中的 '输出文件清单' 部分${NC}"
echo -e "${YELLOW}[*] 下一步: 按照报告中的 '下一步建议' 继续操作${NC}"
echo ""

# 完成标志
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 感谢使用小牛的 SRC 信息收集技能 v2.1 🦞${NC}"
echo -e "${BLUE}========================================${NC}"
