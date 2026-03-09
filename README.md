# src-recon-skill

SRC 众测平台信息收集技能包 - 从子域名枚举到智能漏洞分析，一键完成资产收集和风险识别。

## 📁 项目结构

```
src-recon-skill/
├── core/                   # 核心工具
│   ├── auth_session_manager.py      # 认证会话管理器
│   ├── oneforall_subs.py            # OneForAll 子域名收集
│   ├── fofa_subs.py                 # FOFA 子域名收集
│   ├── http_scanner.py              # HTTP/HTTPS 服务扫描
│   ├── http_scanner_enhanced.py     # 增强版 HTTP 扫描
│   ├── jsfind.py                    # JavaScript 文件分析
│   ├── vuecrack.py                  # Vue.js 应用检测
│   ├── actuator_scanner.py          # Spring Boot Actuator 检测
│   ├── js_path_extractor.py         # JS 路径提取
│   ├── path_bruteforcer.py          # 路径爆破测试
│   └── vulnerability_analyzer.py    # 智能漏洞分析
│
├── scripts/                # 自动化脚本
│   └── src-recon-auto.sh           # 主自动化脚本
│
├── docs/                   # 文档
│   ├── SKILL.md                    # 完整使用指南
│   ├── README.md                   # 项目介绍
│   ├── ONEFORALL_SETUP.md          # OneForAll 配置
│   ├── FOFA_SETUP.md               # FOFA API 配置
│   ├── AUTH_SESSION_MANAGER.md     # 认证管理指南
│   ├── HTTP_SCANNER.md             # HTTP 扫描指南
│   ├── JSFIND.md                   # JS 分析指南
│   ├── JSFIND_CHUNK.md             # Chunk 提取指南
│   ├── VUECRACK.md                 # Vue.js 指南
│   ├── ACTUATOR_SCANNER.md         # Actuator 指南
│   ├── JS_PATH_EXTRACTOR.md        # JS 路径提取指南
│   ├── VULNERABILITY_ANALYZER.md   # 智能分析指南
│   ├── PATH_BRUTEFORCE_REPORT.md   # 路径爆破说明
│   ├── CONCURRENCY_SETTINGS.md     # 并发配置说明
│   └── CONTRIBUTING.md             # 贡献指南
│
├── wordlists/              # 字典文件
│   ├── wordlists.txt               # 子域名字典
│   └── dirs.txt                    # 目录字典
│
├── output/                 # 输出目录
│   └── .gitkeep
│
├── recon/                 # 扫描结果（运行时生成）
│   └── example/
│
├── LICENSE                 # MIT 许可证
├── requirements.txt        # Python 依赖
└── .gitignore             # Git 忽略规则
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

```bash
# 使用自动化脚本
./scripts/src-recon-auto.sh example.com

# 查看结果
ls recon/example.com/
```

---

## 📚 文档

- **SKILL.md** - 完整的使用指南和流程
- **README.md** - 项目介绍

---

**生成工具**: 小牛的 SRC 信息收集技能 🦞
