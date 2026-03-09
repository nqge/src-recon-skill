# src-recon-skill - 项目结构说明

## 📁 目录结构

```
src-recon-skill/
├── core/                   # 核心工具（11 个 Python 工具）
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
│   ├── src-recon-auto.sh           # 主自动化脚本
│   └── src-recon-auto-new.sh       # 新版脚本（开发中）
│
├── docs/                   # 文档（15 个文档文件）
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
├── utils/                  # 工具函数（预留）
│   └── .gitkeep
│
├── output/                 # 输出目录
│   └── recon/                     # 扫描结果
│       └── example/               # 示例输出
│
├── LICENSE                 # MIT 许可证
├── requirements.txt        # Python 依赖
├── .gitignore             # Git 忽略规则
└── README.md              # 项目说明
```

---

## 📂 各目录说明

### core/ - 核心工具

存放所有 Python 工具脚本，每个工具负责特定的安全测试任务。

**工具列表**：
1. auth_session_manager.py - 认证会话管理
2. oneforall_subs.py - OneForAll 子域名收集
3. fofa_subs.py - FOFA 子域名收集
4. http_scanner.py - HTTP 服务扫描
5. http_scanner_enhanced.py - 增强版 HTTP 扫描
6. jsfind.py - JavaScript 文件分析
7. vuecrack.py - Vue.js 应用检测
8. actuator_scanner.py - Spring Boot Actuator 检测
9. js_path_extractor.py - JS 路径提取
10. path_bruteforcer.py - 路径爆破测试
11. vulnerability_analyzer.py - 智能漏洞分析

### scripts/ - 自动化脚本

存放自动化脚本，整合所有工具实现一键扫描。

**脚本**：
- src-recon-auto.sh - 完整的自动化扫描脚本（12 阶段）

### docs/ - 文档

存放所有文档文件，包括使用指南、配置指南等。

**文档分类**：
- 使用指南：SKILL.md, README.md
- 配置指南：FOFA_SETUP.md, ONEFORALL_SETUP.md
- 工具指南：HTTP_SCANNER.md, JSFIND.md, VUECRACK.md 等

### wordlists/ - 字典文件

存放扫描用的字典文件。

**字典**：
- wordlists.txt - 子域名字典
- dirs.txt - 目录字典

### utils/ - 工具函数

预留的工具函数目录，可以存放公共函数、辅助脚本等。

### output/ - 输出目录

存放所有扫描结果。

**结构**：
```
output/
└── recon/
    └── example.com/
        ├── all_subs.txt
        ├── http_services.txt
        ├── port_scan.gnmap
        └── ...
```

---

## 🚀 使用方式

### 使用单个工具

```bash
# 进入 core 目录
cd core/

# 运行工具
python3 fofa_subs.py example.com
python3 http_scanner.py urls.txt results.txt
```

### 使用自动化脚本

```bash
# 运行完整扫描
./scripts/src-recon-auto.sh example.com

# 查看结果
ls output/recon/example.com/
```

---

## 📝 维护指南

### 添加新工具

1. 将工具放入 `core/` 目录
2. 在 `docs/` 中添加使用文档
3. 如需集成，更新 `scripts/src-recon-auto.sh`

### 添加新字典

1. 将字典放入 `wordlists/` 目录
2. 在工具中引用：`$WORDLISTS_DIR/your_dict.txt`

### 更新文档

1. 编辑 `docs/` 中的相应文档
2. 更新 README.md 中的工具列表

---

_项目结构清晰，层次分明，便于维护和扩展。🦞_
