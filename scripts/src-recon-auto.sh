#!/bin/bash
# SRC 自动化信息收集脚本
# 使用方法: ./src-recon-auto.sh example.com

set -e

TARGET=$1
OUTPUT_DIR="recon/$TARGET"
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

# 1. 子域名枚举
echo -e "\n${YELLOW}[*] 阶段 1: 子域名枚举${NC}"
if command -v subfinder &> /dev/null; then
    subfinder -d $TARGET -o $OUTPUT_DIR/subs.txt 2>/dev/null
    SUB_COUNT=$(wc -l < $OUTPUT_DIR/subs.txt)
    echo -e "${GREEN}[+] 发现 $SUB_COUNT 个子域名${NC}"
else
    echo -e "${RED}[-] subfinder 未安装，跳过子域名枚举${NC}"
fi

# 2. 存活检测
echo -e "\n${YELLOW}[*] 阶段 2: 存活检测${NC}"
if [ -f "$OUTPUT_DIR/subs.txt" ]; then
    if command -v httpx &> /dev/null; then
        cat $OUTPUT_DIR/subs.txt | httpx -status-code -title -silent -threads 50 > $OUTPUT_DIR/alive.txt
        ALIVE_COUNT=$(wc -l < $OUTPUT_DIR/alive.txt)
        echo -e "${GREEN}[+] 存活资产: $ALIVE_COUNT${NC}"
    else
        echo -e "${RED}[-] httpx 未安装，跳过存活检测${NC}"
    fi
fi

# 3. 端口扫描与 HTTP 服务探测
echo -e "\n${YELLOW}[*] 阶段 3: 端口扫描与 HTTP 服务探测${NC}"

# 选择扫描模式
SCAN_MODE="${SCAN_MODE:-fast}"  # 默认快速扫描
echo -e "${YELLOW}[*] 扫描模式: $SCAN_MODE${NC}"

if command -v nmap &> /dev/null; then
    if [ -f "$OUTPUT_DIR/all_subs.txt" ]; then
        if [ "$SCAN_MODE" = "full" ]; then
            echo -e "${YELLOW}[*] 全端口扫描模式（1-65535）...${NC}"
            nmap -iL $OUTPUT_DIR/all_subs.txt \
                -p- \
                -T4 \
                --open \
                -oG $OUTPUT_DIR/port_scan_full.gnmap 2>/dev/null
            PORT_COUNT=$(grep -c "open" $OUTPUT_DIR/port_scan_full.gnmap || echo "0")
            echo -e "${GREEN}[+] 开放端口: $PORT_COUNT${NC}"
            echo -e "${YELLOW}[!] 全端口扫描完成，耗时可能较长${NC}"
        else
            echo -e "${YELLOW}[*] 快速扫描模式（Top 1000 + 常见 Web 端口）...${NC}"
            nmap -iL $OUTPUT_DIR/all_subs.txt \
                -p 80,443,8080,8443,3000,5000,8888,9000,9443 \
                --top-ports 1000 \
                -T4 \
                --open \
                -oG $OUTPUT_DIR/port_scan.gnmap 2>/dev/null
            PORT_COUNT=$(grep -c "open" $OUTPUT_DIR/port_scan.gnmap || echo "0")
            echo -e "${GREEN}[+] 开放端口: $PORT_COUNT${NC}"
        fi

        # HTTP/HTTPS 服务探测
        echo -e "${YELLOW}[*] 探测 HTTP/HTTPS 服务${NC}"
        if command -v httpx &> /dev/null; then
            cat $OUTPUT_DIR/all_subs.txt | httpx \
                -status-code \
                -title \
                -tech-detect \
                -waf-detect \
                -silent \
                -threads 50 \
                -retries 2 \
                -timeout 10 \
                -o $OUTPUT_DIR/http_services.txt
            HTTP_COUNT=$(wc -l < $OUTPUT_DIR/http_services.txt)
            echo -e "${GREEN}[+] 发现 HTTP 服务: $HTTP_COUNT${NC}"
        else
            echo -e "${RED}[-] httpx 未安装，跳过 HTTP 探测${NC}"
        fi
    fi
fi

# 4. HTTP 服务详细扫描
echo -e "\n${YELLOW}[*] 阶段 4: HTTP 服务详细扫描${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$OUTPUT_DIR/http_services.txt" ]; then
    # 提取 URL 列表
    awk '{print $1}' $OUTPUT_DIR/http_services.txt > $OUTPUT_DIR/http_urls.txt

    # 使用 Python 脚本详细扫描
    if command -v python3 &> /dev/null; then
        python3 $SCRIPT_DIR/http_scanner.py $OUTPUT_DIR/http_urls.txt $OUTPUT_DIR/http_status_report.txt 2>/dev/null || true
        echo -e "${GREEN}[+] HTTP 服务扫描完成${NC}"
    else
        echo -e "${RED}[-] Python3 未安装，跳过详细扫描${NC}"
    fi

    # 按状态码分类
    grep -E "\[200\]" $OUTPUT_DIR/http_services.txt > $OUTPUT_DIR/status_200.txt 2>/dev/null || true
    grep -E "\[30[0-9]\]" $OUTPUT_DIR/http_services.txt > $OUTPUT_DIR/status_3xx.txt 2>/dev/null || true
    grep -E "\[40[0-9]\]" $OUTPUT_DIR/http_services.txt > $OUTPUT_DIR/status_4xx.txt 2>/dev/null || true
    grep -E "\[50[0-9]\]" $OUTPUT_DIR/http_services.txt > $OUTPUT_DIR/status_5xx.txt 2>/dev/null || true

    # 统计
    COUNT_200=$(wc -l < $OUTPUT_DIR/status_200.txt 2>/dev/null || echo "0")
    COUNT_3XX=$(wc -l < $OUTPUT_DIR/status_3xx.txt 2>/dev/null || echo "0")
    COUNT_4XX=$(wc -l < $OUTPUT_DIR/status_4xx.txt 2>/dev/null || echo "0")
    COUNT_5XX=$(wc -l < $OUTPUT_DIR/status_5xx.txt 2>/dev/null || echo "0")

    echo -e "${GREEN}[+] 状态码统计: 200:$COUNT_200, 3xx:$COUNT_3XX, 4xx:$COUNT_4XX, 5xx:$COUNT_5XX${NC}"
fi

# 4.5 JS 路径提取（新增 - 所有 HTTP 服务）
echo -e "\n${YELLOW}[*] 阶段 4.5: JS 路径提取（所有 HTTP 服务）${NC}"
if [ -f "$OUTPUT_DIR/http_urls.txt" ]; then
    if command -v python3 &> /dev/null; then
        echo "[*] 正在使用 JS Path Extractor 提取路径..."
        echo "    [*] 即使是空白页面或 400 状态，只要能访问 JS 文件就进行提取..."

        # 对所有 HTTP 服务提取路径
        python3 $SCRIPT_DIR/js_path_extractor.py $OUTPUT_DIR/http_urls.txt $OUTPUT_DIR/extracted_paths.txt 2>/dev/null || true

        # 检查提取结果
        if [ -f "$OUTPUT_DIR/extracted_paths.txt" ]; then
            EXTRACTED_COUNT=$(wc -l < $OUTPUT_DIR/extracted_paths.txt 2>/dev/null || echo "0")
            echo -e "${GREEN}[+] 提取路径: $EXTRACTED_COUNT 个${NC}"
        fi
    else
        echo -e "${RED}[-] Python3 未安装，跳过 JS 路径提取${NC}"
    fi
fi

# 5. JS 文件分析与 API 端点发现
echo -e "\n${YELLOW}[*] 阶段 5: JS 文件分析与 API 端点发现${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$OUTPUT_DIR/status_200.txt" ]; then
    # 提取 200 状态的站点 URL
    cat $OUTPUT_DIR/status_200.txt | awk '{print $1}' > $OUTPUT_DIR/sites_for_jsfind.txt

    if command -v python3 &> /dev/null; then
        echo "[*] 正在使用 JSFind 分析站点..."

        # 使用 jsfind.py 分析 JS 文件
        python3 $SCRIPT_DIR/jsfind.py $OUTPUT_DIR/sites_for_jsfind.txt $OUTPUT_DIR/jsfind_results 2>/dev/null || true

        if [ -f "$OUTPUT_DIR/jsfind_results/api_endpoints.txt" ]; then
            API_COUNT=$(wc -l < $OUTPUT_DIR/jsfind_results/api_endpoints.txt)
            echo -e "${GREEN}[+] 发现 $API_COUNT 个 API 端点${NC}"
        fi

        if [ -f "$OUTPUT_DIR/jsfind_results/verified_endpoints.txt" ]; then
            VERIFIED_COUNT=$(grep -c "^-" $OUTPUT_DIR/jsfind_results/verified_endpoints.txt 2>/dev/null || echo "0")
            echo -e "${GREEN}[+] 验证可访问: $VERIFIED_COUNT 个端点${NC}"
        fi

        if [ -f "$OUTPUT_DIR/jsfind_results/accessible_chunks.txt" ]; then
            CHUNK_COUNT=$(wc -l < $OUTPUT_DIR/jsfind_results/accessible_chunks.txt)
            echo -e "${GREEN}[+] 发现可访问 chunk: $CHUNK_COUNT 个${NC}"
        fi
    else
        echo -e "${RED}[-] Python3 未安装，跳过 JS 分析${NC}"
    fi
else
    echo -e "${RED}[-] 未发现 200 状态站点，跳过 JS 分析${NC}"
fi

# 5.5 Vue.js 应用检测（新增）
echo -e "\n${YELLOW}[*] 阶段 5.5: Vue.js 应用安全检测${NC}"
if [ -f "$OUTPUT_DIR/status_200.txt" ]; then
    if command -v python3 &> /dev/null; then
        echo "[*] 正在使用 VueCrack 检测 Vue.js 应用..."

        # 使用 vuecrack.py 检测 Vue.js 应用
        python3 $SCRIPT_DIR/vuecrack.py $OUTPUT_DIR/sites_for_jsfind.txt $OUTPUT_DIR/vuecrack_report.txt 2>/dev/null || true

        # 检查是否发现 Vue.js 应用
        if grep -q "Vue.js 检测: 是" $OUTPUT_DIR/vuecrack_report.txt 2>/dev/null; then
            VUE_COUNT=$(grep -c "✅ 可访问路由" $OUTPUT_DIR/vuecrack_report.txt || echo "0")
            echo -e "${GREEN}[+] 发现 Vue.js 应用，可访问路由: $VUE_COUNT${NC}"
        else
            echo -e "${YELLOW}[*] 未发现 Vue.js 应用${NC}"
        fi
    else
        echo -e "${RED}[-] Python3 未安装，跳过 Vue.js 检测${NC}"
    fi
else
    echo -e "${YELLOW}[*] 无 200 状态站点，跳过 Vue.js 检测${NC}"
fi

# 6. 传统敏感端点扫描
echo -e "\n${YELLOW}[*] 阶段 6: 敏感端点扫描${NC}"
if command -v gobuster &> /dev/null; then
    if [ -f "$OUTPUT_DIR/status_200.txt" ]; then
        WORDLIST="$SCRIPT_DIR/dirs.txt"

        # 只扫描前 5 个 200 状态的站点
        cat $OUTPUT_DIR/status_200.txt | head -5 | awk '{print $1}' | while read url; do
            echo "    扫描: $url"
            gobuster dir -u $url -w $WORDLIST -t 30 -x php,html,js,zip,bak -o $OUTPUT_DIR/dirs_${url##//}.txt 2>/dev/null || true
        done
        echo -e "${GREEN}[+] 端点扫描完成${NC}"
    else
        echo -e "${RED}[-] 未发现 200 状态站点，跳过端点扫描${NC}"
    fi
fi

# 6.5 Spring Boot Actuator 检测（新增）
echo -e "\n${YELLOW}[*] 阶段 6.5: Spring Boot Actuator 检测${NC}"
if [ -f "$OUTPUT_DIR/status_200.txt" ]; then
    if command -v python3 &> /dev/null; then
        echo "[*] 正在使用 Actuator Scanner 检测 Spring Boot..."

        # 使用 actuator_scanner.py 检测 Spring Boot Actuator
        python3 $SCRIPT_DIR/actuator_scanner.py $OUTPUT_DIR/sites_for_jsfind.txt $OUTPUT_DIR/actuator_report.txt 2>/dev/null || true

        # 检查是否发现 Spring Boot Actuator
        if grep -q "Actuator 检测: 是" $OUTPUT_DIR/actuator_report.txt 2>/dev/null; then
            ACTUATOR_COUNT=$(grep -c "^- \[200\]" $OUTPUT_DIR/actuator_report.txt || echo "0")
            VULN_COUNT=$(grep -c "### " $OUTPUT_DIR/actuator_report.txt || echo "0")
            echo -e "${GREEN}[+] 发现 Spring Boot Actuator，可访问端点: $ACTUATOR_COUNT${NC}"
            if [ "$VULN_COUNT" -gt 0 ]; then
                echo -e "${RED}[!] 发现漏洞: $VULN_COUNT 个${NC}"
            fi
        else
            echo -e "${YELLOW}[*] 未发现 Spring Boot Actuator${NC}"
        fi
    else
        echo -e "${RED}[-] Python3 未安装，跳过 Actuator 检测${NC}"
    fi
else
    echo -e "${YELLOW}[*] 无 200 状态站点，跳过 Actuator 检测${NC}"
fi

# 7. 生成报告
echo -e "\n${YELLOW}[*] 生成报告${NC}"

# 统计 JS 发现结果
API_ENDPOINTS_COUNT=$(wc -l < $OUTPUT_DIR/jsfind_results/api_endpoints.txt 2>/dev/null || echo "0")
PATHS_COUNT=$(wc -l < $OUTPUT_DIR/jsfind_results/paths.txt 2>/dev/null || echo "0")
SECRETS_COUNT=$(wc -l < $OUTPUT_DIR/jsfind_results/secrets.txt 2>/dev/null || echo "0")
VERIFIED_ENDPOINTS_COUNT=$(grep -c "^-" $OUTPUT_DIR/jsfind_results/verified_endpoints.txt 2>/dev/null || echo "0")
ACCESSIBLE_CHUNKS_COUNT=$(wc -l < $OUTPUT_DIR/jsfind_results/accessible_chunks.txt 2>/dev/null || echo "0")

# 统计 JS 路径提取结果（新增）
EXTRACTED_PATHS_COUNT=$(wc -l < $OUTPUT_DIR/extracted_paths.txt 2>/dev/null || echo "0")
JS_FILES_SCANNED_COUNT=$(wc -l < $OUTPUT_DIR/js_files_scanned.txt 2>/dev/null || echo "0")

# 统计 Vue.js 发现结果
VUE_DETECTED="否"
if grep -q "Vue.js 检测: 是" $OUTPUT_DIR/vuecrack_report.txt 2>/dev/null; then
    VUE_DETECTED="是"
fi
VUE_ACCESSIBLE_COUNT=$(grep -c "^- \[200\]" $OUTPUT_DIR/vuecrack_report.txt 2>/dev/null || echo "0")

# 统计 Spring Boot Actuator 发现结果
ACTUATOR_DETECTED="否"
if grep -q "Actuator 检测: 是" $OUTPUT_DIR/actuator_report.txt 2>/dev/null; then
    ACTUATOR_DETECTED="是"
fi
ACTUATOR_ACCESSIBLE_COUNT=$(grep -c "^- \[200\]" $OUTPUT_DIR/actuator_report.txt 2>/dev/null || echo "0")
ACTUATOR_VULN_COUNT=$(grep -c "### " $OUTPUT_DIR/actuator_report.txt 2>/dev/null || echo "0")

# 确定使用的扫描结果文件
if [ -f "$OUTPUT_DIR/port_scan_full.gnmap" ]; then
    PORT_SCAN_FILE="$OUTPUT_DIR/port_scan_full.gnmap"
    SCAN_MODE_USED="全端口扫描 (1-65535)"
else
    PORT_SCAN_FILE="$OUTPUT_DIR/port_scan.gnmap"
    SCAN_MODE_USED="快速扫描 (Top 1000 + 常见 Web 端口)"
fi

cat > $REPORT_FILE << EOF
# SRC 信息收集报告

**目标**: $TARGET
**时间**: $(date +%Y-%m-%d\ %H:%M:%S)
**扫描模式**: $SCAN_MODE_USED
**工具**: subfinder, httpx, nmap, nuclei, gobuster, http_scanner, jsfind

---

## 📊 统计信息

| 项目 | 数量 |
|------|------|
| 子域名 | $(wc -l < $OUTPUT_DIR/all_subs.txt 2>/dev/null || echo "0") |
| 存活资产 | $(wc -l < $OUTPUT_DIR/alive.txt 2>/dev/null || echo "0") |
| HTTP/HTTPS 服务 | $(wc -l < $OUTPUT_DIR/http_services.txt 2>/dev/null || echo "0") |
| 开放端口 | $(grep -c "open" $PORT_SCAN_FILE 2>/dev/null || echo "0") |
| API 端点（JS 分析）| $API_ENDPOINTS_COUNT |
| 验证可访问端点 | $VERIFIED_ENDPOINTS_COUNT |
| 可访问 Chunk 文件 | $ACCESSIBLE_CHUNKS_COUNT |
| **提取的路径（所有 HTTP 服务）** | $EXTRACTED_PATHS_COUNT |
| **扫描的 JS 文件** | $JS_FILES_SCANNED_COUNT |
| Vue.js 应用 | $VUE_DETECTED |
| Vue 可访问路由 | $VUE_ACCESSIBLE_COUNT |
| Spring Boot Actuator | $ACTUATOR_DETECTED |
| Actuator 可访问端点 | $ACTUATOR_ACCESSIBLE_COUNT |
| Actuator 漏洞 | $ACTUATOR_VULN_COUNT |

---

## 📈 HTTP 状态码统计

| 状态码 | 数量 | 说明 |
|--------|------|------|
| 200 OK | $COUNT_200 | 成功响应 |
| 3xx 重定向 | $COUNT_3XX | 重定向 |
| 4xx 客户端错误 | $COUNT_4XX | 客户端错误 |
| 5xx 服务器错误 | $COUNT_5XX | 服务器错误 |

---

## 🔍 JS 文件分析结果

### 发现的 API 端点

\`\`\`
$(head -20 $OUTPUT_DIR/jsfind_results/api_endpoints.txt 2>/dev/null || echo "无数据")
$(if [ $(wc -l < $OUTPUT_DIR/jsfind_results/api_endpoints.txt 2>/dev/null || echo "0") -gt 20 ]; then
    echo "... 还有 $(($(wc -l < $OUTPUT_DIR/jsfind_results/api_endpoints.txt) - 20)) 个"
fi)
\`\`\`

### 验证可访问的端点

\`\`\`
$(cat $OUTPUT_DIR/jsfind_results/verified_endpoints.txt 2>/dev/null | grep "^-" | head -20 || echo "无数据")
$(if [ $VERIFIED_ENDPOINTS_COUNT -gt 20 ]; then
    echo "... 还有 $(($VERIFIED_ENDPOINTS_COUNT - 20)) 个"
fi)
\`\`\`

---

## 🌐 HTTP/HTTPS 服务详情

### ✅ 200 OK 站点

\`\`\`
$(cat $OUTPUT_DIR/status_200.txt 2>/dev/null | head -20 || echo "无数据")
\`\`\`

### ⚠️ 异常状态站点

#### 3xx 重定向
\`\`\`
$(cat $OUTPUT_DIR/status_3xx.txt 2>/dev/null | head -10 || echo "无数据")
\`\`\`

#### 4xx 客户端错误
\`\`\`
$(cat $OUTPUT_DIR/status_4xx.txt 2>/dev/null | head -10 || echo "无数据")
\`\`\`

#### 5xx 服务器错误
\`\`\`
$(cat $OUTPUT_DIR/status_5xx.txt 2>/dev/null | head -10 || echo "无数据")
\`\`\`

---

## 🔌 开放端口

扫描模式: $SCAN_MODE_USED

\`\`\`
$(grep "open" $PORT_SCAN_FILE 2>/dev/null || echo "无数据")
\`\`\`

---

## 🎯 高价值测试点

基于 JS 分析和目录扫描发现的端点：

EOF

# 添加验证可访问的 API 端点
if [ -f "$OUTPUT_DIR/jsfind_results/verified_endpoints.txt" ]; then
    echo "### JS 分析发现的可访问端点" >> $REPORT_FILE
    cat $OUTPUT_DIR/jsfind_results/verified_endpoints.txt | grep "^-" | head -10 >> $REPORT_FILE
    echo "" >> $REPORT_FILE
fi

# 添加传统敏感端点
if [ -f "$OUTPUT_DIR/status_200.txt" ]; then
    echo "### 常见敏感端点" >> $REPORT_FILE
    cat $OUTPUT_DIR/status_200.txt | awk '{print $1}' | head -5 | while read url; do
        echo "- ${url}/admin"
        echo "- ${url}/api"
        echo "- ${url}/graphql"
        echo "- ${url}/backup.zip"
        echo "- ${url}/.git"
    done >> $REPORT_FILE
    echo "" >> $REPORT_FILE
fi

cat >> $REPORT_FILE << EOF

---

## 📁 敏感端点发现（目录扫描）

$(for file in $OUTPUT_DIR/dirs_*.txt; do
    if [ -f "$file" ]; then
        echo -e "\n#### $(basename $file)"
        echo "\`\`\`"
        cat "$file" | grep "Status: 200" | tail -10
        echo "\`\`\`"
    fi
done 2>/dev/null || echo "无数据")

---

## 📋 详细报告

- **HTTP 扫描报告**: \`http_status_report.txt\`
- **JS 路径提取（所有 HTTP 服务）**: \`extracted_paths.txt\` ← 新增
  - 从所有 HTTP 服务的 JS 文件中提取的路径
  - 即使是空白页面或 400 状态也提取
- **扫描的 JS 文件**: \`js_files_scanned.txt\` ← 新增
- **JS 分析结果**: \`jsfind_results/\`
  - \`api_endpoints.txt\` - 发现的 API 端点
  - \`paths.txt\` - 发现的路径
  - \`secrets.txt\` - 敏感信息
  - \`verified_endpoints.txt\` - 验证可访问的端点
  - \`accessible_chunks.txt\` - 可访问的 chunk 文件
- **Vue.js 扫描**: \`vuecrack_report.txt\`
  - Vue.js 应用检测结果
  - 可访问路由列表
  - 需要认证的路由
- **Spring Boot Actuator**: \`actuator_report.txt\`
  - Actuator 框架检测结果
  - 可访问端点列表
  - 漏洞列表（未授权访问、敏感信息泄露）
- **端口扫描**: \`$(basename $PORT_SCAN_FILE)\`
- **路径爆破**: \`path_bruteforce_combined.txt\` ← 新增
- **智能分析**: \`vulnerability_analysis.txt\` ← 新增

---

**生成工具**: 小牛的 SRC 信息收集技能 🦞
EOF

echo -e "${GREEN}[+] 报告已生成: $REPORT_FILE${NC}"

echo -e "\n${GREEN}[+] 信息收集完成！${NC}"
echo -e "${YELLOW}[+] 结果目录: $OUTPUT_DIR${NC}"
echo -e "${YELLOW}[+] 查看报告: cat $REPORT_FILE${NC}"
