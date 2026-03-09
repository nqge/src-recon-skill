# API 参数测试工具使用指南

**工具**: `api_parameter_tester.py`
**功能**: 从 JS 中提取的 API 端点和参数进行构造测试，检测敏感信息泄露

---

## 🎯 **核心功能**

### **1. 自动化 API 测试**
- 从 JS 文件中提取的 API 端点
- 自动构造测试参数
- 发送 HTTP 请求并分析响应
- 检测敏感信息泄露

### **2. 多种测试类型**
- **通用测试参数**: 常见参数测试
- **未授权访问测试**: 测试是否需要认证
- **SQL 注入测试**: 检测 SQL 注入漏洞
- **XSS 测试**: 检测跨站脚本漏洞
- **路径遍历测试**: 检测路径遍历漏洞
- **SSRF 测试**: 检测服务器端请求伪造

### **3. 敏感信息检测**
- 手机号
- 身份证号
- 银行卡号
- 密码
- Token/JWT
- API Key
- 邮箱
- IP 地址
- 数据库连接字符串
- 内部路径

---

## 📋 **使用方法**

### **基本用法**

```bash
cd /root/.openclaw/workspace/skills/src-recon

# 测试单个目标
python3 core/api_parameter_tester.py https://example.com output/recon/example.com/jsfind_results

# 输出：
# api_parameter_test_report_20260309_181000.md
```

---

### **完整工作流程**

#### **步骤 1: 运行完整的信息收集**

```bash
cd /root/.openclaw/workspace/skills/src-recon

# 执行完整的 4 阶段自动化
./scripts/src-recon-auto-optimized.sh example.com

# 这会生成：
# output/recon/example.com/jsfind_results/
#   ├── api_endpoints.txt
#   ├── paths.txt
#   ├── secrets.txt
#   └── ...
```

---

#### **步骤 2: 运行 API 参数测试**

```bash
# 使用 jsfind_results 目录进行测试
python3 core/api_parameter_tester.py https://example.com output/recon/example.com/jsfind_results

# 实时输出：
# [+] 加载了 68 个 API 端点
# [+] 加载了 2 个敏感信息
# [*] 开始测试 272 个 API 端点...
# [🔴] /ecs-mobile-gateway/api/v1/internal/debug  | 未授权访问测试       | HIGH 
# [🟡] /ecs-mobile-gateway/api/v1/users/list     | 通用测试参数         | MEDIUM
# [🟢] /login/registerUser                        | SQL 注入测试         | LOW
# ...
```

---

#### **步骤 3: 查看测试报告**

```bash
# 查看生成的报告
cat api_parameter_test_report_20260309_181000.md

# 报告内容包括：
# 1. 统计摘要（总测试数、高风险、中风险、低风险、错误）
# 2. 高风险问题（敏感信息泄露详情）
# 3. 中风险问题
# 4. 错误
# 5. 修复建议
```

---

## 📊 **测试报告示例**

### **统计摘要**

```markdown
## 📊 统计摘要

- **总测试数**: 272
- **高风险**: 12 🔴
- **中风险**: 45 🟡
- **低风险**: 180 🟢
- **错误**: 35 ❌
```

---

### **高风险问题示例**

```markdown
## 🔴 高风险问题（敏感信息泄露）

### 1. /ecs-mobile-gateway/api/v1/internal/debug

**测试类型**: 未授权访问测试
**风险等级**: HIGH

**请求数据包**:
```http
GET https://example.com/ecs-mobile-gateway/api/v1/internal/debug HTTP/1.1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json, text/plain, */*
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8

Query Parameters:
  id=1
  userId=1
```

**响应状态**:
- 状态码: 200
- 响应大小: 15,234 bytes

**回显内容** (前 500 字符):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "users": [
      {
        "id": 1,
        "username": "admin",
        "phone": "138****8000",
        "email": "admin@example.com",
        "idCard": "320***********1234",
        "bankCard": "6222***********1234"
      },
      {
        "id": 2,
        "username": "user1",
        "phone": "139****0000",
        "email": "user1@example.com",
        "idCard": "321***********5678",
        "bankCard": "6225***********5678"
      }
    ],
    "total": 1250
  }
}
```

**敏感信息**:
- 手机号: 1250 个
  - 138****8000
  - 139****0000
  - 136****1234
- 身份证号: 1250 个
  - 320***********1234
  - 321***********5678
  - 322***********9012
- 银行卡号: 1250 个
  - 6222***********1234
  - 6225***********5678
  - 6228***********9012
- 邮箱: 1250 个
  - admin@example.com
  - user1@example.com
  - user2@example.com
```

---

### **修复建议**

```markdown
## 🚀 修复建议

### 高优先级

1. **立即修复敏感信息泄露**
   - 检查所有返回数据的 API 端点
   - 移除敏感信息（手机号、身份证、密码等）
   - 实施数据脱敏
     ```python
     # 示例：手机号脱敏
     def mask_phone(phone):
         return phone[:3] + '****' + phone[-4:]
     ```

2. **加强访问控制**
   - 为所有 API 端点配置身份验证
   - 实施基于角色的访问控制 (RBAC)
   - 限制未授权访问
     ```python
     # 示例：认证装饰器
     @require_auth
     def api_get_users():
         # 只有认证用户才能访问
         pass
     ```

3. **输入验证**
   - 验证所有输入参数
   - 防止 SQL 注入和 XSS 攻击
   - 使用参数化查询
     ```python
     # 示例：参数化查询
     cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
     ```

### 中优先级

1. **错误处理**
   - 统一错误响应格式
   - 避免在错误信息中泄露敏感信息
   - 记录详细的错误日志
     ```python
     # 示例：统一错误响应
     return jsonify({
         "code": -1,
         "message": "内部错误",
         "error": str(e)  # 只在开发环境返回
     }), 500
     ```

2. **响应大小限制**
   - 限制 API 响应大小
   - 实施分页
   - 过滤不必要的字段
     ```python
     # 示例：分页
     def api_get_users(page=1, size=10):
         start = (page - 1) * size
         end = start + size
         return users[start:end]
     ```
```

---

## 🛠️ **高级用法**

### **1. 自定义测试参数**

```python
# 编辑 api_parameter_tester.py
# 修改 test_payloads 字典

self.test_payloads = {
    '通用测试参数': {
        'id': '1',
        'userId': '1',
        # ... 添加更多参数
    },
    '自定义测试': {
        'custom_param': 'custom_value',
    }
}
```

---

### **2. 调整并发数**

```python
# 修改 max_workers 参数
tester = APIParameterTester(
    target_url='https://example.com',
    jsfind_dir='jsfind_results',
    max_workers=20  # 增加并发数（默认 10）
)
```

---

### **3. 只测试特定端点**

```python
# 加载端点
endpoints = tester.load_api_endpoints()

# 过滤端点
filtered_endpoints = [e for e in endpoints if 'api' in e.lower()]

# 只测试过滤后的端点
tester.run_tests(endpoints=filtered_endpoints)
```

---

### **4. 集成到自动化流程**

```bash
# 在 src-recon-auto-optimized.sh 中添加
#!/bin/bash

# ... 阶段 1-3 ...

# 阶段 4: 深度分析
# ...

# API 参数测试（新增）
echo "[*] 运行 API 参数测试..."
python3 core/api_parameter_tester.py $TARGET output/recon/$TARGET/jsfind_results

# 移动报告到输出目录
mv api_parameter_test_report_*.md output/recon/$TARGET/

echo "[+] API 参数测试完成"
```

---

## 🔍 **敏感信息检测模式**

### **默认检测模式**

| 信息类型 | 正则表达式 | 示例 |
|---------|-----------|------|
| 手机号 | `1[3-9]\d{9}` | 13800138000 |
| 身份证号 | `\d{17}[\dXx]` | 320102199001011234 |
| 银行卡号 | `\d{16,19}` | 6222021234567890123 |
| 密码 | `(?i)password["\s:]+["\s]*[^\s"\'<>]{6,}` | password: "123456" |
| Token | `(?i)(token\|jwt\|bearer)["\s:]+["\s]*[^\s"\'<>]{20,}` | token: "eyJhbGci..." |
| API Key | `(?i)(api[_-]?key\|access[_-]?token)["\s:]+["\s]*[^\s"\'<>]{20,}` | api_key: "sk_live_..." |
| 邮箱 | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | admin@example.com |
| IP 地址 | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` | 192.168.1.1 |
| 数据库连接 | `(?i)(mysql\|postgresql\|mongodb\|redis)://[^\s"\'<>]+` | mysql://user:pass@localhost/db |
| 内部路径 | `(?i)/(?:home\|var\|usr\|etc\|root)/[^\s"\'<>]+` | /var/www/html |

---

## 🎯 **风险等级说明**

### **HIGH (🔴 高风险)**
- 状态码: 200 OK
- 响应包含敏感信息
- 需要立即修复

### **MEDIUM (🟡 中风险)**
- 状态码: 200 OK
- 响应大小 > 1000 bytes
- 或状态码 >= 500（服务器错误）

### **LOW (🟢 低风险)**
- 状态码: 401, 403（需要认证）
- 或状态码: 200 OK 但响应较小

### **INFO (ℹ️ 信息)**
- 其他正常响应

### **ERROR (❌ 错误)**
- 请求失败
- 连接错误、超时等

---

## 🚀 **最佳实践**

### **1. 测试前准备**
- ✅ 确保有授权测试
- ✅ 备份重要数据
- ✅ 准备测试环境

### **2. 测试中**
- ✅ 从低风险测试开始
- ✅ 逐步增加测试强度
- ✅ 记录所有测试结果

### **3. 测试后**
- ✅ 分析测试报告
- ✅ 优先修复高风险问题
- ✅ 重新测试验证修复

---

## 🦞 **总结**

**API 参数测试工具**是一个非常强大的自动化测试工具！🦞

**核心价值**：
1. ✅ **自动化测试**: 自动构造参数，发送请求
2. ✅ **敏感信息检测**: 自动检测 10+ 种敏感信息
3. ✅ **风险评估**: 自动评估风险等级
4. ✅ **详细报告**: 生成包含请求数据包、响应状态、回显内容的详细报告
5. ✅ **修复建议**: 提供针对性的修复建议

**使用场景**：
- ✅ SRC 众测项目的 API 漏洞挖掘
- ✅ 渗透测试中的 API 安全评估
- ✅ 代码审计中的 API 安全检查
- ✅ 自动化安全测试流程

**这个工具可以帮助你快速发现 API 接口中的敏感信息泄露问题！🦞**
