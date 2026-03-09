# ONEFORALL_SETUP.md - OneForAll 子域名收集工具

## 📖 工具介绍

**OneForAll** 是一款功能强大的子域名收集工具，集成了多种子域名收集方法。

### 核心功能

1. **常规收集**（无需 API Key）
   - DNS 解析
   - 字典爆破
   - 证书透明度查询
   - 威胁情报平台

2. **搜索引擎收集**（需要 API Key）
   - Shodan
   - Censys
   - FOFA
   - Quake（360 雷神）

---

## 🚀 安装 OneForAll

### 方法 1：使用 Git 克隆

```bash
# 克隆仓库
git clone https://github.com/shmilylty/OneForAll.git
cd OneForAll

# 安装依赖
pip3 install -r requirements.txt

# 验证安装
python3 oneforall.py --help
```

### 方法 2：下载发行版

```bash
# 下载最新版本
wget https://github.com/shmilylty/OneForAll/archive/refs/tags/v0.4.5.tar.gz

# 解压
tar -xzf v0.4.5.tar.gz
cd OneForAll-0.4.5

# 安装依赖
pip3 install -r requirements.txt
```

---

## 🔑 配置搜索引擎 API

### Shodan

```bash
# 获取 API Key
# 访问: https://developer.shodan.io/api

# 配置环境变量
export SHODAN_API_KEY="your_shodan_api_key"
```

### Censys

```bash
# 获取 API Key
# 访问: https://search.censys.io/account

# 配置环境变量
export CENSAT_API_KEY="your_censat_api_id:your_censat_api_secret"
```

### FOFA

```bash
# 获取 API Key
# 访问: https://fofa.info/user/users/info

# 配置环境变量
export FOFA_EMAIL="your_email@example.com"
export FOFA_KEY="your_fofa_api_key"
```

### Quake（360 雷神）

```bash
# 获取 API Key
# 访问: https://quake.360.cn/quake/#/index

# 配置环境变量
export QUAKE_API_KEY="your_quake_api_key"
```

---

## 🛠️ 使用 oneforall_subs.py

### 基本用法

```bash
# 常规收集（无需 API）
python3 oneforall_subs.py example.com

# 使用搜索引擎 API
python3 oneforall_subs.py example.com --api

# 指定输出文件
python3 oneforall_subs.py example.com my_subs.txt
```

### 完整示例

```bash
# 1. 配置搜索引擎 API（可选）
export SHODAN_API_KEY="xxx"
export FOFA_EMAIL="xxx"
export FOFA_KEY="xxx"

# 2. 运行收集
python3 oneforall_subs.py example.com --api

# 3. 查看结果
cat oneforall_subs.txt
```

---

## 📊 输出示例

```
[*] OneForAll 子域名收集
[*] 目标: example.com
[*] 使用 API: 是
[*] 输出文件: oneforall_subs.txt

[*] 使用搜索引擎 API 收集子域名
    目标: example.com
    [*] 可用的搜索引擎: shodan, fofa
    [*] 正在运行 OneForAll 搜索引擎模块...
    [+] 搜索引擎发现 234 个子域名

[*] 证书透明度查询
    目标: example.com
    [+] 证书透明度发现 567 个子域名

[+] 结果已保存到: oneforall_subs.txt
[+] 总共发现 801 个子域名

[*] 来源统计:
    - search_engines: 234 个
    - certificates: 567 个

================================================================================
OneForAll 子域名收集完成
================================================================================
总计: 801 个子域名
```

---

## 🔧 与其他工具集成

### 在 src-recon-auto.sh 中使用

```bash
# 阶段 1：子域名收集
echo -e "\n${YELLOW}[*] 阶段 1: 子域名收集${NC}"

# 检查是否配置了搜索引擎 API
if [ -n "$FOFA_KEY" ] || [ -n "$SHODAN_API_KEY" ]; then
    echo "[*] 使用 OneForAll（含搜索引擎 API）"
    python3 $SCRIPT_DIR/oneforall_subs.py $TARGET --api
else
    echo "[*] 使用 OneForAll（常规模式）"
    python3 $SCRIPT_DIR/oneforall_subs.py $TARGET
fi

# 合并结果
mv oneforall_subs.txt $OUTPUT_DIR/all_subs.txt
```

### 与 FOFA 结合

```bash
# 优先使用 FOFA（如果配置）
if [ -n "$FOFA_KEY" ]; then
    python3 fofa_subs.py $TARGET
    mv fofa_subs.txt $OUTPUT_DIR/fofa_subs.txt
fi

# 使用 OneForAll 收集更多子域名
python3 oneforall_subs.py $TARGET

# 合并去重
cat fofa_subs.txt oneforall_subs.txt 2>/dev/null | sort -u > all_subs.txt
```

---

## ⚙️ 配置文件

OneForAll 的配置文件位于：
```
OneForAll/setting.py
```

可以配置：
- 线程数
- 超时时间
- 启用/禁用模块
- API 密钥

---

## 🎯 使用场景

### 1. 快速子域名枚举

```bash
# 无需 API Key，快速收集
python3 oneforall_subs.py target.com
```

### 2. 深度子域名挖掘

```bash
# 使用所有可用的 API
export SHODAN_API_KEY="xxx"
export FOFA_EMAIL="xxx"
export FOFA_KEY="xxx"

python3 oneforall_subs.py target.com --api
```

### 3. 与其他工具配合

```bash
# 收集子域名
python3 oneforall_subs.py target.com

# 存活检测
cat oneforall_subs.txt | httpx -status-code -title -silent > alive.txt

# 端口扫描
nmap -iL alive.txt -p 80,443,8080 -oG port_scan.gnmap
```

---

## 📈 性能优化

### 1. 并发控制

在 `oneforall_subs.py` 中调整并发数：

```python
# 修改 OneForAll 配置
# OneForAll/setting.py
THREADS = 50  # 调整并发数
```

### 2. 超时设置

```python
# 设置更长的超时时间
timeout=1200  # 20 分钟
```

### 3. 模块选择

```bash
# 只运行特定模块
python3 oneforall_subs.py target.com --enable_modules certificate,dns
```

---

## 🔍 故障排查

### OneForAll 未安装

```bash
[-] OneForAll 未安装

# 解决方法
git clone https://github.com/shmilylty/OneForAll.git
cd OneForAll
pip3 install -r requirements.txt
```

### API 认证失败

```bash
[-] FOFA API 错误: Invalid API key

# 解决方法
# 检查 API Key 是否正确
echo $FOFA_KEY

# 重新配置
export FOFA_KEY="correct_api_key"
```

### 网络连接问题

```bash
[-] 连接超时

# 解决方法
# 1. 检查网络连接
ping -c 3 github.com

# 2. 使用代理
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
```

---

## 📚 参考资料

- **OneForAll GitHub**: https://github.com/shmilylty/OneForAll
- **OneForAll 文档**: https://shmilylty.github.io/OneForAll/
- **Shodan API**: https://developer.shodan.io/api
- **Censys API**: https://search.censys.io/api
- **FOFA API**: https://fofa.info/api/v1/search
- **Quake API**: https://quake.360.cn/quake/api

---

_工具体验：OneForAll 是最全面的子域名收集工具之一。🦞_
