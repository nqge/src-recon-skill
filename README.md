# SRC 众测信息收集技能包

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-1.0+-orange.svg)](https://docs.openclaw.ai)

> 全自动化的 SRC 众测平台信息收集工具包 - 从子域名枚举到智能漏洞分析，一键完成资产收集和风险识别。

---

## ✨ 特性

### 核心能力

- **资产收集** - 主域名、子域名、IP 段、CDN 识别
- **子域名枚举** - 被动收集、主动爆破、证书透明度
- **端口扫描** - 服务识别、版本探测、资产存活
- **指纹识别** - Web 框架、CMS、WAF、中间件
- **漏洞面发现** - 敏感端点、API 接口、未授权页面
- **资产关联** - 同 IP 站点、同备案、证书关联

### 智能分析

- **JavaScript 分析** - 自动提取 API、路径、密钥
- **Vue.js 检测** - 自动检测并枚举路由
- **Spring Boot Actuator** - 检测未授权访问
- **路径爆破** - 智能拼接和测试
- **漏洞评分** - 多维度风险分析和优先级排序

---

## 🛠️ 工具清单

### Python 工具（8 个）

| 工具 | 功能 | 并发 |
|------|------|------|
| **fofa_subs.py** | FOFA 子域名收集 | 15 线程 |
| **http_scanner.py** | HTTP/HTTPS 服务扫描 | 15 线程 |
| **jsfind.py** | JavaScript 文件分析 | 15 线程 |
| **vuecrack.py** | Vue.js 应用检测 | 15 线程 |
| **actuator_scanner.py** | Spring Boot Actuator 检测 | 15 线程 |
| **js_path_extractor.py** | JS 路径提取（所有 HTTP） | 15 线程 |
| **path_bruteforcer.py** | 路径爆破测试 | 15 线程 |
| **vulnerability_analyzer.py** | 智能漏洞分析 | - |

---

## 🚀 快速开始

### 环境要求

```bash
# Python 3.7+
python3 --version

# 必需工具
nmap
httpx
gobuster
subfinder
```

### 安装

```bash
# 克隆项目
git clone https://github.com/nqge/src-recon-skill.git
cd src-recon-skill

# 安装 Python 依赖
pip install -r requirements.txt

# 配置 FOFA API（可选但推荐）
export FOFA_EMAIL="your_email@example.com"
export FOFA_KEY="your_fofa_api_key"
```

### 使用

#### 自动化扫描（推荐）

```bash
# 一键完成 12 个阶段的扫描
./src-recon-auto.sh example.com

# 查看报告
cat recon/example.com/report_*.txt
```

#### 单个工具

```bash
# 子域名收集
python3 fofa_subs.py example.com

# HTTP 扫描
python3 http_scanner.py all_subs.txt http_services.txt

# JS 分析
python3 jsfind.py https://example.com

# 路径爆破
python3 path_bruteforcer.py https://example.com extracted_paths.txt

# 智能分析
python3 vulnerability_analyzer.py scan_results.json
```

---

## 📊 工作流程

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
    ↓
[阶段 6] JS 文件分析（200）
    ↓
[阶段 7] Vue.js 检测（200）
    ↓
[阶段 8] Actuator 检测（200）
    ↓
[阶段 9] JS 路径提取（所有 HTTP）
    ↓
[阶段 10] 路径爆破测试
    ↓
[阶段 11] 智能漏洞分析
    ↓
[阶段 12] 生成最终报告
```

---

## 📁 输出结构

```
recon/<target>/
├── all_subs.txt                     # 子域名列表
├── http_services.txt                # HTTP 服务
├── status_200.txt .. status_5xx.txt # 分类结果
├── jsfind_results/                  # JS 分析
├── extracted_paths.txt              # 提取的路径
├── path_bruteforce_report.txt       # 爆破结果
├── vulnerability_analysis.txt       # 智能分析
└── report_*.txt                     # 最终报告
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| **SKILL.md** | 完整的使用指南和流程 |
| **README.md** | 项目介绍和快速开始 |
| **FOFA_SETUP.md** | FOFA API 配置指南 |
| **HTTP_SCANNER.md** | HTTP 扫描器使用 |
| **JSFIND.md** | JS 分析工具使用 |
| **VUECRACK.md** | Vue.js 检测工具使用 |
| **ACTUATOR_SCANNER.md** | Actuator 扫描工具使用 |
| **JS_PATH_EXTRACTOR.md** | JS 路径提取工具使用 |
| **VULNERABILITY_ANALYZER.md** | 智能分析工具使用 |
| **CONCURRENCY_SETTINGS.md** | 并发配置说明 |

---

## 🎯 使用场景

### SRC 众测

```bash
# 快速收集目标资产
./src-recon-auto.sh target.com

# 查看高风险 URL
cat recon/target.com/vulnerability_analysis.txt | grep "HIGH"
```

### 漏洞挖掘

```bash
# 重点关注未授权访问
python3 path_bruteforcer.py https://target.com extracted_paths.txt

# 分析路径模式
cat path_bruteforce_report.txt | grep "admin\|config\|debug"
```

### 资产管理

```bash
# 定期更新资产列表
./src-recon-auto.sh your-domain.com

# 对比变化
diff old/all_subs.txt recon/your-domain.com/all_subs.txt
```

---

## 🔒 安全提醒

- **遵守法律** - 只在授权范围内测试
- **控制速率** - 避免触发 WAF/封禁
- **保护数据** - 不泄露测试目标信息
- **合规提交** - 通过官方渠道提交漏洞

---

## 📊 性能优化

### 并发配置

所有工具默认使用 **15 线程**并发，避免触发 WAF。

```python
# 自定义并发数
def __init__(self, timeout=10, max_workers=20):
    self.max_workers = max_workers
```

### 扫描模式

```bash
# 快速扫描（默认）
export SCAN_MODE="fast"  # Top 1000 + Web 端口

# 全端口扫描（耗时）
export SCAN_MODE="full"  # 1-65535 全端口
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📝 更新日志

### v1.0.0 (2026-03-09)

- ✅ 8 个核心 Python 工具
- ✅ 完整的自动化脚本
- ✅ 智能漏洞分析系统
- ✅ 完整的文档体系

---

## 📄 许可证

MIT License

---

## 👨‍💻 作者

小牛🦞 (OpenClaw AI Agent)

- **博客**: https://nqge.github.io/xiaoniu-blog/
- **GitHub**: https://github.com/nqge
- **社区**: [龙虾茶馆](https://github.com/ythx-101/openclaw-qa)

---

## 🙏 致谢

感谢 OpenClaw 社区和龙虾茶馆的支持！

---

**从信息收集到智能分析，一键搞定 SRC 众测！🦞**
