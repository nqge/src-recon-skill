# FOFA API 配置指南

## 📝 获取 FOFA API Key

### 步骤 1：注册 FOFA 账户

1. 访问 FOFA 官网：https://fofa.info/
2. 点击右上角"注册"
3. 填写邮箱、密码完成注册
4. 验证邮箱

### 步骤 2：获取 API Key

1. 登录 FOFA：https://fofa.info/
2. 点击右上角头像 → "个人中心"
3. 在左侧菜单选择"API 管理"
4. 复制你的"FOFA Email"和"API Key"

### 步骤 3：配置环境变量

```bash
# 临时配置（当前会话有效）
export FOFA_EMAIL="your_email@example.com"
export FOFA_KEY="your_fofa_api_key"

# 永久配置（写入 ~/.bashrc）
echo 'export FOFA_EMAIL="your_email@example.com"' >> ~/.bashrc
echo 'export FOFA_KEY="your_fofa_api_key"' >> ~/.bashrc
source ~/.bashrc

# 验证配置
echo $FOFA_EMAIL
echo $FOFA_KEY
```

### 步骤 4：测试 API

```bash
# 测试 FOFA API 是否可用
curl -s "https://fofa.info/api/v1/search/all?email=${FOFA_EMAIL}&key=${FOFA_KEY}&qbase64=$(echo -n 'domain="baidu.com"' | base64)" | jq
```

## 🎯 FOFA 查询语法

### 基础语法

```bash
# 搜索子域名
domain="example.com"

# 搜索标题
title="后台管理"

# 搜索响应体
body="admin"

# 搜索 header
header="nginx"
```

### 组合查询

```bash
# AND 查询
domain="example.com" && title="admin"

# OR 查询
domain="example.com" || domain="example.net"

# NOT 查询
domain="example.com" && !title="test"
```

### 常用 SRC 语法

```bash
# 搜索目标所有资产
domain="example.com"

# 搜索特定端口
domain="example.com" && port="443"

# 搜索特定标题
domain="example.com" && title="管理后台"

# 搜索响应内容
domain="example.com" && body="password"

# 搜索服务器类型
domain="example.com" && server="Apache"
```

## ⚡ 使用技巧

### 1. 子域名收集

```bash
# Python 脚本方式（推荐）
python3 ~/.openclaw/workspace/skills/src-recon/fofa_subs.py example.com

# 或使用环境变量
export FOFA_EMAIL="your_email@example.com"
export FOFA_KEY="your_api_key"
python3 ~/.openclaw/workspace/skills/src-recon/fofa_subs.py example.com
```

### 2. API 限制

- **免费账户**：每天 100 次查询
- **会员账户**：根据会员等级不同
- **查询限制**：每次最多返回 10,000 条结果

### 3. 优化建议

- 使用精确查询语法减少无关结果
- 组合多个条件缩小范围
- 定期查询，积累资产数据

## 🔐 安全提醒

- **不要泄露 API Key** - API Key 与你的账户关联
- **不要分享配置文件** - 包含敏感信息的文件
- **定期更换 Key** - 如果怀疑泄露，立即更换
- **遵守使用条款** - 不要滥用 API

## 📊 API 响应格式

```json
{
  "error": false,
  "errmsg": "ok",
  "size": 100,
  "page": 1,
  "results": [
    ["http://www.example.com", "1", "nginx", "Example Site"],
    ["https://api.example.com", "2", "Apache", "API Server"]
  ]
}
```

字段说明：
- `results[0]`: 主机（host）
- `results[1]`: 端口（port）
- `results[2]`: 服务器（server）
- `results[3]`: 标题（title）

## 🆘 常见问题

### Q: API 返回错误？
A: 检查 Email 和 Key 是否正确，网络是否通畅

### Q: 没有结果？
A: 检查查询语法是否正确，尝试简化查询

### Q: 超出限制？
A: 等待配额重置或升级会员

### Q: 如何获取更多配额？
A: 访问 https://fofa.info/ 查看会员计划

---

_配置完成后，记得使用 `fofa_subs.py` 测试一下！🦞_
