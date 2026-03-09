---
name: src-recon
description: SRC 众测平台信息收集技能 - 自动化收集目标资产、子域名、端口、漏洞指纹。用于：(1) SRC 项目资产收集，(2) 子域名枚举，(3) 端口服务识别，(4) 漏洞面发现，(5) 资产关联分析。触发词：SRC、众测、信息收集、资产收集、子域名、端口扫描。
---

# SRC 众测信息收集技能（v2.0 - 分阶段 + 混合扫描）

SRC（Security Response Center）众测平台的自动化资产收集与漏洞面发现工具包。

## 🎯 核心能力

1. **资产收集** - 主域名、子域名、IP 段、CDN 识别
2. **子域名枚举** - 被动收集、主动爆破、证书透明度、FOFA API
3. **端口扫描** - 混合策略（Nmap + 魔改 Fscan）、服务识别、版本探测
4. **指纹识别** - Web 框架、CMS、WAF、中间件
5. **漏洞面发现** - 敏感端点、API 接口、未授权页面
6. **资产关联** - 同 IP 站点、同备案、证书关联

## 🆕 v2.0 新特性

### 分阶段脚本体系

**4 个独立阶段**，每阶段可单独运行：

```bash
# 阶段 1: 子域名收集
./scripts/stage1_subs_collect.sh example.com

# 阶段 2: 服务探测和 IP 解析
./scripts/stage2_service_scan.sh example.com

# 阶段 3: 端口扫描（混合策略）
./scripts/stage3_port_scan_hybrid.sh example.com

# 阶段 4: 深度分析
./scripts/stage4_deep_analysis.sh example.com
```

### 混合扫描策略

**结合 Nmap 和魔改 Fscan 的优势**：

```bash
# 方法 1: Nmap 精准扫描（标准端口）
├─ 端口: 80, 443, 8080, 8443, 3000, 5000, 8888, 9000, 9443
├─ 高精度，服务识别
└─ 输出到 stage3/nmap/

# 方法 2: 魔改 Fscan 快速扫描（Top 1000）
├─ 端口: 1-1000
├─ 高并发，快速探测
├─ 特征去除，避免识别
└─ 输出到 stage3/fscan/

# 结果整合:
├─ 合并 Nmap + Fscan 结果
├─ 去重（同一 IP:端口 只保留一次）
└─ 输出到 stage3/combined/
```

### 魔改特性（避免被识别封禁）

**1. 随机 User-Agent（6 种浏览器指纹）**
```python
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120',
    'Mozilla/5.0 (X11; Linux x86_64) Chrome/120',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/17',
]
```

**2. 随机延迟（50-200ms）**
```python
time.sleep(random.uniform(MIN_DELAY, MAX_DELAY) / 1000.0)
```

**3. 随机 HTTP 请求头**
```python
methods = ['GET', 'HEAD', 'OPTIONS']
method = random.choice(methods)

# 70% 概率添加其他头
if random.random() > 0.3:
    request += f"{key}: {value}\r\n"
```

**4. 服务指纹识别**
```python
def _extract_server_header(self, response: str) -> str:
    # 提取 Server 头（兼容 Nmap）
```

---

## 🛠️ 工具清单

### Python 工具（14 个）

#### 1. port_scanner_custom.py - 魔改版端口扫描器（新增）
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

#### 2-14. 其他工具（保持不变）

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
- simple_subfinder.py

（详见原 SKILL.md）

---

## 🚀 快速开始

### 方法 1: 使用分阶段脚本（推荐 v2.0）

```bash
# 完整流程（4 个阶段）
./scripts/stage1_subs_collect.sh example.com
./scripts/stage2_service_scan.sh example.com
./scripts/stage3_port_scan_hybrid.sh example.com  # 混合扫描策略
./scripts/stage4_deep_analysis.sh example.com

# 或使用优化版一键脚本
./scripts/src-recon-auto-optimized.sh example.com
```

### 方法 2: 使用混合扫描策略（新增）

```bash
# 阶段 3: 混合扫描（Nmap + 魔改 Fscan）
./scripts/stage3_port_scan_hybrid.sh example.com

# 输出目录：
# stage3/nmap/          - Nmap 精准扫描结果
# stage3/fscan/         - Fscan 快速扫描结果
# stage3/combined/      - 合并去重结果
# stage3/web_ips.txt    - Web 服务 IP
# stage3/scan_report.txt - 扫描报告
```

### 方法 3: 单独使用魔改 Fscan（新增）

```bash
# 扫描 Top 1000
python3 core/port_scanner_custom.py \
  target_ips.txt \
  -p 1-1000 \
  -o output.gnmap \
  -f gnmap \
  -t 100

# 扫描特定端口
python3 core/port_scanner_custom.py \
  target_ips.txt \
  -p 80,443,8080,8443 \
  -o web_ports.gnmap
```

### 方法 4: 使用自动化脚本（v1.0）

```bash
./scripts/src-recon-auto.sh example.com
```

---

## 📊 分阶段工作流程

```
输入: example.com
    ↓
[阶段 1] 子域名收集
├─ FOFA 收集
├─ Simple Subfinder（CT 日志 + DNSdumpster）
├─ 字典爆破（270+ 词）
├─ 子域名去重
├─ URL 生成（HTTP + HTTPS）
├─ IP 解析
└─ 输出到 stage1/
    ↓
[阶段 2] 服务探测和 IP 解析
├─ HTTP/HTTPS 服务扫描
├─ 提取可访问的 URL
├─ IP 解析
├─ 整合阶段 1 + 阶段 2 的 IP
├─ IP 去重
├─ 连接错误改进
└─ 输出到 stage2/
    ↓
[阶段 3] 端口扫描（混合策略）
├─ Nmap 精准扫描（标准端口）
│   ├─ 80, 443, 8080, 8443, 3000, 5000, 8888, 9000, 9443
│   ├─ 高精度，服务识别
│   └─ 输出到 stage3/nmap/
├─ 魔改 Fscan 快速扫描（Top 1000）
│   ├─ 1-1000 端口
│   ├─ 高并发，快速探测
│   ├─ 特征去除，避免识别
│   └─ 输出到 stage3/fscan/
├─ 结果整合
│   ├─ 合并 Nmap + Fscan 结果
│   ├─ 去重（同一 IP:端口 只保留一次）
│   ├─ 提取 Web 端口
│   ├─ 生成端口 URL 并测试
│   └─ 输出到 stage3/combined/
├─ 其他端口测试
│   ├─ SSH, FTP, SMTP, MySQL, RDP, VNC
│   ├─ HTTP/HTTPS 端口测试
│   └─ 输出到 stage3/
└─ 输出到 stage3/
    ↓
[阶段 4] 深度分析
├─ 收集所有可访问的 URL
├─ JS 文件分析（200 状态）
├─ Vue.js 检测
├─ Actuator 检测
├─ 路径爆破测试（200/403）
├─ 智能漏洞分析
└─ 最终报告
```

---

## 📁 输出文件结构（v2.0）

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

## 💡 混合扫描策略详解

### Nmap vs Fscan 对比

| 特性 | Nmap | 魔改 Fscan | 混合策略 |
|------|------|-----------|---------|
| 扫描端口 | 标准 9 个 | Top 1000 | 1000+ |
| 精度 | 高 | 中 | 高 |
| 速度 | 2-3 分钟 | 5-10 分钟 | 7-13 分钟 |
| 特征识别 | 容易 | 避免 | 避免 |
| 服务识别 | ✅ | ✅ | ✅ |
| 并发 | 中 | 高 | 高 |

### 扫描模式对比

```bash
# Nmap 精准扫描（标准端口）
nmap -iL target_ips.txt \
  -p 80,443,8080,8443,3000,5000,8888,9000,9443 \
  -T4 \
  --open \
  -oG output.gnmap

# 魔改 Fscan 快速扫描（Top 1000）
python3 core/port_scanner_custom.py \
  target_ips.txt \
  -p 1-1000 \
  -o output.gnmap \
  -f gnmap \
  -t 100

# 混合扫描（推荐）
./scripts/stage3_port_scan_hybrid.sh example.com
```

### 性能对比

```
Nmap 精准扫描:
100 个 IP × 9 个端口 = 900 次扫描
时间: ~2-3 分钟
精度: 高

魔改 Fscan 快速扫描:
100 个 IP × 1000 个端口 = 100,000 次扫描
时间: ~5-10 分钟
精度: 中

混合策略:
Nmap: 100 × 9 = 900 次 (~2-3 分钟)
Fscan: 100 × 1000 = 100,000 次 (~5-10 分钟)
总计: ~7-13 分钟
覆盖: 100% (标准端口 + Top 1000)
特征: 避免识别 ✅
```

---

## 🔧 端口扫描模式选择

### 快速扫描（默认）

```bash
# 设置扫描模式
export SCAN_MODE="fast"  # Top 1000 + Web 端口

# 使用混合扫描策略
./scripts/stage3_port_scan_hybrid.sh example.com
```

### 全端口扫描（可选）

```bash
# 设置扫描模式
export SCAN_MODE="full"  # 1-65535

# 使用 Nmap 全端口扫描
nmap -iL target_ips.txt \
  -p- \
  -T4 \
  --open \
  -oG output.gnmap
```

### Top 1000 说明

**Top 1000 端口** = 常见服务端口 + 高频应用端口

**包含端口**：
- 系统基础：21, 22, 23, 25, 53, 80, 443
- 邮件服务：110, 143, 25, 587
- 数据库：3306, 3389, 5432
- 远程访问：22, 3389, 5900/5901
- Web 应用：80, 443, 8080, 8443
- 管理后台：5000, 5900, 5901, 5902

**覆盖率**: 约 99% 的常见服务和应用

---

## 📝 使用前准备

### 确认目标域名

在开始信息收集之前，请明确：
- ✅ 目标域名是什么？（如：example.com）
- ✅ 是否有授权测试？
- ✅ 测试范围是什么？（主域名、子域名、IP段）

### 设置变量

```bash
# 方式 1: 命令行参数
./scripts/stage1_subs_collect.sh example.com

# 方式 2: 环境变量
export TARGET="example.com"
./scripts/stage1_subs_collect.sh $TARGET

# 方式 3: 交互式输入
./scripts/src-recon-auto.sh
# 脚本会提示：请输入目标域名:
```

### 配置 FOFA API（可选）

```bash
# 配置 FOFA API
export FOFA_EMAIL="your_email@example.com"  # FOFA 账户邮箱
export FOFA_KEY="your_fofa_api_key"         # FOFA API Key

# 验证配置
if [ -n "$FOFA_EMAIL" ] && [ -n "$FOFA_KEY" ]; then
    echo "[+] FOFA API 已配置"
else
    echo "[!] FOFA API 未配置，将跳过 FOFA 搜索"
    echo "[!] 获取 FOFA Key: https://fofa.info/user/users/info"
fi
```

---

## 🔐 安全提醒

- **遵守法律** - 只在授权范围内测试
- **控制速率** - 避免触发 WAF/封禁（魔改版已优化）
- **保护数据** - 不泄露测试目标信息
- **合规提交** - 通过官方渠道提交漏洞

---

## 🎓 学习资源

- **平台规则**: 补天、漏洞盒子、HackerOne 规则文档
- **实战案例**: 公开的 SRC 漏洞报告
- **工具文档**: 各工具的使用指南（见 docs/ 目录）
- **社区**: 安全客、FreeBuf、看雪论坛
- **茶馆**: [龙虾茶馆](https://github.com/ythx-101/openclaw-qa) - OpenClaw 社区

---

## 📊 版本对比

### v1.0 vs v2.0

| 特性 | v1.0 | v2.0 |
|------|------|------|
| 脚本结构 | 单一自动化脚本 | 分阶段脚本（4 个独立） |
| 端口扫描 | Nmap 单一工具 | 混合策略（Nmap + 魔改 Fscan） |
| 特征识别 | 容易被识别 | 魔改版避免识别 |
| 数据整合 | 手动整合 | 自动整合去重 |
| 输出目录 | 单一目录 | 分阶段目录 |
| 灵活性 | 低 | 高（每阶段可单独运行） |

---

_记住：信息收集是渗透测试的基础，做好收集能事半功倍。🦞_

**v2.0 - 分阶段 + 混合扫描，更灵活、更快速、更隐蔽！🦞**
