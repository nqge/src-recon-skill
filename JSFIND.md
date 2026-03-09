# JSFind - JavaScript 文件 API 端点提取工具

## 📖 功能说明

`jsfind.py` 是一个强大的 JavaScript 文件分析工具，用于从网站的 JS 文件中提取隐藏的 API 接口、路径和敏感信息。

### 核心功能

- **JS 文件发现** - 自动发现网站中的 JavaScript 文件
- **API 端点提取** - 从 JS 代码中提取 REST API、GraphQL 端点
- **路径提取** - 提取代码中定义的所有路径
- **敏感信息识别** - 识别可能的 token、key、密码等
- **Chunk 文件提取** - 提取 Webpack/Vite 的 chunk 文件映射并验证
- **端点验证** - 验证发现的端点是否可访问
- **批量分析** - 支持批量分析多个站点

---

## 🎯 使用场景

### 1. API 接口发现

从前端 JS 代码中发现后端 API 接口：

```bash
python3 jsfind.py sites.txt
```

输出示例：
```
[*] 正在分析: https://example.com
    发现 3 个 JS 文件
    分析: https://example.com/app.js
      API 端点: 45
      路径: 123
      敏感信息: 2
```

### 2. 隐藏端点发现

发现未公开的管理接口、测试接口等：

```bash
cat jsfind_results/api_endpoints.txt
```

输出示例：
```
/api/v1/users
/api/v1/admin/config
/graphql
/internal/test
```

### 3. 敏感信息收集

识别 JS 中硬编码的凭证和密钥：

```bash
cat jsfind_results/secrets.txt
```

---

## 🚀 使用方法

### 基本用法

```bash
# 分析站点列表
python3 jsfind.py sites.txt

# 指定输出目录
python3 jsfind.py sites.txt my_results
```

### 站点列表格式

创建 `sites.txt`：

```
https://example.com
https://api.example.com
https://admin.example.com
```

### 输出文件

分析完成后，会在输出目录生成：

| 文件 | 说明 |
|------|------|
| **api_endpoints.txt** | 发现的 API 端点列表 |
| **paths.txt** | 发现的路径列表 |
| **secrets.txt** | 敏感信息 |
| **js_files.txt** | 分析的 JS 文件列表 |
| **accessible_chunks.txt** | 可访问的 chunk 文件列表 |
| **chunk_verification.txt** | 详细 chunk 验证结果 |
| **verified_endpoints.txt** | 验证可访问的端点 |

---

## 🔍 提取规则

### API 端点模式

工具使用以下正则表达式提取 API 端点：

```python
# REST API
r'["\']([/a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)["\']',
r'["\']/(?:api|v1|v2|v3)/[a-zA-Z0-9_-]+["\']',

# GraphQL
r'["\']/(?:graphql|graph)[a-zA-Z0-9_-]*["\']',
r'query\s+[a-zA-Z][a-zA-Z0-9_]*\s*\{',

# API 调用
r'\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
r'fetch\(["\']([^"\']+)["\']',
r'axios\.(?:get|post|put|delete)\(["\']([^"\']+)["\']',

# 路由定义
r'path:\s*["\']([^"\']+)["\']',
r'router\.[a-z]+\(["\']([^"\']+)["\']',
```

### 敏感信息模式

```python
r'["\']([A-Za-z0-9_]{20,})["\']',  # 可能的 token/key
r'["\'](?:Bearer|Token|API[_-]?KEY|SECRET)["\']:\s*["\']([^"\']+)["\']',
r'["\'][a-f0-9]{32,}["\']',  # 可能的 hash/key
```

---

## 📊 输出示例

### 控制台输出

```
[*] 开始分析 3 个站点...
[*] 正在分析: https://example.com
    发现 3 个 JS 文件
    分析: https://example.com/app.js
      API 端点: 45
      路径: 123
      敏感信息: 2
    分析: https://example.com/vendor.js
      API 端点: 12
      路径: 56
      敏感信息: 0
    分析: https://example.com/main.js
      API 端点: 8
      路径: 23
      敏感信息: 1

[*] 验证 65 个端点...
    进度: 10/65
    进度: 20/65
    ...
[+] 验证完成，结果已保存到: jsfind_results/verified_endpoints.txt
[+] 发现 23 个可访问端点

[+] 结果已保存到: jsfind_results/
    - api_endpoints.txt: 65 个 API 端点
    - paths.txt: 202 个路径
    - secrets.txt: 3 个敏感信息
    - js_files.txt: 3 个 JS 文件
```

### verified_endpoints.txt

```
# API 端点验证结果

**基础 URL**: https://example.com
**时间**: 2026-03-09 13:00:00

## ✅ 可访问端点 (200 OK)

- [200] https://example.com/api/v1/users
- [200] https://example.com/api/v1/config
- [200] https://example.com/graphql
- [200] https://example.com/internal/status

## ⚠️ 其他响应

- [401] https://example.com/api/v1/admin
- [403] https://example.com/api/v1/secrets

## ❌ 错误

- [ERROR] https://example.com/api/v1/old: Connection timeout
```

---

## ⚙️ 配置选项

### 调整并发数和超时

```python
finder = JSFinder(timeout=10, max_workers=30)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| timeout | 10 | 请求超时（秒） |
| max_workers | 30 | 并发线程数 |

### 自定义 JS 文件路径

编辑 `find_js_files` 方法中的 `common_paths`：

```python
common_paths = [
    '/app.js',
    '/main.js',
    '/custom/path/to/script.js',  # 添加自定义路径
]
```

---

## 🔧 与其他工具集成

### 在自动化流程中使用

```bash
# 在 src-recon-auto.sh 中自动调用
./src-recon-auto.sh example.com
# 脚本会自动对 200 状态站点运行 jsfind
```

### 配合目录扫描

```bash
# 1. JS 分析发现 API
python3 jsfind.py sites.txt

# 2. 对发现的 API 进行目录扫描
cat jsfind_results/api_endpoints.txt | while read endpoint; do
    gobuster dir -u https://example.com$endpoint -w dirs.txt
done
```

### 配合漏洞扫描

```bash
# 对验证可访问的端点进行漏洞扫描
cat jsfind_results/verified_endpoints.txt | grep "200" | awk '{print $2}' | nuclei -l -
```

---

## 🎯 典型使用流程

```
发现 200 状态站点
    ↓
[提取站点 URL]
    ↓
[jsfind 分析 JS 文件]
    ↓
[提取 API 端点]
    ↓
[验证端点可访问性]
    ↓
[保存可访问端点]
    ↓
[进一步漏洞扫描]
```

---

## 📝 实战案例

### 案例 1：发现隐藏的管理接口

```bash
# 分析目标站点
python3 jsfind.py target_site.txt

# 查看发现的 API
cat jsfind_results/api_endpoints.txt
```

发现：
```
/api/v1/users
/api/v1/admin/config  ← 隐藏的管理接口
/api/v1/internal/debug  ← 内部调试接口
```

### 案例 2：发现 GraphQL 端点

```bash
# 查看所有发现的端点
cat jsfind_results/api_endpoints.txt | grep graphql
```

发现：
```
/graphql
/graph/admin
```

验证 GraphQL 端点：
```bash
curl -X POST https://example.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'
```

### 案例 3：发现敏感信息

```bash
# 查看发现的敏感信息
cat jsfind_results/secrets.txt
```

发现：
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
API_KEY=sk_live_1234567890abcdef
```

---

## 🔐 安全提醒

- **授权测试** - 只分析有授权的目标
- **敏感信息** - 发现的敏感信息妥善保管
- **负责任披露** - 通过官方渠道报告漏洞

---

## 🆘 故障排除

### 问题：未发现 JS 文件

**解决方案**：
1. 检查站点是否是 SPA（单页应用）
2. 手动添加常见 JS 路径到 `common_paths`
3. 使用浏览器开发者工具查看加载的 JS 文件

### 问题：提取的端点太少

**解决方案**：
1. 增加正则表达式模式
2. 检查 JS 文件是否混淆或压缩
3. 尝试美化混淆的 JS 代码

### 问题：验证失败

**解决方案**：
1. 增加超时时间
2. 减少并发数
3. 检查是否需要特定的请求头

---

_工具由小牛的 SRC 信息收集技能提供 🦞_
