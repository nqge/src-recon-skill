---
name: src-recon
description: SRC 众测平台信息收集技能 - 自动化收集目标资产、子域名、端口、漏洞指纹。用于：(1) SRC 项目资产收集，(2) 子域名枚举，(3) 端口服务识别，(4) 漏洞面发现，(5) 资产关联分析。触发词：SRC、众测、信息收集、资产收集、子域名、端口扫描。
---

# SRC 众测信息收集技能

SRC（Security Response Center）众测平台的自动化资产收集与漏洞面发现工具包。

## 🎯 核心能力

1. **资产收集** - 主域名、子域名、IP 段、CDN 识别
2. **子域名枚举** - 被动收集、主动爆破、证书透明度
3. **端口扫描** - 服务识别、版本探测、资产存活
4. **指纹识别** - Web 框架、CMS、WAF、中间件
5. **漏洞面发现** - 敏感端点、API 接口、未授权页面
6. **资产关联** - 同 IP 站点、同备案、证书关联

## 🛠️ 工具清单

### Python 工具（8 个）

#### 1. fofa_subs.py - FOFA 子域名收集
```bash
# 使用 FOFA API 进行大规模子域名收集
python3 fofa_subs.py example.com

# 输出：
# fofa_subs.txt - 收集的子域名列表
# fofa_results.json - 详细结果（JSON 格式）

# 特点：
# - 使用 FOFA API（需要配置 FOFA_EMAIL 和 FOFA_KEY）
# - 支持大规模查询
# - 自动去重和排序
```

#### 2. http_scanner.py - HTTP/HTTPS 服务扫描
```bash
# 批量扫描 HTTP/HTTPS 服务
python3 http_scanner.py all_subs.txt http_services.txt

# 输出：
# http_services.txt - HTTP 服务列表（带状态码和标题）
# status_200.txt - 200 OK 的服务
# status_3xx.txt - 重定向的服务
# status_4xx.txt - 客户端错误
# status_5xx.txt - 服务器错误

# 特点：
# - 并发扫描（默认 15 线程）
# - 记录状态码、标题、大小
# - 自动分类存储
```

#### 3. jsfind.py - JavaScript 文件分析
```bash
# 分析 JavaScript 文件，提取 API、路径、密钥
python3 jsfind.py https://example.com

# 输出：
# jsfind_results/api_endpoints.txt - 发现的 API 端点
# jsfind_results/paths.txt - 提取的路径
# jsfind_results/secrets.txt - 敏感信息（密钥、密码）
# jsfind_results/verified_endpoints.txt - 验证可访问的端点
# jsfind_results/accessible_chunks.txt - 可访问的 chunk 文件

# 特点：
# - 自动下载和分析 JS 文件
# - 提取 API 端点、路径、密钥
# - 验证可访问性
# - 提取并验证 chunk 文件
```

#### 4. vuecrack.py - Vue.js 应用检测
```bash
# 检测 Vue.js 应用并枚举路由
python3 vuecrack.py https://example.com

# 输出：
# vuecrack_report.txt - 检测报告

# 特点：
# - 自动检测 Vue.js 应用
# - 枚举所有路由
# - 检测未授权访问
# - 发现隐藏的路由端点
```

#### 5. actuator_scanner.py - Spring Boot Actuator 检测
```bash
# 检测 Spring Boot Actuator 端点
python3 actuator_scanner.py https://example.com

# 输出：
# actuator_report.txt - 检测报告

# 特点：
# - 检测 Actuator 暴露
# - 扫描常见端点（/env, /health, /info, /beans 等）
# - 检测未授权访问
# - 发现敏感信息泄露
```

#### 6. js_path_extractor.py - JS 路径提取（新增）
```bash
# 从所有 HTTP 服务提取路径（包括错误页面）
python3 js_path_extractor.py http_urls.txt extracted_paths.txt

# 输出：
# extracted_paths.txt - 提取的路径列表
# js_files_scanned.txt - 扫描的 JS 文件列表

# 特点：
# - 扫描所有 HTTP 服务（200/3xx/4xx/5xx）
# - 即使是空白页面也尝试提取
# - 从 JS 文件中提取路径模式
# - 适用于 SPA 应用

# 为什么扫描 4xx/5xx？
# - SPA 可能返回空白页面但加载 JS
# - 错误页面可能引用 JS 文件
# - API 路径可能隐藏在 JS 中
```

#### 7. path_bruteforcer.py - 路径爆破测试（新增）
```bash
# 将提取的路径拼接到目录结构中进行测试
python3 path_bruteforcer.py https://example.com extracted_paths.txt

# 输出：
# path_bruteforce_report.txt - 测试报告

# 特点：
# - 自动发现目录结构
# - 将路径拼接到目录
# - 并发测试（默认 15 线程）
# - 记录状态码、大小、Content-Type
# - 识别未授权访问

# 实战价值：
# - /api/internal/debug - 未授权访问
# - /admin/config - 配置泄露
# - /management/graphql - 隐藏端点
```

#### 8. vulnerability_analyzer.py - 智能漏洞分析（新增）
```bash
# 基于收集的信息进行智能分析
python3 vulnerability_analyzer.py scan_results.json vulnerability_analysis.txt

# 输出：
# vulnerability_analysis.txt - 分析报告

# 特点：
# - 多维度风险分析（路径、技术、状态码、响应）
# - 风险评分系统（HIGH/MEDIUM/LOW/INFO）
# - 自动生成洞察和建议
# - 优先级排序

# 分析维度：
# - 路径模式：/admin, /config, /debug
# - 技术风险：/actuator, /graphql
# - 状态码：200 OK 风险更高
# - 响应特征：JSON、大文件、敏感关键字
```

### 子域名枚举

#### FOFA 搜索引擎（推荐）
```bash
# 前置条件：配置 FOFA API Key
export FOFA_EMAIL="your_email@example.com"  # FOFA 账户邮箱
export FOFA_KEY="your_fofa_api_key"         # FOFA API Key

# 使用 FOFA 搜索子域名
# 语法：domain="example.com"
curl -s "https://fofa.info/api/v1/search/all?email=${FOFA_EMAIL}&key=${FOFA_KEY}&qbase64=$(echo -n 'domain="example.com"' | base64)" | jq -r '.results[].host' 2>/dev/null | grep -oE '[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | sort -u > fofa_subs.txt

# Python 脚本方式（推荐）
python3 << EOF
import base64
import requests
import os

fofa_email = os.getenv('FOFA_EMAIL')
fofa_key = os.getenv('FOFA_KEY')
target = "example.com"  # 修改为目标域名

if not fofa_email or not fofa_key:
    print("[-] 请设置 FOFA_EMAIL 和 FOFA_KEY 环境变量")
    exit(1)

query = f'domain="{target}"'
query_base64 = base64.b64encode(query.encode()).decode()

url = f"https://fofa.info/api/v1/search/all?email={fofa_email}&key={fofa_key}&qbase64={query_base64}&size=1000"

try:
    resp = requests.get(url, timeout=30)
    data = resp.json()
    
    if data.get('error'):
        print(f"[-] FOFA API 错误: {data['errmsg']}")
        exit(1)
    
    if not data.get('results'):
        print("[-] 未找到结果")
        exit(1)
    
    subdomains = set()
    for result in data['results']:
        host = result[0]  # host 字段
        # 提取子域名
        import re
        subs = re.findall(r'[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', host)
        subdomains.update(subs)
    
    with open('fofa_subs.txt', 'w') as f:
        for sub in sorted(subdomains):
            f.write(sub + '\n')
    
    print(f"[+] FOFA 发现 {len(subdomains)} 个子域名")
    print(f"[+] 结果保存到: fofa_subs.txt")
    
except Exception as e:
    print(f"[-] 错误: {e}")
    exit(1)
EOF

# 查看结果
cat fofa_subs.txt
```

#### 被动 DNS 收集
```bash
# 被动收集（推荐，快速不触发 WAF）
subfinder -d $TARGET -o subs.txt

# 证书透明度查询
curl -s "https://crt.sh/?q=%.${TARGET}&output=json" | jq -r '.[].name_value' | sort -u > crt_subs.txt

# 主动爆破（谨慎使用）
puredns brute $TARGET wordlists/subdomains.txt -resolvers resolvers.txt

# 综合工具（多源聚合）
python3 one_for_all.py --target $TARGET
```

#### 合并所有来源
```bash
# 合并所有子域名来源并去重
cat fofa_subs.txt subs.txt crt_subs.txt 2>/dev/null | sort -u > all_subs.txt
echo "[+] 总共发现 $(wc -l < all_subs.txt) 个子域名"
```

### 端口扫描

#### 扫描模式选择

```bash
# 设置扫描模式
export SCAN_MODE="fast"  # "fast" 或 "full"

# 模式说明：
# - fast: 快速扫描（默认） - Top 1000 端口 + 常见 Web 端口
# - full: 全端口扫描 - 扫描 1-65535 全部端口（耗时较长）
```

#### 快速扫描（默认）

```bash
# 扫描常见 Web 端口 + Top 1000 端口
nmap -iL all_subs.txt \
    -p 80,443,8080,8443,3000,5000,8888,9000,9443 \
    --top-ports 1000 \
    -T4 \
    --open \
    -oG port_scan.gnmap

echo "[+] 快速扫描完成，扫描端口: Top 1000 + 常见 Web 端口"
```

#### 全端口扫描（可选）

```bash
# 扫描全部 1-65535 端口
nmap -iL all_subs.txt \
    -p- \
    -T4 \
    --open \
    -oG port_scan_full.gnmap

echo "[+] 全端口扫描完成，扫描端口: 1-65535"
echo "[!] 注意：全端口扫描耗时较长（可能需要数小时）"
```

#### 服务版本识别

```bash
# 对发现的主机进行服务版本识别
nmap -sV -sC -p- $TARGET -oA version_scan
```

#### UDP 端口扫描（可选）

```bash
# UDP 端口扫描（慢）
nmap -sU --top-port 100 <target> -oA udp_scan
```

#### 大规模扫描（可选）

```bash
# 使用 masscan 进行大规模快速扫描
masscan -p1-65535 <target> --rate=1000 -oL masscan.txt
```

### Web 指纹识别（增强版）
```bash
# httpx 批量指纹识别（推荐）
cat http_services.txt | httpx \
    -status-code \
    -title \
    -tech-detect \
    -waf-detect \
    -silent \
    -o fingerprint_with_status.txt

# 按状态码分类
echo "[*] 按状态码分类..."

# 200 OK
grep -E "\[200\]" http_services.txt | awk '{print $1, $2, $3}' > status_200.txt
echo "  200 OK: $(wc -l < status_200.txt)"

# 3xx 重定向
grep -E "\[30[0-9]\]" http_services.txt | awk '{print $1, $2, $3}' > status_3xx.txt
echo "  3xx 重定向: $(wc -l < status_3xx.txt)"

# 4xx 客户端错误
grep -E "\[40[0-9]\]" http_services.txt | awk '{print $1, $2, $3}' > status_4xx.txt
echo "  4xx 客户端错误: $(wc -l < status_4xx.txt)"

# 5xx 服务器错误
grep -E "\[50[0-9]\]" http_services.txt | awk '{print $1, $2, $3}' > status_5xx.txt
echo "  5xx 服务器错误: $(wc -l < status_5xx.txt)"

# 使用 nuclei 进行深度指纹识别
nuclei -l http_services.txt \
    -silent \
    -t ~/nuclei-templates/technologies/ \
    -o nuclei_tech.txt

# 使用 whatweb 进行详细分析（可选）
cat http_urls.txt | while read url; do
    whatweb $url 2>/dev/null | tee -a whatweb_results.txt
done
```

### 目录与文件扫描
```bash
# 目录枚举
gobuster dir -u <url> -w /path/to/wordlist -t 50 -x php,html,js

# 敏感文件扫描
dirsearch -u <url> -e php,html,js -w wordlists/dir.txt

# API 发现
ffuf -u <url>/FUZZ -w wordlists/api.txt -mc 200
```

### 资产关联分析
```bash
# 同 IP 站点查询
python3 sameip.py <ip>

# 备案查询
API: http://beian.chinaz.com/

# Whois 查询
whois example.com

# 证书关联
curl "https://crt.sh/?q=<org_name>&output=json"
```

## 📋 SRC 信息收集流程

### 阶段 0：准备阶段（重要）

```bash
# 1. 设置目标变量（必需）
export TARGET="example.com"  # 修改为你的目标域名

# 2. 配置 FOFA API（可选，但强烈推荐）
export FOFA_EMAIL="your_email@example.com"  # FOFA 账户邮箱
export FOFA_KEY="your_fofa_api_key"         # FOFA API Key

# 验证 FOFA 配置
if [ -n "$FOFA_EMAIL" ] && [ -n "$FOFA_KEY" ]; then
    echo "[+] FOFA API 已配置"
else
    echo "[!] FOFA API 未配置，将跳过 FOFA 搜索"
    echo "[!] 获取 FOFA Key: https://fofa.info/user/users/info"
fi

# 3. 确认授权
echo "目标: $TARGET"
echo "是否有授权测试? (y/n)"
read -r AUTHORIZED
if [ "$AUTHORIZED" != "y" ]; then
    echo "未授权，退出"
    exit 1
fi

# 4. 创建工作目录
mkdir -p recon/$TARGET
cd recon/$TARGET
```

### 阶段 1：初始资产收集

#### 1.1 主域名解析
```bash
nslookup $TARGET
dig $TARGET ANY
```

#### 1.2 FOFA 子域名搜索（优先）
```bash
# 使用 FOFA 搜索子域名
python3 << EOF
import base64
import requests
import os
import re

fofa_email = os.getenv('FOFA_EMAIL')
fofa_key = os.getenv('FOFA_KEY')
target = os.getenv('TARGET')

if not fofa_email or not fofa_key:
    print("[!] FOFA API 未配置，跳过")
    exit(0)

query = f'domain="{target}"'
query_base64 = base64.b64encode(query.encode()).decode()

url = f"https://fofa.info/api/v1/search/all?email={fofa_email}&key={fofa_key}&qbase64={query_base64}&size=1000"

try:
    print("[*] 正在使用 FOFA 搜索子域名...")
    resp = requests.get(url, timeout=30)
    data = resp.json()
    
    if data.get('error'):
        print(f"[-] FOFA API 错误: {data['errmsg']}")
        exit(1)
    
    if not data.get('results'):
        print("[-] FOFA 未找到结果")
        exit(0)
    
    subdomains = set()
    for result in data['results']:
        host = result[0]
        subs = re.findall(r'[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', host)
        subdomains.update(subs)
    
    with open('fofa_subs.txt', 'w') as f:
        for sub in sorted(subdomains):
            f.write(sub + '\n')
    
    print(f"[+] FOFA 发现 {len(subdomains)} 个子域名")
    
except Exception as e:
    print(f"[-] FOFA 搜索失败: {e}")
    exit(1)
EOF
```

#### 1.3 其他子域名枚举
```bash
# 被动 DNS 收集
subfinder -d $TARGET -o subs.txt

# 证书透明度
curl -s "https://crt.sh/?q=%.${TARGET}&output=json" | jq -r '.[].name_value' | sort -u > crt_subs.txt

# 合并所有来源
cat fofa_subs.txt subs.txt crt_subs.txt 2>/dev/null | grep -v '^$' | sort -u > all_subs.txt
echo "[+] 总共发现 $(wc -l < all_subs.txt) 个子域名"
```

#### 1.4 存活检测与 IP 段识别
```bash
# 存活检测
cat all_subs.txt | httpx -status-code -title -silent -threads 50 > alive.txt

# IP 段识别
whois $TARGET | grep -i "netrange\|inetnum\|netname"
```

### 阶段 2：端口服务扫描与 HTTP 服务探测
```bash
# 4. 端口扫描（存活主机）
# 扫描常见 HTTP/HTTPS 端口
nmap -iL all_subs.txt -p 80,443,8080,8443,3000,5000,8888,9000,9443 -T4 --open -oG port_scan.gnmap

# 5. 提取开放端口的主机
grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' port_scan.gnmap | sort -u > hosts_with_ports.txt

# 6. HTTP/HTTPS 服务探测
echo "[*] 正在探测 HTTP/HTTPS 服务..."

# 使用 httpx 批量探测（推荐）
cat all_subs.txt | httpx \
    -status-code \
    -title \
    -tech-detect \
    -waf-detect \
    -silent \
    -threads 50 \
    -retries 2 \
    -timeout 10 \
    -o http_services.txt

# 提取 HTTP 和 HTTPS 站点
echo "[+] HTTP 服务:"
grep -E "http://" http_services.txt | awk '{print $1}' | sort -u > http_urls.txt
echo "  发现 $(wc -l < http_urls.txt) 个 HTTP 服务"

echo "[+] HTTPS 服务:"
grep -E "https://" http_services.txt | awk '{print $1}' | sort -u > https_urls.txt
echo "  发现 $(wc -l < https_urls.txt) 个 HTTPS 服务"

# 7. 生成访问状态报告
echo "[*] 生成访问状态报告..."
cat > http_status_report.txt << EOF
# HTTP/HTTPS 服务访问状态报告

**目标**: $TARGET
**时间**: $(date +%Y-%m-%d\ %H:%M:%S)

## 📊 统计信息

| 类型 | 数量 |
|------|------|
| HTTP 服务 | $(wc -l < http_urls.txt 2>/dev/null || echo "0") |
| HTTPS 服务 | $(wc -l < https_urls.txt 2>/dev/null || echo "0") |
| 总计 | $(wc -l < http_services.txt 2>/dev/null || echo "0") |

## 🌐 HTTP 服务详情

\`\`\`
$(cat http_services.txt 2>/dev/null | grep -E "http://" || echo "无")
\`\`\`

## 🔒 HTTPS 服务详情

\`\`\`
$(cat http_services.txt 2>/dev/null | grep -E "https://" || echo "无")
\`\`\`

## ⚠️ 异常状态

| URL | 状态码 | 标题 | 问题 |
|-----|--------|------|------|
$(grep -E "\[4[0-9]{2}\]|\[5[0-9]{2}\]" http_services.txt 2>/dev/null | head -10 || echo "无异常状态")
EOF

echo "[+] 报告已生成: http_status_report.txt"
```

### 阶段 3：Web 应用指纹
```bash
# 6. Web 指纹识别
cat alive.txt | while read url; do
  whatweb $url
  wafw00f $url
done

# 7. 技术栈识别
nuclei -u <url> -t ~/nuclei-templates/technologies/
```

### 阶段 4：漏洞面发现

#### 4.1 敏感端点扫描
```bash
# 8. 敏感端点扫描
gobuster dir -u <url> -w wordlists/dirs.txt -x php,html,js,zip,bak

# 9. API 发现
ffuf -u <url>/api/FUZZ -w wordlists/api-endpoints.txt -mc 200

# 10. 敏感文件扫描
dirsearch -u <url> -e php,html,js,sql,zip -w wordlists/sensitive.txt
```

#### 4.2 JavaScript 路径提取（新增）
```bash
# 从所有 HTTP 服务提取路径（包括 200/3xx/4xx/5xx）
python3 js_path_extractor.py http_urls.txt extracted_paths.txt

# 参数说明：
# http_urls.txt - HTTP 服务列表（从阶段 2 生成）
# extracted_paths.txt - 输出提取的路径列表

# 为什么包括 4xx/5xx？
# - 即使是错误页面，也可能加载 JS 文件
# - SPA 应用可能返回空白页面但包含 JS
# - API 路径可能隐藏在 JS 中
```

#### 4.3 路径爆破测试（新增）
```bash
# 将提取的路径拼接到站点的目录结构中进行未授权访问测试
python3 path_bruteforcer.py https://example.com extracted_paths.txt

# 参数说明：
# https://example.com - 目标站点
# extracted_paths.txt - 从 JS 提取的路径列表

# 输出：
# path_bruteforce_report.txt - 测试结果报告

# 报告包含：
# - 可访问的 URL (200 OK)
# - 需要认证的 URL (401/403)
# - 错误信息
# - URL 大小和 Content-Type
```

#### 4.4 智能漏洞分析（新增）
```bash
# 基于收集的所有信息进行智能分析
# 1. 准备数据（将扫描结果转换为 JSON）

# 2. 运行智能分析
python3 vulnerability_analyzer.py scan_results.json vulnerability_analysis.txt

# 参数说明：
# scan_results.json - 包含所有 URL、状态码、大小等信息的 JSON
# vulnerability_analysis.txt - 输出的分析报告

# 分析维度：
# - 路径模式分析（/admin, /config, /debug）
# - 技术风险分析（/actuator, /graphql）
# - 状态码评估（200 OK 风险更高）
# - 响应特征分析（JSON、大文件、敏感关键字）

# 风险等级：
# - HIGH (≥15 分) - 优先验证
# - MEDIUM (10-14 分) - 有条件验证
# - LOW (5-9 分) - 有时间再测
# - INFO (< 5 分) - 信息收集
```

### 阶段 5：资产关联整理

#### 5.1 生成资产报告
```bash
# 11. 生成资产报告
cat > report.md << EOF
# SRC 资产收集报告

## 目标
- 主域名: example.com
- 子域名: $(wc -l < subs.txt)
- 存活资产: $(wc -l < alive.txt)
- 开放端口: $(grep "open" port_scan.gnmap | wc -l)

## 资产列表
$(cat alive.txt)

## 端口服务
$(grep "open" port_scan.gnmap)

## 指纹识别
$(cat fingerprint.txt)

## 潜在测试点
$(cat potential_targets.txt)
EOF
```

#### 5.2 完整的自动化流程（新增）
```bash
# 使用自动化脚本执行完整的 SRC 信息收集流程
cd ~/.openclaw/workspace/skills/src-recon
./src-recon-auto.sh example.com

# 该脚本会自动执行以下阶段：
# 阶段 1: FOFA 子域名收集
# 阶段 2: 子域名存活检测
# 阶段 3: 端口扫描
# 阶段 4: HTTP/HTTPS 服务扫描
# 阶段 5: HTTP 状态分类
# 阶段 6: JS 文件分析
# 阶段 7: Vue.js 检测
# 阶段 8: Spring Boot Actuator 检测
# 阶段 9: JS 路径提取（所有 HTTP 服务）
# 阶段 10: 路径爆破测试
# 阶段 11: 智能漏洞分析
# 阶段 12: 生成最终报告
```

## 📂 字典资源

### 子域名字典
```bash
# 常用子域名
wordlists/subdomains-top1million-5000.txt
wordlists/subdomains.txt

# 自定义字典
echo -e "www\napi\ntest\ndev\nstaging\nadmin\nblog\nshop\nm\nmobile" > custom_subs.txt
```

### 目录扫描字典
```bash
# 常用目录
wordlists/dirb-common.txt
wordlists/directory-list-2.3-medium.txt

# 敏感文件
wordlists/sensitive-files.txt
wordlists/backup-files.txt
```

### API 端点字典
```bash
echo -e "api\ngraphql\nv1\nv2\nadmin\nuser\nauth\nlogin\nregister\nprofile" > api-endpoints.txt
```

## 🔍 常见测试点

### 高价值端点
- `/admin` - 后台管理
- `/api` - API 接口
- `/graphql` - GraphQL 端点
- `/wp-admin` - WordPress 后台
- `/phpmyadmin` - 数据库管理
- `/.git` - Git 泄露
- `/backup.zip` - 备份文件
- `/web.config` - 配置文件
- `/sitemap.xml` - 站点地图

### 敏感参数
- `?debug=1` - 调试模式
- `?test=1` - 测试参数
- `?redirect=` - URL 重定向
- `?file=` - 文件包含
- `?page=` - 页面参数
- `?id=` - SQL 注入

## 🚨 安全提醒

- **遵守法律** - 只在授权范围内测试
- **控制速率** - 避免触发 WAF/封禁
- **保护数据** - 不泄露测试目标信息
- **合规提交** - 通过官方渠道提交漏洞

## 🎓 学习资源

- **平台规则**: 补天、漏洞盒子、HackerOne 规则文档
- **实战案例**: 公开的 SRC 漏洞报告
- **工具文档**: 各工具官方文档
- **社区**: 安全客、FreeBuf、看雪论坛

## 📊 输出文件说明

### 目录结构
```
recon/<target>/
├── all_subs.txt                     # 统一的子域名列表
├── http_services.txt                # HTTP/HTTPS 服务列表
├── status_200.txt                   # 200 OK 的服务
├── status_3xx.txt                   # 重定向的服务
├── status_4xx.txt                   # 客户端错误
├── status_5xx.txt                   # 服务器错误
├── port_scan.gnmap                  # Nmap 结果（快速扫描）
├── port_scan_full.gnmap             # Nmap 结果（全端口扫描）
│
├── jsfind_results/                  # JS 分析结果
│   ├── api_endpoints.txt            # 发现的 API 端点
│   ├── paths.txt                    # 提取的路径
│   ├── secrets.txt                  # 敏感信息
│   ├── verified_endpoints.txt       # 验证可访问的端点
│   └── accessible_chunks.txt        # 可访问的 chunk 文件
│
├── extracted_paths.txt              # 从 JS 提取的路径（所有服务）
├── js_files_scanned.txt             # 扫描的 JS 文件列表
│
├── path_bruteforce_report.txt       # 路径爆破测试报告
├── path_bruteforce_combined.txt     # 合并的测试结果
│
├── vuecrack_report.txt              # Vue.js 检测报告
├── actuator_report.txt              # Actuator 检测报告
│
├── vulnerability_analysis.txt       # 智能漏洞分析报告
├── all_scan_results.json            # 所有扫描结果（JSON）
│
└── report_*.txt                     # 最终汇总报告
```

### 关键文件说明

#### all_subs.txt
- 所有来源的子域名集合
- 来源：FOFA、subfinder、证书透明度等

#### http_services.txt
- HTTP/HTTPS 服务列表
- 格式：URL [状态码] [标题] [大小]

#### extracted_paths.txt（新增）
- 从所有 HTTP 服务的 JS 文件中提取的路径
- 包括 200/3xx/4xx/5xx 状态的服务
- 用于后续路径爆破

#### path_bruteforce_report.txt（新增）
- 路径爆破测试结果
- 分类：可访问、需要认证、错误
- 包含状态码、大小、Content-Type

#### vulnerability_analysis.txt（新增）
- 智能漏洞分析报告
- 风险分级：HIGH/MEDIUM/LOW/INFO
- 提供优先验证建议

---

## 📊 完整工作流程

```
输入: example.com
    ↓
[阶段 1] FOFA 子域名收集
    ↓
[阶段 2] 子域名存活检测
    ↓
[阶段 3] 端口扫描
    ↓
[阶段 4] HTTP/HTTPS 服务扫描
    ↓
[阶段 5] HTTP 状态分类
    ├─ status_200.txt
    ├─ status_3xx.txt
    ├─ status_4xx.txt
    └─ status_5xx.txt
    ↓
[阶段 6] JS 文件分析（仅 200）
    ├─ 提取 API 端点
    ├─ 提取路径
    ├─ 提取密钥
    └─ 验证可访问性
    ↓
[阶段 7] Vue.js 检测（仅 200）
    ├─ 检测 Vue 应用
    └─ 枚举路由
    ↓
[阶段 8] Spring Boot Actuator 检测（仅 200）
    ├─ 检测 Actuator
    └─ 扫描端点
    ↓
[阶段 9] JS 路径提取（所有 HTTP）
    ├─ 扫描所有 HTTP 服务
    ├─ 包括 200/3xx/4xx/5xx
    └─ 提取路径
    ↓
[阶段 10] 路径爆破测试（新增）
    ├─ 发现目录结构
    ├─ 路径拼接
    ├─ 并发测试
    └─ 记录结果
    ↓
[阶段 11] 智能漏洞分析（新增）
    ├─ 多维度分析
    ├─ 风险评分
    ├─ 优先级排序
    └─ 生成洞察
    ↓
[阶段 12] 生成最终报告
    └─ report_*.txt
```

---

## 🔧 并发配置

所有工具默认使用 **15 线程**并发，避免：
- 触发站点 WAF 封禁
- 导致站点访问失败
- 被防火墙拦截
- 对目标造成过大压力

如需调整，编辑对应工具的 `__init__` 方法：

```python
def __init__(self, timeout=10, max_workers=15):  # 修改这个值
    self.max_workers = max_workers
```

---

## 🔐 安全提醒

- **遵守法律** - 只在授权范围内测试
- **控制速率** - 避免触发 WAF/封禁（已默认优化）
- **保护数据** - 不泄露测试目标信息
- **合规提交** - 通过官方渠道提交漏洞

---

## 🎓 学习资源

- **平台规则**: 补天、漏洞盒子、HackerOne 规则文档
- **实战案例**: 公开的 SRC 漏洞报告
- **工具文档**: 各工具的使用指南（见 /root/.openclaw/workspace/skills/src-recon/*.md）
- **社区**: 安全客、FreeBuf、看雪论坛
- **茶馆**: [龙虾茶馆](https://github.com/ythx-101/openclaw-qa) - OpenClaw 社区

---

## 📝 自动化脚本模板

### 使用方法

```bash
# 方式 1：命令行参数
./src-recon-auto.sh example.com

# 方式 2：交互式输入
./src-recon-auto.sh
# 脚本会提示：请输入目标域名:
```

### 脚本模板

```bash
#!/bin/bash
# SRC 自动化信息收集脚本
# 使用方法: ./src-recon-auto.sh [目标域名]

# 检查参数或交互式输入
if [ -z "$1" ]; then
    read -p "请输入目标域名: " TARGET
else
    TARGET=$1
fi

# 验证域名格式
if [[ ! $TARGET =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$ ]]; then
    echo "[-] 无效的域名格式: $TARGET"
    exit 1
fi

OUTPUT_DIR="recon/$TARGET"
mkdir -p $OUTPUT_DIR

echo "[+] ========================================"
echo "[+] SRC 信息收集开始"
echo "[+] 目标: $TARGET"
echo "[+] 输出目录: $OUTPUT_DIR"
echo "[+] ========================================"

# 子域名枚举
echo "[*] 子域名枚举..."
subfinder -d $TARGET -o $OUTPUT_DIR/subs.txt
cat $OUTPUT_DIR/subs.txt | httpx -status-code -title -silent > $OUTPUT_DIR/alive.txt

# 端口扫描
echo "[*] 端口扫描..."
nmap -iL $OUTPUT_DIR/alive.txt -p 80,443,8080,8443 -oG $OUTPUT_DIR/port_scan.gnmap

# 指纹识别
echo "[*] 指纹识别...
cat $OUTPUT_DIR/alive.txt | while read url; do
  whatweb $url >> $OUTPUT_DIR/fingerprint.txt
done

# 敏感端点扫描
echo "[*] 敏感端点扫描..."
cat $OUTPUT_DIR/alive.txt | while read url; do
  gobuster dir -u $url -w wordlists/dirs.txt -t 30 -x php,html,js -o $OUTPUT_DIR/dirs_${url##//}.txt
done

echo "[+] 收集完成，结果保存在: $OUTPUT_DIR"
```

## 🎯 快速开始

### 使用自动化脚本（推荐）

```bash
# 1. 输入目标域名
TARGET="example.com"  # 修改为你的目标

# 2. 运行自动化脚本
cd ~/.openclaw/workspace/skills/src-recon
./src-recon-auto.sh $TARGET

# 3. 查看生成的报告
cat recon/$TARGET/report_*.txt

# 该脚本会自动执行 12 个阶段：
# 阶段 1: FOFA 子域名收集
# 阶段 2: 子域名存活检测
# 阶段 3: 端口扫描
# 阶段 4: HTTP/HTTPS 服务扫描
# 阶段 5: HTTP 状态分类
# 阶段 6: JS 文件分析
# 阶段 7: Vue.js 检测
# 阶段 8: Spring Boot Actuator 检测
# 阶段 9: JS 路径提取（所有 HTTP 服务）
# 阶段 10: 路径爆破测试
# 阶段 11: 智能漏洞分析
# 阶段 12: 生成最终报告
```

### 使用单个工具

```bash
# 1. FOFA 子域名收集
python3 fofa_subs.py example.com

# 2. HTTP 服务扫描
python3 http_scanner.py all_subs.txt http_services.txt

# 3. JS 文件分析
python3 jsfind.py https://example.com

# 4. Vue.js 检测
python3 vuecrack.py https://example.com

# 5. Spring Boot Actuator 检测
python3 actuator_scanner.py https://example.com

# 6. JS 路径提取（新增）
python3 js_path_extractor.py http_urls.txt extracted_paths.txt

# 7. 路径爆破测试（新增）
python3 path_bruteforcer.py https://example.com extracted_paths.txt

# 8. 智能漏洞分析（新增）
python3 vulnerability_analyzer.py scan_results.json vulnerability_analysis.txt
```

### 手动执行（逐步进行）

```bash
# 步骤 1：设置目标
export TARGET="example.com"

# 步骤 2：子域名枚举
subfinder -d $TARGET -o subs.txt

# 步骤 3：存活检测
cat subs.txt | httpx -status-code -title -silent > alive.txt

# 步骤 4：端口扫描
nmap -iL alive.txt -p 80,443,8080,8443 -oG port_scan.gnmap

# 步骤 5：指纹识别
nuclei -l alive.txt -t ~/nuclei-templates/technologies/

# 步骤 6：敏感端点扫描
gobuster dir -u https://www.$TARGET -w dirs.txt -x php,html,js,zip,bak
```

### 在 OpenClaw 中使用

```bash
# 通过 OpenClaw 执行
cd ~/.openclaw/workspace/skills/src-recon
./src-recon-auto.sh <目标域名>
```

---

## 📝 使用前准备

### 确认目标域名

在开始信息收集之前，请明确：
- ✅ 目标域名是什么？（如：example.com）
- ✅ 是否有授权测试？
- ✅ 测试范围是什么？（主域名、子域名、IP段）

### 设置变量

```bash
# 方式 1：命令行参数
./src-recon-auto.sh example.com

# 方式 2：环境变量
export TARGET="example.com"
./src-recon-auto.sh $TARGET

# 方式 3：交互式输入
read -p "请输入目标域名: " TARGET
./src-recon-auto.sh $TARGET
```

---

_记住：信息收集是渗透测试的基础，做好收集能事半功倍。🦞_
