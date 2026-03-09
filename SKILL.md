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

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/nqge/src-recon-skill.git
cd src-recon-skill

# 安装依赖
pip install -r requirements.txt

# 配置 FOFA API（可选）
export FOFA_EMAIL="your_email@example.com"
export FOFA_KEY="your_api_key"
```

### 自动化扫描（推荐）

```bash
# 一键完整扫描（9 个阶段）
./scripts/src-recon-auto.sh example.com

# 查看报告
cat output/recon/example.com/report_*.md
```

### 单个工具使用

```bash
# 子域名收集
python3 core/fofa_subs.py example.com

# HTTP 服务扫描
python3 core/http_scanner_enhanced.py domains.txt results.txt

# JS 文件分析
python3 core/jsfind.py https://example.com

# 路径爆破
python3 core/path_bruteforcer.py https://example.com paths.txt
```

## 🛠️ 工具清单

### Python 工具（12 个）

#### 1. auth_session_manager.py - 认证会话管理器
```bash
# 从文件加载认证信息
python3 core/auth_session_manager.py https://example.com auth.json

# 从环境变量加载
export TARGET_COOKIE="sessionid=xxx"
python3 core/auth_session_manager.py https://example.com

# 特点：
# - 支持 Cookie、账号密码、Token、API Key、Bearer Token
# - 自动应用认证到会话
# - 测试认证有效性
# - 保存会话供后续使用
```

#### 2. oneforall_subs.py - OneForAll 子域名收集
```bash
# 常规收集（无需 API）
python3 core/oneforall_subs.py example.com

# 使用搜索引擎 API
python3 core/oneforall_subs.py example.com --api

# 特点：
# - 集成 30+ 种子域名收集方法
# - 支持多种搜索引擎 API（Shodan、Censys、FOFA、Quake）
# - 证书透明度查询
# - 威胁情报平台集成
# - 自动去重和验证
```

#### 3. fofa_subs.py - FOFA 子域名收集
```bash
# 使用 FOFA API 进行大规模子域名收集
python3 core/fofa_subs.py example.com

# 输出：
# - fofa_subs.txt - 收集的子域名列表
# - fofa_results.json - 详细结果（JSON 格式）

# 特点：
# - 使用 FOFA API（需要配置 FOFA_EMAIL 和 FOFA_KEY）
# - 支持大规模查询
# - 自动去重和排序
```

#### 4. http_scanner.py - HTTP/HTTPS 服务扫描
```bash
# 批量扫描 HTTP/HTTPS 服务
python3 core/http_scanner.py domains.txt results.txt

# 特点：
# - 并发扫描提高速度
# - 状态码和标题提取
# - 按状态码分类
# - 支持 HTTP 和 HTTPS
```

#### 5. http_scanner_enhanced.py - 增强版 HTTP 扫描
```bash
# 同时测试 HTTP 和 HTTPS
python3 core/http_scanner_enhanced.py domains.txt results.txt

# 输出：
# - http_services.txt - HTTP 服务列表
# - resolved_ips.txt - 解析的 IP 列表
# - domain_ip_mapping.json - 域名到 IP 映射

# 特点：
# - 同时测试 HTTP 和 HTTPS
# - DNS 解析获取 IP
# - 生成 IP 列表供端口扫描
# - 连接错误和 SSL 错误诊断
```

#### 6. connection_improver.py - 连接改进工具
```bash
# 对失败的连接进行改进
python3 core/connection_improver.py http_services.txt improvement.txt

# 特点：
# - SSL 错误诊断（证书有效性、链验证）
# - 连接错误诊断（DNS、端口、防火墙）
# - 多协议测试（HTTP、HTTPS、Alt 端口）
# - 自动生成解决方案
```

#### 7. jsfind.py - JavaScript 文件分析
```bash
# 分析 JavaScript 文件
python3 core/jsfind.py https://example.com

# 输出：
# - jsfind_results/api_endpoints.txt - API 端点
# - jsfind_results/paths.txt - 发现的路径
# - jsfind_results/secrets.txt - 敏感信息
# - jsfind_results/verified_endpoints.txt - 验证可访问的端点
# - jsfind_results/accessible_chunks.txt - 可访问的 chunk 文件

# 特点：
# - 自动发现和下载 JS 文件
# - 提取 API 端点、路径、敏感信息
# - 验证端点可访问性
# - Chunk 文件映射和验证
```

#### 8. vuecrack.py - Vue.js 应用检测
```bash
# 检测 Vue.js 应用并枚举路由
python3 core/vuecrack.py https://example.com

# 输出：
# - vuecrack_report.txt - 检测报告

# 特点：
# - 检测 Vue.js 框架
# - 枚举所有路由
# - 检测未授权访问
# - 挖掘隐藏页面
```

#### 9. actuator_scanner.py - Spring Boot Actuator 检测
```bash
# 检测 Spring Boot Actuator 端点
python3 core/actuator_scanner.py https://example.com

# 输出：
# - actuator_report.txt - 检测报告

# 特点：
# - 检测 Actuator 暴露
# - 扫描常见端点
# - 识别漏洞
# - 检测未授权访问
```

#### 10. js_path_extractor.py - JS 路径提取器
```bash
# 从所有 HTTP 服务提取 JS 路径
python3 core/js_path_extractor.py http_services.txt paths.txt

# 特点：
# - 扫描所有 HTTP 服务（包括 403、404）
# - 提取 JS 文件中的路径
# - 生成路径列表供爆破使用
```

#### 11. path_bruteforcer.py - 路径爆破测试器
```bash
# 路径拼接和爆破测试
python3 core/path_bruteforcer.py https://example.com paths.txt results.txt

# 输出：
# - path_bruteforce_results.txt - 测试结果

# 特点：
# - 自动发现目录结构
# - 路径拼接和测试
# - 并发扫描提高速度
# - 生成详细报告
```

#### 12. vulnerability_analyzer.py - 智能漏洞分析器
```bash
# 智能漏洞分析
python3 core/vulnerability_analyzer.py scan_results.json analysis.txt

# 输出：
# - vulnerability_analysis.txt - 分析报告

# 特点：
# - 多维度风险评分
# - 优先级排序
# - 生成洞察和建议
```

## 🔥 完整的 9 阶段自动化流程

```
阶段 1: 子域名枚举（FOFA）
    ├─ 使用 FOFA API 收集子域名
    ├─ 自动去重和验证
    └─ 输出: all_subs.txt
    ↓
阶段 2: HTTP/HTTPS 服务扫描 + IP 解析
    ├─ 同时测试 HTTP 和 HTTPS
    ├─ DNS 解析获取 IP
    ├─ 🔥 新增：连接错误和 SSL 错误改进
    └─ 输出: http_services.txt, resolved_ips.txt
    ↓
阶段 3: 端口扫描
    ├─ 扫描解析的 IP
    ├─ 🔥 新增：发现 Web 端口（80/443/8080/8443）
    ├─ 🔥 新增：生成端口 URL 并扫描
    ├─ 🔥 新增：合并新发现的 URL
    └─ 输出: port_scan.gnmap, port_http_services.txt
    ↓
阶段 4: JS 文件分析（200 状态）
    ├─ 分析可访问的 HTTP 服务
    ├─ 提取 API 端点、路径、敏感信息
    └─ 输出: jsfind_results/
    ↓
阶段 5: Vue.js 应用检测（200 状态）
    ├─ 检测 Vue.js 框架
    └─ 枚举所有路由
    ↓
阶段 6: Spring Boot Actuator 检测（200 状态）
    ├─ 检测 Actuator 暴露
    └─ 扫描常见端点
    ↓
阶段 7: 路径爆破测试（200/403 状态）
    ├─ 路径拼接和爆破
    ├─ 并发测试
    └─ 输出: path_bruteforce_combined.txt
    ↓
阶段 8: 智能漏洞分析（所有结果）
    ├─ 多维度风险评分
    ├─ 优先级排序
    └─ 生成洞察
    ↓
阶段 9: 最终报告
    └─ Markdown 格式的完整报告
```

## 🔥 最新改进（v1.1.0）

### 改进 1: 阶段 2 连接错误和 SSL 错误处理

**问题**: 大量 URL 因为连接错误或 SSL 错误被忽略

**解决方案**:
```bash
# 自动提取有错误的 URL
grep "\[ERROR\]" http_services.txt | awk '{print $2}' > error_urls.txt

# 运行连接改进工具
python3 core/connection_improver.py \
  http_services.txt \
  connection_improvement.txt
```

### 改进 2: 阶段 3 端口扫描后服务探测

**问题**: 端口扫描发现的 Web 服务未进行 HTTP 探测

**解决方案**:
```bash
# 从端口扫描结果提取 Web 端口
grep -E "80/tcp|443/tcp|8080/tcp|8443/tcp" port_scan.gnmap | \
  grep "open" | awk '{print $2}' > web_ips.txt

# 为每个 IP 生成 HTTP/HTTPS URL
while IFS= read -r ip; do
    echo "http://$ip" >> port_http_urls.txt
    echo "https://$ip" >> port_http_urls.txt
done < web_ips.txt

# 对新发现的 URL 进行 HTTP 扫描
python3 core/http_scanner_enhanced.py \
  port_http_urls.txt \
  port_http_services.txt

# 合并新的可访问 URL 到主列表
grep -E "^\[200\]|^\[30[0-9]\]|^\[403\]" port_http_services.txt | \
  awk '{print $2}' >> http_urls.txt

# 去重
sort -u http_urls.txt -o http_urls.txt
```

## 📊 使用示例

### 示例 1: 完整自动化扫描

```bash
# 配置 FOFA API
export FOFA_EMAIL="your_email@example.com"
export FOFA_KEY="your_api_key"

# 运行自动化扫描
./scripts/src-recon-auto.sh example.com

# 查看报告
cat output/recon/example.com/report_*.md
```

### 示例 2: 单独使用工具

```bash
# 子域名收集
python3 core/fofa_subs.py example.com

# HTTP 扫描
python3 core/http_scanner_enhanced.py domains.txt results.txt

# JS 分析
python3 core/jsfind.py https://example.com

# 智能分析
python3 core/vulnerability_analyzer.py scan_results.json
```

## 📁 项目结构

```
src-recon-skill/
├── SKILL.md                          # 本文件
├── README.md                         # 项目介绍
├── requirements.txt                  # Python 依赖
├── LICENSE                           # MIT 许可证
├── .gitignore                        # Git 忽略文件
│
├── core/                             # Python 工具（12 个）
│   ├── auth_session_manager.py
│   ├── oneforall_subs.py
│   ├── fofa_subs.py
│   ├── http_scanner.py
│   ├── http_scanner_enhanced.py
│   ├── connection_improver.py
│   ├── jsfind.py
│   ├── vuecrack.py
│   ├── actuator_scanner.py
│   ├── js_path_extractor.py
│   ├── path_bruteforcer.py
│   └── vulnerability_analyzer.py
│
├── scripts/                          # 自动化脚本
│   └── src-recon-auto.sh             # 主自动化脚本
│
├── docs/                             # 文档
│   ├── PROJECT_STRUCTURE.md          # 项目结构
│   ├── CONNECTION_IMPROVEMENT.md     # 连接改进指南
│   └── [其他工具指南]
│
├── wordlists/                        # 字典
│   ├── wordlists.txt                 # 通用字典
│   └── dirs.txt                      # 目录字典
│
├── utils/                            # 工具
│   └── [辅助工具]
│
└── output/                           # 输出目录
    └── recon/
        └── <target>/
            ├── all_subs.txt
            ├── http_services.txt
            ├── http_urls.txt
            ├── resolved_ips.txt
            ├── port_scan.gnmap
            ├── port_http_services.txt
            ├── connection_improvement.txt
            ├── jsfind_results/
            ├── vuecrack_report.txt
            ├── actuator_report.txt
            ├── path_bruteforce_combined.txt
            ├── vulnerability_analysis.txt
            └── report_*.md
```

## 🎯 适用场景

### 1. SRC 众测

```bash
./scripts/src-recon-auto.sh target.com
```

### 2. 子域名枚举

```bash
python3 core/oneforall_subs.py target.com
python3 core/fofa_subs.py target.com
```

### 3. 漏洞挖掘

```bash
# JS 分析
python3 core/jsfind.py https://example.com

# 路径爆破
python3 core/path_bruteforcer.py https://example.com paths.txt

# 智能分析
python3 core/vulnerability_analyzer.py scan_results.json
```

## 🔧 配置说明

### FOFA API 配置

```bash
# 配置 FOFA API
export FOFA_EMAIL="your_email@example.com"
export FOFA_KEY="your_api_key"
```

### 扫描模式配置

```bash
# 快速扫描（默认，Top 1000 + Web 端口）
export SCAN_MODE="fast"

# 全端口扫描（1-65535）
export SCAN_MODE="full"
```

## 📚 参考文档

- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [连接改进指南](docs/CONNECTION_IMPROVEMENT.md)
- [OneForAll 配置](docs/ONEFORALL_SETUP.md)
- [FOFA API 配置](docs/FOFA_SETUP.md)

## 🌟 社区

- **GitHub**: https://github.com/nqge/src-recon-skill
- **博客**: https://nqge.github.io/xiaoniu-blog/
- **茶馆**: https://github.com/ythx-101/openclaw-qa

## 📄 许可证

MIT License

---

_生成工具: 小牛的 SRC 信息收集技能 🦞_
