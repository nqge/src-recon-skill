# AUTH_SESSION_MANAGER.md - 认证会话管理器

## 📖 工具介绍

**auth_session_manager.py** 是一个认证会话管理器，支持多种认证方式，用于需要登录才能访问的页面或 API 的信息收集。

### 支持的认证方式

1. **Cookie** - 浏览器 Cookie
2. **账号密码** - 用户名和密码
3. **Token** - 认证 Token
4. **API Key** - API 密钥
5. **Bearer Token** - OAuth Bearer Token

---

## 🚀 使用方法

### 方法 1：从文件加载

```bash
# 创建认证文件
cat > auth.json << EOF
{
  "cookie": "sessionid=xxx; csrftoken=yyy",
  "token": "your_token",
  "username": "user",
  "password": "pass"
}
EOF

# 使用认证文件
python3 auth_session_manager.py https://example.com auth.json
```

### 方法 2：从环境变量

```bash
# 设置环境变量
export TARGET_COOKIE="sessionid=xxx; csrftoken=yyy"
export TARGET_TOKEN="your_token"
export TARGET_USERNAME="user"
export TARGET_PASSWORD="pass"
export TARGET_API_KEY="your_api_key"
export TARGET_BEARER_TOKEN="your_bearer_token"

# 运行
python3 auth_session_manager.py https://example.com
```

### 方法 3：交互式输入

```bash
python3 auth_session_manager.py https://example.com

# 会提示选择认证方式并输入相应信息
```

---

## 📊 认证文件格式

### JSON 格式

```json
{
  "cookie": "sessionid=xxx; csrftoken=yyy",
  "token": "your_token",
  "username": "user",
  "password": "pass",
  "api_key": "your_api_key",
  "bearer_token": "your_bearer_token"
}
```

### Cookie 格式

```
sessionid=abc123; csrftoken=xyz789; user_id=123
```

---

## 🎯 使用场景

### 场景 1：需要登录的网站

```bash
# 1. 获取 Cookie
# 在浏览器中登录，然后复制 Cookie

# 2. 保存 Cookie
export TARGET_COOKIE="sessionid=xxx; csrftoken=yyy"

# 3. 测试认证
python3 auth_session_manager.py https://example.com/dashboard

# 4. 使用保存的会话进行扫描
python3 http_scanner.py urls.txt --session auth_session.json
```

### 场景 2：API 认证

```bash
# 1. 配置 API Key
export TARGET_API_KEY="your_api_key"

# 2. 测试认证
python3 auth_session_manager.py https://api.example.com/v1/users

# 3. 使用会话
python3 jsfind.py https://api.example.com --session auth_session.json
```

### 场景 3：Bearer Token

```bash
# 1. 配置 Bearer Token
export TARGET_BEARER_TOKEN="your_bearer_token"

# 2. 测试认证
python3 auth_session_manager.py https://example.com/api/protected
```

---

## 🔧 与其他工具集成

### 在自动化脚本中使用

```bash
# src-recon-auto.sh 中添加认证支持

# 检查是否需要认证
if [ -f "auth.json" ] || [ -n "$TARGET_COOKIE" ]; then
    echo "[*] 检测到认证信息"

    # 创建认证会话
    python3 auth_session_manager.py https://$TARGET auth.json

    # 使用会话进行扫描
    python3 http_scanner.py all_subs.txt http_services.txt --session auth_session.json
else
    echo "[*] 匿名扫描"
    python3 http_scanner.py all_subs.txt http_services.txt
fi
```

### 与 Python 工具配合

```python
import requests
from auth_session_manager import AuthSessionManager

# 创建会话管理器
manager = AuthSessionManager()

# 加载认证信息
auth_info = manager.load_from_file('auth.json')
manager.apply_auth(auth_info)

# 获取配置好的会话
session = manager.get_session()

# 使用会话发送请求
response = session.get('https://example.com/protected')
```

---

## 📝 输出示例

```
[*] 从环境变量加载认证信息
[+] 使用 Cookie 认证

[*] 测试访问: https://example.com/dashboard
[*] 响应状态码: 200
[+] 认证有效，可以访问

[+] 会话信息已保存到: auth_session.json

[+] 认证会话已保存，可以用于后续扫描
```

---

## 🎓 认证方式说明

### Cookie

**适用场景**：基于 Session 的 Web 应用

```bash
export TARGET_COOKIE="sessionid=xxx; csrftoken=yyy"
```

**获取方法**：
1. 在浏览器中登录
2. 打开开发者工具（F12）
3. 在 Network 面板中查看请求头
4. 复制 Cookie 值

### 账号密码

**适用场景**：需要登录的网站

```bash
export TARGET_USERNAME="user"
export TARGET_PASSWORD="pass"
```

**注意**：需要提供登录接口 URL

### Token

**适用场景**：基于 Token 的 API

```bash
export TARGET_TOKEN="your_token"
```

**请求头**：`Authorization: Token your_token`

### API Key

**适用场景**：RESTful API

```bash
export TARGET_API_KEY="your_api_key"
```

**请求头**：`X-API-Key: your_api_key`

### Bearer Token

**适用场景**：OAuth 2.0

```bash
export TARGET_BEARER_TOKEN="your_bearer_token"
```

**请求头**：`Authorization: Bearer your_bearer_token`

---

## 🔒 安全提醒

- **不要提交认证信息到 Git**
- **使用环境变量或本地文件**
- **定期更换密码和 Token**
- **限制 API Key 的权限**

### .gitignore

```
# 认证信息
auth.json
auth_session.json
*.cookie
```

---

## 💡 最佳实践

### 1. 使用环境变量

```bash
# 在 ~/.bashrc 中配置
export TARGET_API_KEY="xxx"

# 重新加载
source ~/.bashrc
```

### 2. 使用本地配置文件

```bash
# 创建 .env 文件
cat > .env << EOF
TARGET_COOKIE=xxx
TARGET_TOKEN=yyy
EOF

# 加载
source .env
```

### 3. 分离开发和生产配置

```bash
# 开发环境
cp auth.dev.json auth.json

# 生产环境
cp auth.prod.json auth.json
```

---

## 🐛 故障排查

### 认证失败

```
[-] 认证失败或权限不足
```

**解决方法**：
1. 检查 Cookie/Token 是否过期
2. 确认账号密码正确
3. 检查登录接口 URL
4. 查看浏览器中的实际请求

### 会话过期

```
[-] 认证失败: 401
```

**解决方法**：
1. 重新获取 Cookie/Token
2. 检查会话有效期
3. 使用刷新 Token

### 权限不足

```
[-] 认证失败: 403
```

**解决方法**：
1. 确认账号权限
2. 检查 API Key 权限范围
3. 联系管理员

---

_工具体验：认证管理是信息收集的重要环节。🦞_
