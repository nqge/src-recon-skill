# JS 路径提取器使用指南

## 📖 功能说明

`js_path_extractor.py` 是一个强大的 JavaScript 文件路径提取工具，专门用于从站点的 JS 文件中提取所有可能的 API 端点和路径。

### 核心特点

**即使站点是空白页面或返回 400 状态，只要能访问 JS 文件就进行提取！**

- **JS 文件发现** - 自动发现站点中的所有 JS 文件
- **路径提取** - 使用多种正则表达式提取路径
- **所有 HTTP 服务** - 对所有发现的 HTTP/HTTPS 服务进行提取
- **空白页面友好** - 即使站点无内容也能从 JS 提取
- **错误状态友好** - 即使 400/403/500 也尝试提取

---

## 🎯 为什么需要这个工具？

### 问题场景

1. **空白 SPA 应用** - 前端是空白页面，所有内容在 JS 中
2. **400 错误页面** - 站点返回 400，但 JS 文件可访问
3. **未授权访问** - 主页面不可访问，但 JS 文件公开
4. **API 优先** - 没有前端界面的纯 API 服务

### 解决方案

直接访问 JS 文件，从中提取所有可能的路径：
```javascript
// 从 JS 中提取
fetch('/api/v1/users')
axios.post('/admin/config')
router.get('/internal/debug')
```

---

## 🚀 使用方式

### 基本用法

```bash
# 从 URL 列表提取路径
python3 js_path_extractor.py urls.txt

# 指定输出文件
python3 js_path_extractor.py urls.txt paths.txt
```

### URL 列表格式

创建 `urls.txt`：

```
https://example.com
https://blank.example.com
https://api.example.com
https://error.example.com
```

### 在自动化流程中使用

```bash
# 在 src-recon-auto.sh 中自动调用
./src-recon-auto.sh example.com
```

阶段 4.5 会自动对所有 HTTP 服务进行路径提取。

---

## 📊 输出示例

### 控制台输出

```
[*] 正在扫描: https://example.com
    [*] 发现 JS 文件...
    [+] 发现 8 个 JS 文件
    [*] 提取路径...
      app.js: 123 个路径
      main.js: 45 个路径
      chunk-abc.js: 67 个路径
      vendor.js: 234 个路径
    [+] 总共提取 469 个路径

[+] 结果已保存:
    - extracted_paths.txt: 469 个路径
    - js_files_scanned.txt: 8 个 JS 文件
```

### extracted_paths.txt

```
/api/v1/users
/api/v1/admin/config
/admin/dashboard
/internal/debug
/graphql
/auth/login
/auth/register
/user/profile
/settings/general
...
```

### js_files_scanned.txt

```
https://example.com/app.js
https://example.com/main.js
https://example.com/chunk-abc.js
https://example.com/vendor.js
...
```

---

## 🔍 提取模式

### 基本路径模式

```python
# 提取所有可能的路径
r'/(?:[\w-]+/)*[\w-]+'
```

### API 端点模式

```python
# REST API
r'["\']/(?:api|v1|v2|v3)[/\w-]*["\']'

# Router 配置
r'path:\s*["\']([^"\']+)["\']'
r'route:\s*["\']([^"\']+)["\']'

# Fetch/Axios 调用
r'fetch\(["\']([^"\']+)["\']'
r'axios\.(?:get|post|put|delete)\(["\']([^"\']+)["\']'
```

### Java Spring 模式

```python
# Spring 注解
r'@GetMapping\(["\']([^"\']+)["\']'
r'@PostMapping\(["\']([^"\']+)["\']'
r'@RequestMapping\(["\']([^"\']+)["\']'
```

---

## 💡 实战价值

### 1. 空白页面挖洞

站点访问是空白，但 JS 文件可访问：

```bash
# 发现 JS 文件
https://example.com/app.js

# 提取路径
/api/v1/admin
/internal/debug
/graphql
```

### 2. 400 错误页面挖洞

主页面返回 400，但 JS 文件正常：

```bash
# 尝试访问提取的路径
curl https://example.com/api/v1/admin
curl https://example.com/internal/debug
```

### 3. API 端点发现

从 JS 文件中提取未公开的 API：

```python
# 提取的 API
/api/v1/users/export
/api/v1/logs/download
/admin/config
```

---

## 🎯 工作流程

```
发现所有 HTTP/HTTPS 服务
    ↓
[对每个服务尝试访问]
    ↓
[发现 JS 文件]
    ├─ 从 HTML 提取
    └─ 尝试常见路径
    ↓
[提取 JS 内容]
    ↓
[正则表达式提取路径]
    ├─ 基本路径
    ├─ API 端点
    ├─ Router 配置
    ├─ Fetch/Axios 调用
    └─ Spring 注解
    ↓
[保存所有路径]
    ↓
[进一步验证或扫描]
```

---

## 🔧 与其他工具配合

### 配合 nuclei 验证

```bash
# 对提取的路径进行验证
cat extracted_paths.txt | nuclei -u https://example.com -l -
```

### 配合 ffuzz 模糊测试

```bash
# 对发现的 API 进行模糊测试
ffuf -u https://example.com/FUZZ -w extracted_paths.txt
```

### 配合 sqlmap 注入测试

```bash
# 对发现的参数进行注入测试
cat extracted_paths.txt | grep "?" | while read url; do
    sqlmap -u "$url"
done
```

---

## 📝 使用技巧

### 1. 过滤路径

```bash
# 只看 API 端点
grep "^/api" extracted_paths.txt

# 只看管理端点
grep -E "(admin|debug|internal)" extracted_paths.txt
```

### 2. 去重和排序

```bash
# 去重并排序
sort -u extracted_paths.txt > unique_paths.txt
```

### 3. 分类统计

```bash
# 按前缀分类
grep -c "^/api" extracted_paths.txt
grep -c "^/admin" extracted_paths.txt
grep -c "^/v1" extracted_paths.txt
```

---

## 🔐 安全提醒

- **授权测试** - 只提取有授权的目标的路径
- **合法访问** - 提取的路径需要进一步验证才能访问
- **负责任披露** - 通过官方渠道报告发现的漏洞
- **不要滥用** - 不要对所有路径进行无差别攻击

---

## 🎯 典型使用场景

### 场景 1：SPA 应用信息收集

```bash
# 发现空白 SPA 应用
curl https://example.com
# 返回空白页面

# 提取路径
python3 js_path_extractor.py https://example.com

# 验证发现的路由
for path in $(head -20 extracted_paths.txt); do
    curl https://example.com$path
done
```

### 场景 2：API 端点收集

```bash
# 提取所有 API 端点
grep "^/api" extracted_paths.txt > api_endpoints.txt

# 验证可访问性
nuclei -u https://example.com -l api_endpoints.txt
```

---

_工具由小牛的 SRC 信息收集技能提供 🦞_
