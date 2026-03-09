---
name: src-recon
description: SRC 众测平台信息收集技能 - 自动化收集目标资产、子域名、端口、漏洞指纹。用于：(1) SRC 项目资产收集，(2) 子域名枚举，(3) 端口服务识别，(4) 漏洞面发现，(5) 资产关联分析。触发词：SRC、众测、信息收集、资产收集、子域名、端口扫描。
---

# SRC 众测信息收集技能（v2.2 - API 参数测试 + 高级 Payload）

SRC（Security Response Center）众测平台的自动化资产收集与漏洞面发现工具包。

## 🎯 核心能力

1. **资产收集** - 主域名、子域名、IP 段、CDN 识别
2. **子域名枚举** - 被动收集、主动爆破、证书透明度、FOFA API
3. **端口扫描** - 混合策略（Nmap + 魔改 Fscan）、服务识别、版本探测
4. **指纹识别** - Web 框架、CMS、WAF、中间件
5. **漏洞面发现** - 敏感端点、API 接口、未授权页面
6. **资产关联** - 同 IP 站点、同备案、证书关联
7. **智能访问** - 自动检测目标类型、优化 SSL 访问、多种方法组合

## 🆕 v2.2 新特性

### API 参数测试工具

**新增 Stage 9**：自动化 API 参数测试
- ✅ 支持 214 个测试 payload
- ✅ 6 大漏洞类型：SQL 注入、XSS、路径遍历、SSRF、未授权访问
- ✅ 智能测试：自动识别可测参数、智能替换、响应分析
- ✅ 详细报告：Markdown 格式、漏洞分级、修复建议

**使用方法**：
```bash
python3 core/api_parameter_tester.py $TARGET output/recon/$TARGET/jsfind_results
```

**测试能力**：
- SQL 注入测试（91 个 payload）
  - 高级函数：substring, substr, substrB, case when, left, right
  - 长度函数：length(), len()
  - 运算符报错：除法、取模、位运算、溢出
- XSS 测试（63 个 payload）
  - 脚本注入、图片注入、SVG 注入
  - 事件处理器、CSS 注入
- 路径遍历测试（27 个 payload）
  - Linux/Windows 路径遍历
  - 日志文件、配置文件
- SSRF 测试（27 个 payload）
  - 内网访问、云元数据
  - DNS 外带、Gopher 协议
- 未授权访问测试（6 个 payload）
  - 常见未授权端点

### 高级 SQL 注入 Payload

**新增 26 个高级函数 payload**：
- 字符串截取：substring, substr, substrB
- 条件判断：case when
- 左右截取：left, right
- 长度函数：length(), len()

**新增 8 个隐式版本 payload**：
- 移除 `AND` 关键字
- 使用 `OR` 代替
- 更难被 WAF 检测

**新增 8 个除法运算 payload**：
- Oracle, MySQL, PostgreSQL, SQL Server
- 数据库指纹识别
- 错误消息提取

### 11 阶段自动化流程

**更新后的阶段划分**：
1. Stage 1: 子域名收集
2. Stage 2: 存活检测
3. Stage 3: 端口扫描
4. Stage 4: JS 文件分析
5. Stage 5: 路径提取
6. Stage 6: 指纹识别
7. Stage 7: 路径爆破
8. Stage 8: 访问测试
9. **Stage 9: API 参数测试** ⭐ 新增
10. Stage 10: 智能漏洞分析
11. Stage 11: 最终报告生成

## 🆕 v2.1 新特性

### 智能目标类型检测

**自动检测目标类型**：
- ✅ IP 地址：跳过子域名收集，直接生成基础文件
- ✅ URL：提取域名后进行子域名收集
- ✅ 域名：进行完整的子域名收集

**使用方法**：
```bash
# IP 地址
./scripts/stage1_subs_collect.sh 192.168.1.1

# URL
./scripts/stage1_subs_collect.sh "https://jxgj.jshbank.com/wxcp/index.html"

# 域名
./scripts/stage1_subs_collect.sh jshbank.com
```

### 访问优化策略

**多种方法组合**：
1. requests (custom SSL) - 自定义 SSL 适配器
2. curl -k - 忽略 SSL 证书
3. curl -kL - 跟随重定向
4. HTTP fallback - HTTPS 转 HTTP
5. Browser UA - 模拟浏览器访问

**改进效果**：
- 从 6 个可访问 URL 增加到 10 个
- 提升了 66.7%
- SSL Error 改进率 22.2%

---

## 🛠️ 工具清单

### Python 工具（15 个）

#### 1. optimized_access_tester.py - 优化版访问测试器（新增）
```bash
# 多方法组合测试
python3 core/optimized_access_tester.py urls.txt report.md

# 完整测试
python3 core/optimized_access_tester.py urls.txt report.md --timeout 30 --workers 10

# 输出：
# report.md - Markdown 格式报告

# 特点：
# - 5 种方法组合测试
# - 自动尝试所有方法，返回第一个成功的结果
# - 并发测试（默认 5 线程）
# - 超时控制（默认 15 秒）
# - 详细的统计报告

# 测试方法：
# 1. requests (custom SSL) - 自定义 SSL 适配器
# 2. curl -k - 忽略 SSL 证书
# 3. curl -kL - 跟随重定向
# 4. HTTP fallback - HTTPS 转 HTTP
# 5. Browser UA - 模拟浏览器访问

# 改进效果：
# - 从 6 个可访问 URL 增加到 10 个
# - 提升了 66.7%
# - SSL Error 改进率 22.2%
```

#### 2. port_scanner_custom.py - 魔改版端口扫描器
```bash
# 扫描 Top 1000 端口（快速）
python3 core/port_scanner_custom.py \
  target_ips.txt \
  -p 1-1000 \
  -o output.gnmap \
  -f gnmap \
  -t 100 \
  --timeout 3

# 扫描特定端口
python3 core/port_scanner_custom.py \
  target_ips.txt \
  -p 80,443,8080,8443 \
  -o web_ports.gnmap

# 输出格式选项：
# -f gnmap  # GNMAP 格式（兼容 Nmap）
# -f json   # JSON 格式
# -f txt    # TXT 格式

# 特点：
# - 随机 User-Agent（6 种浏览器指纹）
# - 随机延迟（50-200ms）
# - 随机 HTTP 请求头
# - 避免 WAF/防火墙识别
# - 高并发（100 线程）
# - GNMAP 格式输出（兼容 Nmap）

# 魔改特性：
# - 避免 WAF 识别
# - 避免被封禁
# - 模拟真实浏览器
# - 服务指纹识别
```

#### 3-15. 其他工具

包括：
- auth_session_manager.py
- oneforall_subs.py
- fofa_subs.py
- http_scanner.py
- jsfind.py
- vuecrack.py
- actuator_scanner.py
- js_path_extractor.py
- path_bruteforcer.py
- vulnerability_analyzer.py
- advanced_connection_tester.py
- http_access_tester.py
- browser_access_tester.py
- simple_subfinder.py

（详见原 SKILL.md）

---

## 🚀 快速开始

### 方法 1: 使用分阶段脚本（推荐 v2.1）

```bash
# 完整流程（4 个阶段）
./scripts/stage1_subs_collect.sh example.com
./scripts/stage2_service_scan.sh example.com
./scripts/stage3_port_scan_hybrid.sh example.com
./scripts/stage4_deep_analysis.sh example.com
```

### 方法 2: 智能目标输入（v2.1 新增）

```bash
# IP 地址（自动跳过子域名收集）
./scripts/stage1_subs_collect.sh 192.168.1.1

# URL（自动提取域名并收集子域名）
./scripts/stage1_subs_collect.sh "https://jxgj.jshbank.com/wxcp/index.html"

# 域名（进行子域名收集）
./scripts/stage1_subs_collect.sh jshbank.com
```

### 方法 3: 使用混合扫描策略

```bash
# 阶段 3: 混合扫描（Nmap + 魔改 Fscan）
./scripts/stage3_port_scan_hybrid.sh example.com
```

### 方法 4: 优化版访问测试

```bash
# 多方法组合测试
python3 core/optimized_access_tester.py urls.txt report.md
```

---

## 📊 v2.1 核心改进

### 1. 智能目标类型检测

**自动检测目标类型**：
```
IP 地址 → 跳过子域名收集，直接生成基础文件
URL    → 提取域名，进行子域名收集
域名    → 进行子域名收集
```

**优势**：
- ✅ 更智能（自动检测目标类型）
- ✅ 更高效（IP 目标跳过子域名收集，节省 5-10 分钟）
- ✅ 更灵活（支持多种目标类型）

### 2. 优化版访问测试

**5 种方法组合**：
```
1. requests (custom SSL) - 自定义 SSL 适配器
2. curl -k - 忽略 SSL 证书
3. curl -kL - 跟随重定向
4. HTTP fallback - HTTPS 转 HTTP
5. Browser UA - 模拟浏览器访问
```

**改进效果**：
```
改进前: 6 个可访问 URL (8.3%)
改进后: 10 个可访问 URL (13.9%)
提升: +4 个 URL (+66.7%)
```

### 3. 分阶段脚本体系

**4 个独立阶段**：
```
阶段 1: 子域名收集（智能目标检测）
阶段 2: 服务探测和 IP 解析
阶段 3: 端口扫描（混合策略）
阶段 4: 深度分析
```

### 4. 混合扫描策略

**Nmap + 魔改 Fscan**：
```
Nmap: 标准端口，高精度
Fscan: Top 1000，快速探测
魔改: 特征去除，避免识别
```

---

## 📊 输出文件结构（v2.1）

```
output/recon/<target>/
├── stage1/
│   ├── all_subs_unique.txt          # 唯一子域名
│   ├── all_urls_unique.txt          # 唯一 URL
│   ├── all_ips_unique.txt           # 唯一 IP
│   └── domain_ip_mapping.json       # 域名到 IP 映射
│
├── stage2/
│   ├── http_services.txt            # HTTP 扫描结果
│   ├── http_accessible_urls.txt     # 可访问的 URL
│   ├── resolved_ips.txt             # 解析的 IP
│   ├── domain_ip_mapping.json       # 域名到 IP 映射
│   ├── all_ips_unique.txt           # 唯一 IP（汇总）
│   └── http_access_improvement.txt   # 连接改进报告
│
├── stage3/
│   ├── nmap/
│   │   └── standard_ports.gnmap     # Nmap 精准扫描结果
│   ├── fscan/
│   │   └── top1000_ports.gnmap      # Fscan 快速扫描结果
│   ├── combined/
│   │   └── port_scan_combined.gnmap # 合并去重结果
│   ├── web_ips.txt                  # Web 服务 IP
│   ├── port_http_urls.txt           # 端口 URL
│   ├── port_http_services.txt       # 端口 HTTP 扫描
│   ├── port_accessible_urls.txt     # 端口可访问 URL
│   ├── other_service_results.txt    # 其他端口测试
│   ├── other_accessible_urls.txt    # 其他可访问 URL
│   ├── all_accessible_urls.txt      # 总计可访问 URL
│   └── scan_report.txt              # 扫描报告
│
└── stage4/
    ├── jsfind_results/              # JS 分析结果
    ├── vuecrack_report.txt          # Vue.js 报告
    ├── actuator_report.txt          # Actuator 报告
    ├── path_bruteforce_combined.txt # 路径爆破结果
    ├── vulnerability_analysis.txt   # 智能分析
    └── final_report.md              # 最终报告
```

---

## 💡 使用场景

### 场景 1: IP 地址目标

```bash
./scripts/stage1_subs_collect.sh 192.168.1.1
```

**特点**：
- ✅ 自动检测为 IP 地址
- ✅ 跳过子域名收集（节省时间）
- ✅ 直接生成 IP 文件和 URL

**输出**：
```
stage1/
├── all_subs_unique.txt      # 空（0 个子域名）
├── all_ips_unique.txt       # 192.168.1.1
└── all_urls_unique.txt      # http://192.168.1.1
                              # https://192.168.1.1
```

---

### 场景 2: URL 目标

```bash
./scripts/stage1_subs_collect.sh "https://jxgj.jshbank.com/wxcp/index.html"
```

**特点**：
- ✅ 自动检测为 URL
- ✅ 提取域名：jxgj.jshbank.com
- ✅ 进行子域名收集

**输出**：
```
stage1/
├── all_subs_unique.txt      # 36 个子域名
├── all_ips_unique.txt       # 42 个 IP
└── all_urls_unique.txt      # 72 个 URL
```

---

### 场景 3: 域名目标

```bash
./scripts/stage1_subs_collect.sh jshbank.com
```

**特点**：
- ✅ 自动检测为域名
- ✅ 进行完整的子域名收集

**输出**：
```
stage1/
├── all_subs_unique.txt      # 36 个子域名
├── all_ips_unique.txt       # 42 个 IP
└── all_urls_unique.txt      # 72 个 URL
```

---

## 🔧 错误处理和优化

### 错误类型

**Connection Error (66.7%)**：
- 大部分是内部环境（F5 设备）
- DNS 解析失败
- 网络隔离
- **难以改进**

**SSL Error (27.3%)**：
- Legacy SSL Renegotiation 问题
- SSL 证书过期
- **可改进**（使用自定义 SSL 适配器）

**Timeout (6.1%)**：
- 网络延迟
- 服务过载
- **可部分改进**（增加超时时间）

### 改进方法

**1. HTTP 访问测试工具**
```bash
python3 core/http_access_tester.py ssl_error_urls.txt ssl_improvement.txt
```

**2. 优化版访问测试器**
```bash
python3 core/optimized_access_tester.py all_error_urls.txt optimization_report.md
```

**3. 增加超时时间**
```bash
export TIMEOUT=30
python3 core/http_scanner_enhanced.py all_subs.txt http_services.txt
```

---

## 📊 版本对比

### v1.0 vs v2.0 vs v2.1

| 特性 | v1.0 | v2.0 | v2.1 |
|------|------|------|------|
| 脚本结构 | 单一脚本 | 分阶段脚本（4 个） | 分阶段脚本（智能目标检测） |
| 端口扫描 | Nmap 单一工具 | 混合策略（Nmap + Fscan） | 混合策略 + 魔改版 |
| 特征识别 | 容易被识别 | 魔改版避免识别 | 魔改版 + 随机化 |
| 目标类型 | 仅域名 | 仅域名 | IP + URL + 域名 ✅ |
| 访问优化 | 无 | HTTP 访问测试工具 | 5 种方法组合 ✅ |
| 数据整合 | 手动整合 | 自动整合去重 | 自动整合去重 |
| 输出目录 | 单一目录 | 分阶段目录 | 分阶段目录 |
| 灵活性 | 低 | 高 | 非常高 ✅ |

---

## 🎓 学习资源

- **平台规则**: 补天、漏洞盒子、HackerOne 规则文档
- **实战案例**: 公开的 SRC 漏洞报告
- **工具文档**: 各工具的使用指南（见 docs/ 目录）
- **社区**: 安全客、FreeBuf、看雪论坛
- **茶馆**: [龙虾茶馆](https://github.com/ythx-101/openclaw-qa) - OpenClaw 社区

---

## 🔐 安全提醒

- **遵守法律** - 只在授权范围内测试
- **控制速率** - 避免触发 WAF/封禁（魔改版已优化）
- **保护数据** - 不泄露测试目标信息
- **合规提交** - 通过官方渠道提交漏洞

---

## 📝 使用前准备

### 确认目标类型

在开始信息收集之前，请明确：
- ✅ 目标是什么？（IP/URL/域名）
- ✅ 是否有授权测试？
- ✅ 测试范围是什么？

### 设置变量

```bash
# 方式 1: 命令行参数（支持多种类型）
./scripts/stage1_subs_collect.sh 192.168.1.1
./scripts/stage1_subs_collect.sh "https://example.com"
./scripts/stage1_subs_collect.sh example.com

# 方式 2: 环境变量
export TARGET="example.com"
./scripts/stage1_subs_collect.sh $TARGET

# 方式 3: 交互式输入
./scripts/src-recon-auto.sh
```

---

_记住：信息收集是渗透测试的基础，做好收集能事半功倍。🦞_

**v2.1 - 智能目标检测 + 访问优化，更智能、更高效、更灵活！🦞**
