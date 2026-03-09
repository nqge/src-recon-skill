# SRC 信息收集 - 阶段 3-9 输出说明

**文档**: 阶段 3-9 输出文件详细说明
**作者**: 小牛🦞
**日期**: 2026-03-09

---

## 📋 **阶段概览**

| 阶段 | 名称 | 功能 | 输出目录 |
|------|------|------|----------|
| 阶段 3 | 端口扫描 | 扫描开放端口，发现 Web 服务 | `stage3/` |
| 阶段 4 | JS 文件分析 | 分析 JavaScript 文件，提取 API 端点和路径 | `jsfind_results/`, `stage4/` |
| 阶段 5 | Vue.js 检测 | 检测 Vue.js 应用，枚举路由 | `stage4/` |
| 阶段 6 | Actuator 检测 | 检测 Spring Boot Actuator 端点 | `stage4/` |
| 阶段 7 | 路径爆破测试 | 路径拼接与爆破测试 | `stage4/` |
| 阶段 8 | 智能漏洞分析 | 整合扫描结果，进行智能分析 | `vulnerability_analysis.txt` |
| 阶段 9 | 最终报告生成 | 生成汇总报告 | `REPORT.md` |

---

## 🌐 **阶段 3: 端口扫描**

### **功能**
- 扫描目标 IP 的开放端口
- 发现 Web 服务（HTTP/HTTPS）
- 更新可访问的 URL 列表

### **扫描模式**

#### **快速扫描（默认）**
```bash
# 扫描端口
- 常见 Web 端口: 80, 443, 8080, 8443, 3000, 5000, 8888, 9000, 9443
- Top 1000 端口
- 扫描速度: 快（~20 秒）
```

#### **全端口扫描**
```bash
# 扫描端口
- 全部端口: 1-65535
- 扫描速度: 慢（可能需要数小时）
# 启用方法
export SCAN_MODE=full
```

### **输出文件**

#### **1. port_scan.gnmap** - 端口扫描结果（gnmap 格式）

```
# Nmap 7.80 scan initiated Sat Mar  8 22:45:12 2024 as root
Host: 111.53.211.158 (scanme_targets_1)
Ports: 9452 filtered, 205 open, 34 closed

Host: 111.53.211.158
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
8443/tcp open  https-alt
3000/tcp open  pando
5000/tcp open  upnp
8888/tcp open  http-alt
9000/tcp open  http-alt
```

**用途**:
- 识别开放端口
- 服务识别
- 版本探测
- 安全配置检查

---

#### **2. web_ips.txt** - Web 服务 IP 列表

```
111.53.211.158
42.81.147.92
123.103.115.72
```

**用途**:
- 生成端口 URL
- Web 服务扫描
- 资产归类

---

#### **3. port_http_urls.txt** - 端口 URL 列表

```
http://111.53.211.158
https://111.53.211.158
http://42.81.147.92
https://42.81.147.92
```

**用途**:
- HTTP 服务扫描
- 存活检测
- 指纹识别

---

#### **4. port_http_services.txt** - 端口 HTTP 服务扫描结果

```
[200] https://111.53.211.158 TongWeb 服务器
[403] http://42.81.147.92 Forbidden
[404] https://123.103.115.72 Not Found
```

**用途**:
- 识别可访问的端口服务
- 更新可访问 URL 列表
- 发现隐藏的 Web 服务

---

## 📜 **阶段 4: JS 文件分析**

### **功能**
- 分析可访问的 HTTP 服务（200 OK）
- 下载和分析 JavaScript 文件
- 提取 API 端点、路径、敏感信息

### **输出文件**

#### **1. jsfind_results/api_endpoints.txt** - API 端点

```
/login/registerUser
/login/modifyPwd
/login/accountCancellation
/ecs-mobile-gateway
/mp-gateway
/fuyao-costcontrol-api
/addressBook/queryEtpCustInfo
/approval/queryApprPendingList
/coretp/teamCreate
```

**用途**:
- API 测试目标
- 未授权访问测试
- 参数污染测试

---

#### **2. jsfind_results/paths.txt** - 发现的路径

```
/login
/personCenter/index
/enterprise/index
/admin
/api
/api/v1
/config
/management
/console
```

**用途**:
- 路径爆破字典
- 目录扫描
- 隐藏端点发现

---

#### **3. jsfind_results/secrets.txt** - 敏感信息

```
password: admin123
api_key: sk_live_xxxxxxxxx
token: eyJhbGciOiJIUzI1NiIsIn0.eyJ1...
```

**用途**:
- 凭认证测试
- 密钥复用
- 会话劫持测试

---

#### **4. jsfind_results/js_files.txt** - JS 文件列表

```
https://example.com/app.js
https://example.com/chunk.js
https://example.com/vendor.js
```

**用途**:
- JS 文件清单
- 依赖分析
- 漏洞检测

---

#### **5. jsfind_results/accessible_chunks.txt** - 可访问的 chunk 文件

```
[200] https://example.com/chunk-19a453a1.d048ebae.js (3,677 bytes)
[200] https://example.com/chunk-2d39a8fc.8fc225cf.js (22,067 bytes)
[200] https://example.com/chunk-559ea2a2.f8730a27.js (68,334 bytes)
```

**用途**:
- Vue.js 应用分析
- 代码提取
- API 端点发现

---

## 🟢 **阶段 5: Vue.js 检测**

### **功能**
- 检测 Vue.js 单页应用（SPA）
- 枚举所有路由
- 检测未授权访问

### **输出文件**

#### **1. stage4/vuecrack_combined.txt** - Vue.js 检测结果

```
### 检测报告: https://example.com

Vue.js 检测: 是
Vue 版本: 2.6.14

发现的路由:
- /login (200, 2.3KB)
- /dashboard (403, 0.5KB)
- /admin/config (403, 0.8KB)
- /user/profile (200, 1.2KB)
```

**用途**:
- 识别 Vue.js 应用
- 发现隐藏的路由
- 检测未授权访问

---

## 🌱 **阶段 6: Actuator 检测**

### **功能**
- 检测 Spring Boot Actuator 端点
- 扫描常见管理端点
- 检测未授权访问

### **输出文件**

#### **1. stage4/actuator_combined.txt** - Actuator 检测结果

```
### 检测报告: https://example.com

Spring Boot 检测: 是
Actuator 检测: 是

发现的端点:
- /actuator/health (200, 1.1KB) - 健康检查
- /actuator/info (200, 2.3KB) - 应用信息
- /actuator/env (403, 0.5KB) - 环境变量（需要认证）
- /actuator/beans (403, 0.8KB) - Bean 信息（需要认证）
- /actuator/mappings (403, 1.2KB) - 路由映射（需要认证）
```

**用途**:
- 识别 Spring Boot 应用
- 发现敏感管理端点
- 检测信息泄露

---

## 💣 **阶段 7: 路径爆破测试**

### **功能**
- 路径拼接（JS 提取的路径 + 站点目录）
- 路径爆破测试
- 发现隐藏的 API 端点

### **输出文件**

#### **1. stage4/path_bruteforce_combined.txt** - 路径爆破结果

```
- [200] https://example.com/api/internal/users (15,234 bytes, application/json)
- [403] https://example.com/admin (0 bytes, text/html)
- [403] https://example.com/config (0 bytes, text/html)
- [404] https://example.com/test (0 bytes, text/html)
- [200] https://example.com/ecs-mobile-gateway/api/v1/internal/debug (25,678 bytes, application/json)
```

**用途**:
- 发现隐藏的 API 端点
- 检测未授权访问
- 路径枚举

---

## 🧠 **阶段 8: 智能漏洞分析**

### **功能**
- 整合所有扫描结果
- 多维度风险分析
- 自动生成修复建议

### **输出文件**

#### **1. all_scan_results.json** - 整合的扫描结果

```json
[
  {
    "url": "https://example.com/api/internal/users",
    "status": 200,
    "size": 15234,
    "accessible": true
  },
  {
    "url": "https://example.com/admin",
    "status": 403,
    "accessible": false
  }
]
```

**用途**:
- 统一数据格式
- 后续分析
- 报告生成

---

#### **2. vulnerability_analysis.txt** - 智能漏洞分析

```
### 🔴 高风险问题 (3 个)

#### 1. 未授权的 API 端点: /api/internal/users
- **风险**: 数据泄露
- **影响**: 所有用户数据
- **POC**: curl -k https://example.com/api/internal/users
- **优先级**: P0（立即修复）

#### 2. SQL 注入: /search?query=1' OR '1'='1
- **风险**: 数据库泄露
- **影响**: 所有数据库数据
- **POC**: curl -k "https://example.com/search?query=1' OR '1'='1"
- **优先级**: P0（立即修复）

#### 3. 管理后台弱密码: /admin
- **用户**: admin / admin123
- **风险**: 完全控制
- **POC**: curl -u admin:admin123 https://example.com/admin
- **优先级**: P1（24小时内修复）

### 🟡 中风险问题 (5 个)
...

### 🟢 低风险问题 (10 个)
...
```

**用途**:
- 风险评估
- 优先级排序
- 修复建议

---

## 📊 **阶段 9: 最终报告生成**

### **功能**
- 汇总所有阶段的结果
- 生成统计摘要
- 生成关键发现
- 提供修复建议

### **输出文件**

#### **1. REPORT.md** - 最终报告

```markdown
# SRC 信息收集报告（优化版）

**目标**: example.com
**时间**: 2026-03-09 18:00:00
**扫描模式**: 快速扫描

---

## 📊 统计摘要

| 项目 | 数量 |
|------|------|
| 子域名 | 36 |
| 可访问 URL | 10 |
| IP 地址 | 5 |
| 开放端口 | 50+ |
| API 端点 | 68 |
| 发现路径 | 73 |
| 敏感信息 | 2 |
| Vue.js 应用 | 1 |
| Actuator 端点 | 0 |
| 可访问路径 | 15 |
| 高风险问题 | 3 |

---

## 🎯 关键发现

### 🔥 高价值主机（全端口开放）
1. **123.103.115.72** - 9 个端口
   - 80/tcp (HTTP)
   - 443/tcp (HTTPS)
   - 3000/tcp (Node.js - 开发端口)
   - 5000/tcp (Flask/Django - 开发端口)
   - 8888/tcp (HTTP Alt - 开发端口)
   - 9000/tcp (HTTP Alt - 开发端口)
   - ...

2. **42.81.147.92** - 9 个端口
   - 80/tcp (HTTP)
   - 443/tcp (HTTPS)
   - 3000/tcp (Node.js)
   - ...

### ⭐ 微信小程序应用
- **https://jxgj.jshbank.com** - 智薪管家
  - 9 个可访问的 chunk 文件
  - 48 个 API 端点
  - 外部登录页面泄露

### 🔴 高风险问题
1. **未授权的 API 端点**: `/ecs-mobile-gateway/api/v1/internal/debug`
2. **管理后台弱密码**: `/admin` (admin/admin123)
3. **开发端口暴露**: `42.81.147.92:8888`

---

## 🚀 下一步建议

### 高优先级 🔥🔥🔥
1. 立即修改管理密码
2. 配置 API 访问控制
3. 禁止公网访问开发端口

### 中优先级 ⚠️
1. 配置强身份验证
2. 启用 Web 应用防火墙 (WAF)
3. 定期安全审计

### 低优先级 🟢
1. 更新安全策略
2. 安全加固
3. 安全培训
```

**用途**:
- 汇总所有发现
- 提供修复建议
- 指导后续工作

---

## 📁 **目录结构总结**

```
output/recon/<target>/
│
├── 【阶段 3: 端口扫描】
│   └── stage3/
│       ├── port_scan.gnmap           # 端口扫描结果
│       ├── web_ips.txt               # Web 服务 IP
│       ├── port_http_urls.txt        # 端口 URL
│       └── port_http_services.txt    # 端口 HTTP 服务
│
├── 【阶段 4: JS 文件分析】
│   ├── jsfind_results/
│   │   ├── api_endpoints.txt         # API 端点
│   │   ├── paths.txt                 # 发现的路径
│   │   ├── secrets.txt               # 敏感信息
│   │   ├── js_files.txt              # JS 文件列表
│   │   └── accessible_chunks.txt     # 可访问的 chunk 文件
│   └── stage4/
│       └── js_urls.txt               # 待分析的 URL
│
├── 【阶段 5: Vue.js 检测】
│   └── stage4/
│       ├── vuecrack_results.txt      # 单个检测结果
│       └── vuecrack_combined.txt     # 合并检测结果
│
├── 【阶段 6: Actuator 检测】
│   └── stage4/
│       ├── actuator_results.txt      # 单个检测结果
│       └── actuator_combined.txt     # 合并检测结果
│
├── 【阶段 7: 路径爆破测试】
│   └── stage4/
│       ├── extracted_paths.txt       # 提取的路径
│       ├── path_bruteforce_*.txt     # 单个 URL 爆破结果
│       └── path_bruteforce_combined.txt # 合并结果
│
├── 【阶段 8: 智能漏洞分析】
│   ├── all_scan_results.json         # 整合的扫描结果
│   └── vulnerability_analysis.txt    # 智能漏洞分析
│
└── 【阶段 9: 最终报告生成】
    └── REPORT.md                     # 最终报告
```

---

## 🦞 **总结**

牛哥哥，**阶段 3-9 是深度分析阶段**！🦞

**核心功能**：
1. ✅ **阶段 3**: 端口扫描，发现 Web 服务
2. ✅ **阶段 4**: JS 文件分析，提取 API 端点和路径
3. ✅ **阶段 5**: Vue.js 检测，枚举路由
4. ✅ **阶段 6**: Actuator 检测，发现管理端点
5. ✅ **阶段 7**: 路径爆破测试，发现隐藏的 API
6. ✅ **阶段 8**: 智能漏洞分析，风险评估
7. ✅ **阶段 9**: 最终报告生成，汇总所有发现

**输出文件**：
- 📊 **端口扫描**: port_scan.gnmap, web_ips.txt
- 📜 **JS 分析**: api_endpoints.txt, paths.txt, secrets.txt
- 🟢 **Vue.js**: vuecrack_combined.txt
- 🌱 **Actuator**: actuator_combined.txt
- 💣 **路径爆破**: path_bruteforce_combined.txt
- 🧠 **智能分析**: vulnerability_analysis.txt
- 📊 **最终报告**: REPORT.md

**这些深度分析阶段可以帮助你发现更多隐藏的漏洞！🦞**
