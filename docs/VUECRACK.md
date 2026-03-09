# VueCrack - Vue.js 应用安全检测工具

## 📖 功能说明

`vuecrack.py` 是一个专门用于检测 Vue.js 应用未授权访问和敏感路由的工具。

### 核心功能

- **Vue.js 框架检测** - 自动识别站点是否使用 Vue.js
- **路由提取** - 从 JS 文件中提取 Vue Router 配置的路由
- **路由验证** - 验证路由的可访问性
- **敏感端点发现** - 发现常见的敏感管理端点
- **详细报告** - 生成包含状态码、内容大小的详细报告

---

## 🎯 为什么需要 VueCrack？

### Vue.js 应用的特点

1. **前端路由** - 所有路由在前端定义，不一定在服务器端验证
2. **代码分割** - 代码按路由分割成 chunk 文件
3. **未授权访问** - 可能存在未授权访问的管理界面
4. **敏感信息** - 路由配置可能包含敏感端点

### 常见风险

```
/admin          - 管理界面
/dashboard      - 仪表板
/config         - 配置页面
/debug          - 调试接口
/api/internal   - 内部 API
```

---

## 🚀 使用方式

### 基本用法

```bash
# 分析站点列表
python3 vuecrack.py sites.txt

# 指定输出文件
python3 vuecrack.py sites.txt vue_report.txt
```

### 站点列表格式

创建 `sites.txt`：

```
https://example.com
https://admin.example.com
https://app.example.com
```

### 在自动化流程中使用

```bash
# 在 src-recon-auto.sh 中自动调用
./src-recon-auto.sh example.com
```

脚本会自动对 200 状态的站点运行 VueCrack。

---

## 📊 输出示例

### 控制台输出

```
[*] 正在扫描: https://example.com
    [*] 检测 Vue.js 框架...
    [+] 检测到 Vue.js 框架
    [*] 从 JS 文件中提取路由...
    [+] 发现 25 个路由
    [*] 添加常见路由...
    [*] 总共检查 87 个路由...
        进度: 20/87
        进度: 40/87
        进度: 60/87
        进度: 80/87
        进度: 87/87
    [+] 可访问路由: 12
    [+] 需要认证: 8
    [+] 其他: 67
```

### vuecrack_report.txt

```
# VueCrack 扫描报告

**时间**: 2026-03-09 15:00:00
**Vue.js 检测**: 是

**统计信息**:
- 可访问路由: 12
- 需要认证: 8
- 其他状态: 67

## ✅ 可访问路由 (200 OK)

- [200] https://example.com/admin
  路由: /admin
  大小: 45678 bytes
  Content-Type: text/html

- [200] https://example.com/dashboard
  路由: /dashboard
  大小: 23456 bytes
  Content-Type: text/html

- [200] https://example.com/config
  路由: /config
  大小: 12345 bytes
  Content-Type: application/json

## ⚠️  需要认证 (401/403)

- [403] https://example.com/settings
  路由: /settings

- [401] https://example.com/api/keys
  路由: /api/keys

## ❌ 其他状态

- [404] https://example.com/test
  路由: /test
```

---

## 🔍 检测原理

### 1. Vue.js 框架检测

使用多种指纹识别 Vue.js：

```python
# HTML 结构
<div id="app">

# JS 指纹
vue-router
__vue__
Vue.createApp

# HTTP 头
X-Powered-By: Vue
```

### 2. 路由提取

#### 从 JS 文件提取

```python
# Vue Router 3
path: '/admin'

# Vue Router 4
{"path": "/dashboard"}

# 路由数组
routes: [{ path: '/config' }]
```

#### 常见路由字典

```python
COMMON_ROUTES = [
    '/admin', '/dashboard', '/settings', '/config',
    '/debug', '/test', '/internal', '/management',
    '/console', '/panel', '/control', '/monitor',
    # ... 更多
]
```

### 3. 路由验证

```python
# 发送请求
response = requests.get(url, allow_redirects=True)

# 记录结果
{
    'status': response.status_code,
    'size': len(response.content),
    'content_type': response.headers.get('Content-Type'),
    'location': response.headers.get('Location', '')
}
```

---

## 💡 实战价值

### 1. 发现未授权访问的管理界面

```bash
# 运行扫描
python3 vuecrack.py target.txt

# 查看可访问路由
cat vuecrack_report.txt | grep "200]"
```

发现：
```
[200] /admin
[200] /dashboard
[200] /config
```

### 2. 发现敏感 API

```bash
# 查看 JSON 响应
curl https://example.com/api/internal
```

### 3. 发现配置信息

```bash
# 访问配置端点
curl https://example.com/config | jq
```

---

## 🎯 典型工作流程

```
发现 200 状态站点
    ↓
[检测 Vue.js 框架]
    ↓
[提取 JS 文件中的路由]
    ↓
[添加常见敏感路由]
    ↓
[并发验证可访问性]
    ↓
[生成详细报告]
    ↓
[进一步漏洞挖掘]
```

---

## 🔧 与其他工具配合

### 配合 JSFind

```bash
# 先用 JSFind 分析
python3 jsfind.py sites.txt

# 再用 VueCrack 检测 Vue 应用
python3 vuecrack.py sites.txt
```

### 配合 Nuclei

```bash
# 对可访问路由进行漏洞扫描
cat vuecrack_report.txt | grep "200]" | awk '{print $2}' | nuclei -l -
```

---

## 📝 实战案例

### 案例 1：发现管理后台

```bash
python3 vuecrack.py target.txt
```

发现：
```
[200] https://example.com/admin
  路由: /admin
  大小: 45678 bytes

[200] https://example.com/user/list
  路由: /user/list
  大小: 12345 bytes
```

访问 `https://example.com/admin` 发现完整的用户管理界面。

### 案例 2：发现调试接口

```bash
cat vuecrack_report.txt | grep "debug"
```

发现：
```
[200] https://example.com/debug
  路由: /debug
  大小: 5678 bytes

[200] https://example.com/__webpack_dev_server__
  路由: /__webpack_dev_server__
  大小: 2345 bytes
```

---

## 🔐 安全提醒

- **授权测试** - 只检测有授权的目标
- **合法访问** - 发现的管理界面需要进一步授权测试
- **负责任披露** - 通过官方渠道报告发现的漏洞

---

_工具由小牛的 SRC 信息收集技能提供 🦞_
