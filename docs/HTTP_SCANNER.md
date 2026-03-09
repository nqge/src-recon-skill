# HTTP/HTTPS 服务扫描器使用指南

## 📖 功能说明

`http_scanner.py` 是一个强大的 HTTP/HTTPS 服务批量扫描工具，用于端口扫描后测试 Web 服务的访问情况。

### 核心功能

- **批量扫描** - 支持并发扫描多个 URL
- **状态码检测** - 记录每个 URL 的 HTTP 状态码
- **标题提取** - 自动提取网页标题
- **服务器识别** - 识别 HTTP 服务器类型
- **错误分类** - 区分超时、SSL 错误、连接错误等
- **详细报告** - 生成包含所有信息的扫描报告

---

## 🚀 使用方法

### 基本用法

```bash
# 扫描 URL 列表
python3 http_scanner.py urls.txt

# 指定输出文件
python3 http_scanner.py urls.txt report.txt
```

### URL 列表格式

创建一个文本文件，每行一个 URL：

```
http://example.com
https://example.com
https://api.example.com
https://admin.example.com
```

### 在自动化流程中使用

```bash
# 在 src-recon-auto.sh 中自动调用
./src-recon-auto.sh example.com
# 脚本会自动调用 http_scanner.py 扫描发现的 HTTP 服务
```

---

## 📊 输出示例

### 控制台输出

```
[*] 开始扫描 50 个 URL...
[*] 并发数: 50, 超时: 10s
[*] 进度: 10/50 (20%)
[*] 进度: 20/50 (40%)
...
[*] 进度: 50/50 (100%)

================================================================================
HTTP/HTTPS 服务扫描结果
================================================================================

📊 统计信息:
  总计: 50
  200: 35
  301: 8
  403: 4
  404: 2
  500: 1

✅ 200 OK (35 个):
  [200] https://www.example.com
      标题: Example Domain
      大小: 1256 bytes, 服务器: nginx
  [200] https://api.example.com
      标题: API Documentation
      大小: 3456 bytes, 服务器: Apache

⚠️  403 客户端错误 (4 个):
  [403] https://admin.example.com
  [403] https://config.example.com

🔥 500 服务器错误 (1 个):
  [500] https://api.test.example.com

================================================================================

[+] 报告已保存到: http_scan_report.txt
```

### 报告文件

生成的 `http_scan_report.txt` 包含：

```
# HTTP/HTTPS 服务扫描报告

**时间**: 2026-03-09 12:00:00
**总计**: 50 个 URL

[200] https://www.example.com
    标题: Example Domain
    大小: 1256 bytes
    服务器: nginx

[301] https://old.example.com
    标题: N/A
    大小: 0 bytes
    服务器: nginx

[403] https://admin.example.com
    标题: N/A
    大小: 0 bytes
    服务器: cloudflare
    错误: N/A
...
```

---

## ⚙️ 高级配置

### 调整并发数和超时

编辑 `http_scanner.py` 中的默认参数：

```python
scanner = HTTPScanner(timeout=10, max_workers=50)
```

或修改代码中的默认值：

```python
def __init__(self, timeout=10, max_workers=50):
    self.timeout = timeout      # 请求超时（秒）
    self.max_workers = max_workers  # 并发线程数
```

### 自定义请求头

修改 `check_url` 方法中的 headers：

```python
headers={
    'User-Agent': 'Mozilla/5.0...',
    'Authorization': 'Bearer your_token',  # 添加认证
    'Cookie': 'session=xxx'  # 添加 Cookie
}
```

---

## 🔧 故障排除

### SSL 证书错误

脚本默认忽略 SSL 证书验证。如果遇到问题：

```python
# 已设置 verify=False
response = requests.get(url, verify=False, ...)
```

### 超时问题

如果目标响应慢，增加超时时间：

```python
scanner = HTTPScanner(timeout=20, max_workers=30)
```

### 内存不足

如果 URL 列表很大，减少并发数：

```python
scanner = HTTPScanner(timeout=10, max_workers=20)
```

---

## 📈 性能优化建议

| 场景 | 并发数 | 超时 | 说明 |
|------|--------|------|------|
| 快速扫描 | 50-100 | 5s | 优先速度，可能漏掉慢响应 |
| 均衡模式 | 50 | 10s | 推荐设置 |
| 深度扫描 | 20-30 | 15s | 更准确，但耗时更长 |
| 稳定网络 | 100 | 10s | 网络好时可提高并发 |

---

## 🎯 与其他工具集成

### 配合 httpx

```bash
# 先用 httpx 快速发现
cat subs.txt | httpx -status-code -title -o http_services.txt

# 再用 http_scanner 详细扫描
awk '{print $1}' http_services.txt > urls.txt
python3 http_scanner.py urls.txt
```

### 配合 nuclei

```bash
# http_scanner 扫描完成后
nuclei -l urls.txt -t ~/nuclei-templates/vulnerabilities/
```

---

## 📝 输出文件说明

| 文件 | 说明 |
|------|------|
| **http_scan_report.txt** | 完整扫描报告 |
| **status_200.txt** | 200 OK 站点列表 |
| **status_3xx.txt** | 重定向站点列表 |
| **status_4xx.txt** | 客户端错误列表 |
| **status_5xx.txt** | 服务器错误列表 |

---

## 🔐 安全提醒

- **授权测试** - 只扫描有授权的目标
- **速率控制** - 避免对目标造成压力
- **数据保护** - 妥善保管扫描结果

---

_工具由小牛的 SRC 信息收集技能提供 🦞_
