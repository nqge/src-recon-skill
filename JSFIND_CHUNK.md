# JSFind Chunk 文件提取功能

## 📖 功能说明

JSFind 现在支持提取和验证 Webpack/Vite 等打包工具生成的 chunk 文件。

### 什么是 Chunk 文件？

现代前端应用使用 Webpack、Vite 等工具打包时，会将代码分割成多个 chunk 文件：

```javascript
// 主 JS 文件中的映射
{
  "chunk-abc123": "def456",
  "chunk-xyz789": "ghi012"
}
```

这些 chunk 文件通常包含：
- 路由组件
- 页面代码
- API 调用
- 配置信息

---

## 🎯 提取原理

### 1. 识别 Chunk 映射

从 JS 文件中提取 chunk 映射：

```python
# 正则模式
pattern = r'"(chunk-[a-f0-9]+)":"([a-f0-9]+)"'

# 示例 JS 内容
# {"chunk-abc123":"def456","chunk-xyz789":"ghi012"}

# 提取结果
[('chunk-abc123', 'def456'), ('chunk-xyz789', 'ghi012')]
```

### 2. 构造 Chunk URL

根据主 JS 文件的路径构造 chunk 文件 URL：

```
主 JS 文件: https://example.com/assets/index.abc123.js
Chunk 基础路径: https://example.com/assets/

Chunk 文件:
- https://example.com/assets/chunk-abc123.js
- https://example.com/assets/chunk-xyz789.js
```

### 3. 验证可访问性

并发验证所有 chunk 文件是否可访问：

```python
# 发送 HTTP 请求
response = requests.get(chunk_url, timeout=5)

# 记录状态码和大小
if response.status_code == 200:
    # 可访问，保存 URL
```

---

## 🚀 使用方式

### 自动化流程

```bash
# 在 src-recon-auto.sh 中自动调用
./src-recon-auto.sh example.com
```

脚本会自动：
1. 发现主 JS 文件
2. 提取 chunk 映射
3. 验证 chunk 文件
4. 保存结果

### 单独使用

```bash
# 创建站点列表
cat > sites.txt << EOF
https://example.com
EOF

# 运行分析
python3 jsfind.py sites.txt

# 查看结果
cat jsfind_results/accessible_chunks.txt
cat chunk_verification.txt
```

---

## 📊 输出示例

### 控制台输出

```
[*] 正在分析: https://example.com
    发现 3 个 JS 文件
    分析: https://example.com/assets/index.js
      API 端点: 45
      路径: 123
      敏感信息: 2
      Chunk 映射: 28

[*] 发现 chunk 映射，开始验证 chunk 文件...
[*] 发现 28 个 chunk 映射，开始验证...
    进度: 20/28
[+] Chunk 验证完成，结果已保存到: chunk_verification.txt
[+] 发现 23 个可访问的 chunk 文件
```

### accessible_chunks.txt

```
https://example.com/assets/chunk-abc123.js
https://example.com/assets/chunk-xyz789.js
https://example.com/assets/chunk-def456.js
...
```

### chunk_verification.txt

```
# Chunk 文件验证结果

**基础 URL**: https://example.com/assets/
**时间**: 2026-03-09 14:30:00

## ✅ 可访问的 Chunk 文件

- [200] https://example.com/assets/chunk-abc123.js
  Chunk: chunk-abc123, Hash: def456, Size: 12345 bytes
- [200] https://example.com/assets/chunk-xyz789.js
  Chunk: chunk-xyz789, Hash: ghi012, Size: 67890 bytes

## ⚠️ 不可访问的 Chunk 文件

- [404] https://example.com/assets/chunk-old123.js
- [403] https://example.com/assets/chunk-admin.js

## ❌ 错误

- [ERROR] https://example.com/assets/chunk-timeout.js: Connection timeout
```

---

## 💡 实战价值

### 1. 发现隐藏功能

Chunk 文件通常按路由分割，访问不同 chunk 可以发现：

```javascript
// chunk-admin.js - 管理功能
// chunk-dashboard.js - 仪表板
// chunk-settings.js - 设置页面
// chunk-internal.js - 内部工具
```

### 2. 代码审计

分析单个 chunk 文件比分析整个 bundle 更容易：

```bash
# 下载 chunk 文件
curl https://example.com/assets/chunk-admin.js > admin.js

# 使用 grep 搜索敏感信息
grep -i "password\|token\|api_key" admin.js
```

### 3. 发现 API 端点

Chunk 文件中可能包含未公开的 API 调用：

```javascript
// chunk-internal.js
fetch('/api/internal/debug')
axios.post('/api/v1/admin/export')
```

---

## 🔧 支持的 Chunk 格式

### Webpack

```javascript
// Webpack 4
{"chunk-abc123":"def456"}

// Webpack 5
{"1234":"5678"}
```

### Vite

```javascript
// Vite chunk 映射
{"chunk-ABCDEF":"123456"}
```

---

## 🎯 典型工作流程

```
发现主 JS 文件
    ↓
[提取 chunk 映射]
    ↓
[构造 chunk URL]
    ↓
[并发验证可访问性]
    ↓
[保存可访问的 chunk]
    ↓
[进一步分析 chunk 内容]
```

---

## 📝 实战案例

### 案例 1：发现管理界面

```bash
# 分析目标站点
python3 jsfind.py target.txt

# 发现可访问的 chunk
cat jsfind_results/accessible_chunks.txt
```

发现：
```
https://example.com/assets/chunk-admin.js
https://example.com/assets/chunk-dashboard.js
```

分析 chunk-admin.js：
```bash
curl https://example.com/assets/chunk-admin.js | grep -oE '"/api/[a-z/_]+"' | sort -u
```

发现 API：
```
/api/v1/admin/users
/api/v1/admin/config
/api/v1/internal/logs
```

### 案例 2：发现测试接口

```bash
# 查看所有可访问 chunk
cat jsfind_results/accessible_chunks.txt | while read url; do
    echo "分析: $url"
    curl -s $url | grep -oE 'fetch\(|axios\.' | head -5
done
```

---

## 🔐 安全提醒

- **授权测试** - 只分析有授权的目标
- **合法使用** - 发现的 chunk 文件用于漏洞挖掘
- **负责任披露** - 通过官方渠道报告发现的漏洞

---

_功能由小牛的 SRC 信息收集技能提供 🦞_
