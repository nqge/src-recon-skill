# Spring Boot Actuator 扫描器使用指南

## 📖 功能说明

`actuator_scanner.py` 是一个专门用于检测 Spring Boot Actuator 框架未授权访问和敏感端点的工具。

### 核心功能

- **Actuator 框架检测** - 自动识别 Spring Boot Actuator
- **端点提取** - 从 `/actuator` 提取所有可用端点
- **端点验证** - 验证端点的可访问性
- **漏洞识别** - 识别未授权访问、敏感信息泄露等漏洞
- **详细报告** - 生成包含漏洞列表的详细报告

---

## ⚠️ 为什么重要？

### Spring Boot Actuator 的风险

Spring Boot Actuator 是 Spring Boot 提供的生产级监控和管理端点，默认包含多个敏感端点：

| 端点 | 功能 | 风险 |
|------|------|------|
| `/actuator/health` | 健康检查 | 低 |
| `/actuator/env` | 环境变量 | **高** - 可能泄露密码、密钥 |
| `/actuator/configprops` | 配置属性 | **高** - 配置信息泄露 |
| `/actuator/heapdump` | 堆转储 | **严重** - 内存敏感信息 |
| `/actuator/threaddump` | 线程转储 | 中 - 线程信息泄露 |
| `/actuator/mappings` | 请求映射 | 中 - API 端点泄露 |
| `/actuator/shutdown` | 关闭应用 | **严重** - 可拒绝服务 |

---

## 🚀 使用方式

### 基本用法

```bash
# 分析站点列表
python3 actuator_scanner.py sites.txt

# 指定输出文件
python3 actuator_scanner.py sites.txt actuator_report.txt
```

### 站点列表格式

创建 `sites.txt`：

```
https://example.com
https://api.example.com
https://admin.example.com
```

### 在自动化流程中使用

```bash
# 在 src-recon-auto.sh 中自动调用
./src-recon-auto.sh example.com
```

脚本会自动对 200 状态的站点运行 Actuator Scanner。

---

## 📊 输出示例

### 控制台输出

```
[*] 正在扫描: https://example.com
    [*] 检测 Spring Boot Actuator 框架...
    [+] 检测到 Spring Boot Actuator
    [*] 从 /actuator 提取端点列表...
    [+] 提取到 18 个端点
    [*] 添加常见 Actuator 端点...
    [*] 总共检查 67 个端点...
        进度: 20/67
        进度: 40/67
        进度: 60/67
        进度: 67/67
    [+] 可访问端点: 8
    [!] 可访问敏感端点: 3
    [+] 需要认证: 2
    [+] 其他: 57
```

### actuator_report.txt

```
# Spring Boot Actuator 扫描报告

**时间**: 2026-03-09 16:00:00
**Actuator 检测**: 是

**统计信息**:
- 可访问端点: 8
- 需要认证: 2
- 其他状态: 57
- 发现漏洞: 3

## 🔴 漏洞列表

### 未授权访问 - 环境变量 [HIGH]

- **端点**: /actuator/env
- **URL**: https://example.com/actuator/env
- **描述**: 可以直接访问 /env 端点，可能泄露敏感配置信息

### 敏感信息泄露 [CRITICAL]

- **端点**: /actuator/env
- **URL**: https://example.com/actuator/env
- **描述**: /env 端点响应中包含密码或密钥

### 未授权访问 - 堆转储 [CRITICAL]

- **端点**: /actuator/heapdump
- **URL**: https://example.com/actuator/heapdump
- **描述**: 可以直接访问 /heapdump 端点，可能泄露内存敏感信息

## ✅ 可访问端点 (200 OK)

- [200] https://example.com/actuator
  端点: /actuator
  大小: 2345 bytes
  Content-Type: application/json

- [200] https://example.com/actuator/health
  端点: /actuator/health
  大小: 567 bytes
  Content-Type: application/json

- [200] https://example.com/actuator/env
  端点: /actuator/env
  大小: 45678 bytes
  Content-Type: application/json
  ⚠️  敏感数据: env

- [200] https://example.com/actuator/configprops
  端点: /actuator/configprops
  大小: 123456 bytes
  Content-Type: application/json
  ⚠️  敏感数据: configprops

## ⚠️  需要认证 (401/403)

- [403] https://example.com/actuator/shutdown
  端点: /actuator/shutdown

- [401] https://example.com/actuator/heapdump
  端点: /actuator/heapdump
```

---

## 🔍 检测原理

### 1. Actuator 框架检测

使用多种指纹识别 Spring Boot Actuator：

```python
# JSON 响应结构
{"_links": {...}}

# 特征字段
'health', 'status', 'groups'

# HTTP 头
X-Application-Context
```

### 2. 端点提取

#### 从 /actuator 提取

```python
# 访问 /actuator 端点
GET /actuator

# 响应示例
{
  "_links": {
    "self": {"href": "http://localhost:8080/actuator"},
    "health": {"href": "http://localhost:8080/actuator/health"},
    "env": {"href": "http://localhost:8080/actuator/env"}
  }
}

# 提取所有端点
['/actuator', '/actuator/health', '/actuator/env']
```

#### 常见端点字典

```python
# 新版（/actuator 前缀）
'/actuator/health'
'/actuator/env'
'/actuator/configprops'
'/actuator/heapdump'

# 旧版（无前缀）
'/health'
'/env'
'/configprops'
'/heapdump'
```

### 3. 漏洞识别

#### 未授权访问 /env

```python
if endpoint == '/actuator/env' and status == 200:
    # 检查响应内容
    if 'password' in content or 'secret' in content:
        return 'CRITICAL'
    else:
        return 'HIGH'
```

#### 敏感信息泄露

```python
# 检查敏感关键字
sensitive_keywords = ['password', 'secret', 'api_key', 'token', 'jdbc']

for keyword in sensitive_keywords:
    if keyword in content.lower():
        return 'CRITICAL'
```

---

## 💡 实战价值

### 1. 发现未授权的环境变量

```bash
# 运行扫描
python3 actuator_scanner.py target.txt

# 查看漏洞
cat actuator_report.txt | grep "环境变量"
```

访问 `/actuator/env` 可能泄露：
```json
{
  "activeProfiles": ["prod"],
  "propertySources": [{
    "name": "application.properties:prod",
    "properties": {
      "spring.datasource.password": "P@ssw0rd123",
      "spring.redis.host": "redis.internal",
      "api.secret.key": "sk_live_1234567890"
    }
  }]
}
```

### 2. 发现配置信息

访问 `/actuator/configprops` 可能泄露：
- 数据库连接信息
- API 密钥
- 内部服务地址
- 缓存配置

### 3. 发现堆转储

访问 `/actuator/heapdump` 可能泄露：
- 内存中的敏感数据
- 密码和密钥
- 用户信息
- 会话数据

---

## 🎯 典型工作流程

```
发现 200 状态站点
    ↓
[检测 Spring Boot Actuator]
    ↓
[提取可用端点]
    ↓
[添加常见端点]
    ↓
[并发验证可访问性]
    ↓
[识别漏洞类型]
    ↓
[生成详细报告]
```

---

## 🔧 与其他工具配合

### 配合 nuclei

```bash
# 对可访问端点进行漏洞扫描
cat actuator_report.txt | grep "200]" | awk '{print $2}' | nuclei -l -
```

### 配合 Burp Suite

```bash
# 将可访问端点导入 Burp
cat actuator_report.txt | grep "200]" | awk '{print $2}' > burp_input.txt
```

---

## 📝 实战案例

### 案例 1：未授权访问环境变量

```bash
python3 actuator_scanner.py target.txt
```

发现：
```
### 未授权访问 - 环境变量 [HIGH]
- **端点**: /actuator/env
- **URL**: https://example.com/actuator/env
```

访问该端点发现数据库密码、API 密钥等敏感信息。

### 案例 2：敏感信息泄露

```bash
cat actuator_report.txt | grep "敏感信息泄露"
```

发现：
```
### 敏感信息泄露 [CRITICAL]
- **端点**: /actuator/env
- **描述**: /env 端点响应中包含密码或密钥
```

---

## 🔐 安全提醒

- **授权测试** - 只检测有授权的目标
- **合法访问** - 发现的漏洞需要进一步验证
- **负责任披露** - 通过官方渠道报告漏洞
- **不要滥用** - 不要下载 heapdump 等大文件

---

## 🎯 漏洞等级说明

| 等级 | 说明 |
|------|------|
| **CRITICAL** | 可直接获取敏感信息（密码、密钥） |
| **HIGH** | 未授权访问配置或环境信息 |
| **MEDIUM** | 未授权访问一般信息 |
| **LOW** | 信息泄露风险较低 |

---

_工具由小牛的 SRC 信息收集技能提供 🦞_
