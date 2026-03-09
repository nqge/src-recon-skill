# SRC 信息收集技能 - 最终输出文件说明与智能分析示例

**目标**: 详细说明 SRC 信息收集技能的最终输出文件结构，并提供智能分析示例

---

## 📁 **完整流程输出文件结构**

### **目录结构**

```
output/recon/<target>/
├── 阶段 0: 准备文件（用户创建）
│   ├── auth.json                    # 认证信息（Cookie/密码/Token）
│   ├── wordlists/                   # 字典文件
│   └── targets.txt                 # 目标列表

├── 阶段 1: 子域名收集
│   ├── stage1/
│   │   ├── all_subs.txt            # 所有子域名（未去重）
│   │   ├── all_subs_unique.txt     # 唯一子域名
│   │   ├── all_urls.txt            # 所有 URL
│   │   ├── all_urls_unique.txt     # 唯一 URL
│   │   ├── all_ips.txt             # 所有 IP
│   │   └── all_ips_unique.txt      # 唯一 IP
│   ├── fofa_subs.txt              # FOFA 收集的子域名
│   ├── oneforall_subs.txt        # OneForAll 收集的子域名
│   └── subs.txt                   # 被动 DNS 收集的子域名

├── 阶段 2: 服务探测
│   ├── stage2/
│   │   ├── http_services.txt        # HTTP 服务扫描结果
│   │   ├── http_accessible_urls.txt # 可访问的 URL
│   ├── stage2/
│   │   ├── domain_ip_mapping.json  # 域名到 IP 映射
│   │   ├── resolved_ips.txt        # 解析的 IP
│   │   ├── all_ips_unique.txt       # 唯一 IP
│   │   ├── ipv4_only.txt           # 仅 IPv4 的 IP
│   │   ├── error_urls.txt         # 错误的 URL
│   │   ├── http_access_improvement.txt # 连接改进报告
│   │   └── http_accessible_urls.txt # 可访问的 URL（优化后）

├── 阶段 3: 端口扫描
│   ├── stage3/
│   │   ├── port_scan.gnmap         # 端口扫描结果
│   │   ├── standard_ports.gnmap    # 标准端口扫描
│   │   ├── web_ips.txt             # Web 服务 IP
│   │   ├── all_accessible_urls.txt # 所有可访问的 URL

├── 阶段 4: 深度分析
│   ├── jsfind_results/           # JS 分析结果
│   │   ├── api_endpoints.txt     # API 端点
│   │   ├── paths.txt             # 发现的路径
│   │   ├── secrets.txt           # 敏感信息
│   │   ├── js_files.txt          # JS 文件列表
│   │   └── accessible_chunks.txt # 可访问的 chunk 文件
│   ├── stage4/
│   │   ├── js_urls.txt          # 待分析的 URL
│   │   ├── vuecrack_combined.txt # Vue.js 检测结果
│   │   ├── actuator_combined.txt # Actuator 检测结果
│   │   ├── path_bruteforce_combined.txt # 路径爆破结果
│   ├── all_scan_results.json    # 整合的扫描结果
│   └── vulnerability_analysis.txt # 智能漏洞分析

├── 错误分析报告
├── ERROR_ANALYSIS.md            # 错误详情分析
├── ERROR_IMPROVEMENT.md         # 错误改进结果
└── FINAL_OPTIMIZATION.md        # 最终优化报告

├── 最终报告
├── REPORT.md                   # 最终报告（汇总所有阶段）
├── STAGES.md                   # 各阶段状态
└── report_20260309_HHMMSS.md   # 带时间戳的报告
```

---

## 📊 **各阶段输出文件详解**

### **阶段 1: 子域名收集** 🔍

#### **核心文件**

##### **all_subs_unique.txt** - 唯一子域名列表
```
jxgj.jshbank.com
captcha.jshbank.com
cash.jshbank.com
cloud.jshbank.com
coas-api.jshbank.com
ebank.jshbank.com
ecbank.jshbank.com
esc.jshbank.com
...
```

**用途**: 
- 子域名爆破的字典文件
- 端口扫描的目标列表
- 资产导出的基础数据

---

##### **all_urls_unique.txt** - 唯一 URL 列表
```
http://jxgj.jshbank.com
https://jxgj.jshbank.com
http://captcha.jshbank.com
https://captcha.jshbank.com
http://cash.jshbank.com
...
```

**用途**:
- HTTP 服务扫描
- 存活检测
- 指纹识别

---

### **阶段 2: 服务探测** 🌐

#### **http_services.txt** - HTTP 服务扫描结果
```
[200] https://jxgj.jshbank.com 智薪管家
[403] http://coas-api.jshbank.com
[403] https://ebank.jshbank.com
[403] https://pbank.jshbank.com
[403] https://vision.jshbank.com
...
```

**用途**: 
- 识别可访问的服务
- 状态码统计
- 标题收集

---

#### **http_accessible_urls.txt** - 可访问的 URL（优化后）
```
https://jxgj.jshbank.com
https://shop.jshbank.com
https://vpn.jshbank.com
https://coas-api.jshbank.com
https://ebank.jshbank.com
https://cloud.jshbank.com
https://captcha.jshbank.com
https://fuyao-costcontrol-api.jshbank.com
```

**用途**:
- 深度分析的目标列表
- 漏洞验证的目标
- 渗透测试的目标

---

#### **domain_ip_mapping.json** - 域名到 IP 映射
```json
{
  "jxgj.jshbank.com": ["111.53.210.79", "111.53.211.158"],
  "captcha.jshbank.com": ["111.53.211.140"],
  "cloud.jshbank.com": ["111.53.211.158"]
}
```

**用途**:
- 资产关联分析
- IP 段识别
- 同服务器站点发现

---

#### **resolved_ips.txt** - 解析的 IP 列表
```
111.53.210.79
111.53.211.158
111.53.211.140
...
```

**用途**:
- 端口扫描的目标列表
- IP 段扫描
- 资产归类

---

### **阶段 3: 端口扫描** 🔌

#### **port_scan.gnmap** - 端口扫描结果（gnmap 格式）
```
# Nmap 7.80 scan initiated Sat Mar  8 22:45:12 2024 as root
Stats: 8 targets scanned in 22.34 seconds
Host: 111.53.211.158 (scanme_targets_1)
Ports: 9452 filtered, 205 open, 34 closed
...

Host: 111.53.211.158
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
8443/tcp open  https-alt
3000/tcp open  pando
5000/tcp open  upnp (Java RMI)
8888/tcp open  http-alt
9000/tcp open  http-alt
```

**用途**:
- 识别开放端口
- 服务识别
- 版本探测
- 安全配置检查

---

### **阶段 4: 深度分析** 🎯

#### **jsfind_results/api_endpoints.txt** - API 端点发现
```
/login/registerUser
/login/modifyPwd
/login/accountCancellation
/ecs-mobile-gateway
/mp-gateway
/fuyao-costcontrol-api
/addressBook/queryEtpCustInfo
...
```

**用途**:
- API 测试目标
- 未授权访问测试
- 参数污染测试

---

#### **jsfind_results/paths.txt** - 路径提取
```
/login
/personCenter/index
/enterprise/index
/admin
/api
/config
/management
/console
...
```

**用途**:
- 路径爆破字典
- 目录扫描
- 隐藏端点发现

---

#### **jsfind_results/secrets.txt** - 敏感信息发现
```
password: admin123
api_key: sk_live_xxxxxxxxx
token: eyJhbGciOiJIUzI1NiIsIn0.eyJ1...
...
```

**用途**:
- 凭认证测试
- 密钥复用
- 会话劫持测试

---

#### **vulnerability_analysis.txt** - 智能漏洞分析
```
### 🔴 高风险问题 (3 个)

#### 1. 未授权的 API 端点: /api/internal/users
- **风险**: 数据泄露
- **影响**: 所有用户数据
- **POC**: curl -k https://example.com/api/internal/users
- **优先级**: P0（立即修复）

#### 2. SQL 注入: /search?query=1' OR '1'='1
- **风险**: 数据库泄露
- **影响**: 所有数据库数据
- **POC**: curl -k "https://example.com/search?query=1' OR '1'='1"
- **优先级**: P0（立即修复）

#### 3. 管理后台弱密码: /admin
- **用户**: admin / admin123
- **风险**: 完全控制
- **POC**: curl -u admin:admin123 https://example.com/admin
- **优先级**: P1（24小时内修复）
```

**用途**:
- 优先级排序
- 风险评估
- 修复建议

---

## 🎯 **智能分析示例**

### **示例目标**: jshbank.com

#### **输入**
```
目标: jshbank.com
```

---

#### **阶段 1: 子域名收集结果**

```
发现: 36 个子域名
主要子域名:
- jxgj.jshbank.com (智薪管家)
- captcha.jshbank.com (验证码)
- cash.jshbank.com (现金管理)
- ebank.jshbank.com (网银)
- pbank.jshbank.com (手机银行)
...
```

**分析**:
- ✅ 发现 36 个子域名
- ✅ 识别核心业务系统（网银、手机银行、现金管理）
- ✅ 发现微信小程序应用

---

#### **阶段 2: 服务探测结果**

```
HTTP 服务: 6 个可访问 URL
- https://jxgj.jshbank.com
- https://shop.jshbank.com
- https://vpn.jshbank.com
- https://coas-api.jshbank.com
- https://ebank.jshbank.com
- https://cloud.jshankbank.com

错误分析:
- 连接错误: 44 个
- SSL 错误: 18 个
- 超时: 4 个

优化后: 10 个可访问 URL (+66.7%)
```

**分析**:
- ⚠️ 大量 SSL 错误（Legacy SSL Renegotiation）
- ⚠️ 部分服务需要特殊处理
- ✅ 优化后可访问 URL 从 6 个增加到 10 个

---

#### **阶段 3: 端口扫描结果**

```
高价值主机（全端口开放）:
1. 123.103.115.72: 9 个端口
   - 80/tcp (HTTP)
   - 443/tcp (HTTPS)
   - 3000/tcp (Node.js - 开发端口)
   - 5000/tcp (Flask/Django - 开发端口)
   - 8888/tcp (HTTP Alt - 开发端口)
   - 9000/tcp (HTTP Alt - 开发端口)
   - 9443/tcp (HTTPS Alt - 开发端口)

2. 42.81.147.92: 9 个端口
   - 80/tcp (HTTP)
   - 443/tcp (HTTPS)
   - 3000/tcp (Node.js)
   - 5000/tcp (Flask/Django)
   - 8080/tcp (HTTP Alt)
   - 8443/tcp (HTTPS Alt)
   - 8888/tcp (HTTP Alt)
```

**分析**:
- 🔥 发现 2 个全端口开放的主机
- 🔥 9 个开发端口暴露（3000, 5000, 8888）
- ⚠️ 可能存在开发接口泄露
- ⚠️ 可能存在未授权的管理后台

---

#### **阶段 4: 深度分析结果**

**API 端点发现** (48 个):
```
登录认证 (18 个):
- /login/registerUser
- /login/modifyPwd
  - /login/logout
- ...

企业服务 (8 个):
- /coretp/teamCreate
- /enterprise/index
- /etp/qryEtpAcctInfo
  ...

网关服务 (4 个):
- /ecs-mobile-gateway
- /mp-gateway
- /fuyao-costcontrol-api
```

**路径提取** (73 个):
```
/admin
/api
/api/v1
/config
/management
/console
...
```

**敏感信息** (2 个):
```
password: admin123
api_key: sk_live_xxxxxxxxx
```

---

#### **智能漏洞分析**

```
### 🔴 高风险问题 (3 个)

#### 1. 未授权的 API 端点: /ecs-mobile-gateway/api/v1/internal
- **风险**: 数据泄露
- **影响**: 所有用户数据
- **建议**: 立即配置访问控制

#### 2. 管理后台弱密码: /admin
- **用户**: admin / admin123
- **风险**: 完全控制
- **建议**: 立即修改密码

#### 3. 开发端口暴露: 42.81.147.92:8888
- **风险**: 开发接口泄露
- **影响: 代码注入、数据泄露
- **建议: 禁止公网访问
```

---

## 📋 **最终报告文件**

### **REPORT.md** - 最终汇总报告

```
# jshbank.com SRC 信息收集报告

**目标**: jshbank.com
**时间**: 2026-03-09 14:53:27

## 📊 统计摘要
- 子域名: 36 个
- 可访问 URL: 10 个
- 开放端口: 50+ 个
- 高风险问题: 3 个

## 🎯 关键发现
1. 全端口开放的主机: 2 个
2. 微信小程序应用: jxgj.jshbank.com
3. 开发端口暴露: 9 个
4. 管理后台弱密码

## 🚀 下一步建议
1. 立即修改管理密码
2. 禁止公网访问开发端口
3. 配置 API 访问控制
...
```

---

## 🎯 **智能分析示例代码**

### **Python 智能分析脚本**

```python
#!/usr/bin/env python3
"""
SRC 信息收集智能分析脚本
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime

class SRCAnalyzer:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.results = {}
    
    def analyze(self):
        """执行智能分析"""
        
        # 1. 读取所有阶段的结果文件
        self._load_stage1_results()
        self._load_stage2_results()
        self._load_stage3_results()
        self._load_stage4_results()
        
        # 2. 进行智能分析
        self._analyze_subdomains()
        self._analyze_services()
        self._analyze_ports()
        self._analyze_deep_analysis()
        
        # 3. 生成最终报告
        self._generate_final_report()
        
        return self.results
    
    def _load_stage1_results(self):
        """加载阶段 1 结果"""
        stage1_dir = self.output_dir / "stage1"
        
        if (stage1_dir / "all_subs_unique.txt").exists():
            with open(stage1 / "all_subs_unique.txt) as f:
                self.results['subdomains'] = [line.strip() for line in f if line.strip()]
        else:
            self.results['subdomains'] = []
        
        if (stage1_dir / "all_ips_unique.txt").exists():
            with open(stage1_dir / "all_ips_unique.txt") as f:
                self.results['ips'] = [line.strip() for line in f if line.strip()]
        else:
            self.results['ips'] = []
    
    def _load_stage2_results(self):
        """加载阶段 2 结果"""
        stage2_dir = self<arg_value>.output_dir / "stage2"
        
        if (stage2_dir / "http_accessible_urls.txt").exists():
            with open(stage2_dir / "http_accessible_urls.txt") as f:
                self.results['accessible_urls'] = [line.strip() for line in f if line.strip()]
        else:
            self.results['accessible_urls'] = []
        
        if (stage2_dir / "error_urls.txt").exists():
            with open(stage2_dir / "error_urls.txt") as f:
                self.results['error_urls'] = [line.strip() for line in f if line.strip()]
        else:
            self.results['error_urls'] = []
    
    def _load_stage3_results(self):
        """加载阶段 3 结果"""
        stage3_dir = self.output_dir / "stage3"
        
        if (stage3_dir / "port_scan.gnmap").exists():
            self.results['port_scan'] = str(stage3_dir / "port_scan.gnmap")
        
        if (stage3_dir / "web_ips.txt").exists():
            with open(stage3_dir / "web_ips.txt") as f:
                self.results['web_ips'] = [line.strip() for line in f if line.strip()]
        else:
            self.results['web_ips'] = []
    
    def _load_stage4_results(self):
        """加载阶段 4 结果"""
        stage4_dir = self.output_dir / "stage4"
        
        # JS 分析结果
        jsfind_dir = self.output_dir / "jsfind_results"
        if jsfind_dir.exists():
            if (jsfind_dir / "api_endpoints.txt").exists():
                with open(jsfind_dir / "api_endpoints.txt") as f:
                    self.results['api_endpoints'] = [line.strip() for line in f if line.strip()]
            if (jsfind_dir / "paths.txt").exists():
                with open(jsfind_dir / "paths.txt") as f:
                    self.results['paths'] = [line.strip() for line in f if line.strip()]
            if (jsfind_dir / "secrets.txt").exists():
                with open(jsfind_dir / "secrets.txt") as f:
                    self.results['secrets'] = []
                    for line in f:
                        content = line.strip()
                        if content:
                            self.results['secrets'].append(content)
        
        # 漏洞分析结果
        vuln_file = self.output_dir / "vulnerability_analysis.txt"
        if vuln_file.exists():
            self.results['vulnerabilities'] = vuln_file
        
        # 路径爆破结果
        path_file = self.output_dir / "path_bruteforce_combined.txt"
        if path_file.exists():
            self.results['path_bruteforce'] = path_file
    
    def _analyze_subdomains(self):
        """分析子域名"""
        print(f"\n[+] 子域名分析:")
        print(f"    总数: {len(self.results['subdomains'])}")
        print(f"    示例: {self.results['subdomains'][:5]}")
        
        # 按域名类型分类
        business_domains = []
        wechat_domains = []
        other_domains = []
        
        for sub in self.results['subdomains']:
            if 'jshbank' in sub:
                business_domains.append(sub)
            elif 'wx' in sub:
                wechat_domains.append(sub)
            else:
                other_domains.append(sub)
        
        print(f"    业务域名: {len(business_domains)} 个")
        print(f"    微信小程序: {len(wechat_domains)} 个")
        print(f"    其他域名: {len(other_domains)} 个")
    
    def _analyze_services(self):
        """分析服务"""
        print(f"\n[+] 服务分析:")
        print(f"    可访问: {len(self.results['accessible_urls'])} 个")
        print(f"    错误: {len(self.results['error_urls'])} 个")
        print(f"    服务器类型: TongWeb/WebLogic/其他")
        
        # 检查错误类型
        error_types = {}
        for error_url in self.results['error_urls']:
            try:
                response = requests.get(error_url, timeout=5, verify=False)
                if 'SSL' in str(response.content):
                    error_types['SSL'] = error_types.get('SSL', 0) + 1
                elif 'Connection' in str(response.content):
                    error_types['Connection'] = error_types.get('Connection', 0) + 1
                elif 'timeout' in str(response.content).lower():
                    error_types['Timeout'] = error_types.get('Timeout', 0) + 1
            except:
                pass
        
        print(f"    错误分类:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"        {error_type}: {count} 个")
    
    def _analyze_ports(self):
        """分析端口"""
        print(f"\n[+] 端口分析:")
        
        if 'web_ips' in self.results:
            print(f"    Web 服务 IP: {len(self.results['web_ips'])} 个")
            
            # 分析端口分布
            port_counts = {}
            for ip in self.results['web_ips'][:5]:
                # 使用 nmap 解析端口信息
                try:
                    import subprocess
                    result = subprocess.run(
                        ['nmap', '-p-', '-T4', '-oX', ip],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    ports = re.findall(r'(\d+)/open', result.stdout)
                    for port in ports:
                        port_counts[port] = port_counts.get(port, 0) + 1
                except:
                    pass
            
            print(f"    端口分布:")
            for port, count in sorted(port_counts.items(), key=lambda x: x[1]):
                print(f"        {port}: {count} 次")
    
    def _analyze_deep_analysis(self):
        """深度分析"""
        print(f"\n[+] 深度分析:")
        
        # API 端点分析
        if 'api_endpoints' in self.results:
            print(f"    API 端点: {len(self.results['api_endpoints'])} 个")
            
            # 按功能分类
            api_categories = self._categorize_apis(self.results['api_endpoints'])
            
            print(f"    按功能分类:")
            for category, apis in sorted(api_categories.items(), key=lambda x: len(x), reverse=True):
                if len(apis) >= 3:
                    print(f"      {category}: {len(apis):2d} 个")
                    for api in apis[:3]:
                        print(f"        - {api}")
                    if len(apis) > 3:
                        print(f"        ... 还有 {len(apis) - 3} 个")
        
        # 路径分析
        if 'paths' in self.results:
            print(f"    发现路径: {len(self.results['paths'])} 个")
            
            # 高风险路径
            high_risk_paths = [p for p in self.results['paths'] if 'admin' in p.lower() or 'config' in p.lower() or 'debug' in p.lower()]
            print(f"    高风险路径: {len(high_risk_paths)} 个")
            for path in high_risk_paths[:5]:
                print(f"        - {path}")
        
        # 敏感信息分析
        if 'secrets' in self.results and self.results['secrets']:
            print(f"    敏感信息: {len(self.results['secrets')} 条")
    
    def _categorize_apis(self, apis):
        """按功能分类 API 端点"""
        categories = {
            '登录认证': [],
            '企业服务': [],
            '网关服务': [],
            '通讯录管理': [],
            '系统功能': [],
            '其他': []
        }
        
        for api in apis:
            if 'login' in api.lower() or 'register' in api.lower() or 'pwd' in api.lower():
                categories['登录认证'].append(api)
            elif 'etp' in api.lower() or 'enterprise' in api.lower() or 'team' in api.lower():
                categories['企业服务'].append(api)
            elif 'gateway' in api.lower() or 'api' in api.lower():
                categories['网关服务'].append(api)
            elif 'address' in api.lower() or 'contact' in api.lower():
                categories['通讯录管理'].append(api)
            elif 'common' in api.lower() or 'help' in api.lower() or 'city' in api.lower():
                categories['系统功能'].append(api)
            else:
                categories['其他'].append(api)
        
        return categories
    
    def _generate_final_report(self):
        """生成最终报告"""
        report_path = self.output_dir / "ANALYSIS_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 智能分析报告\n\n")
            f.write(f"**目标**: {self.output_dir.name}\n")
            f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n---\n")
            
            # 统计摘要
            f.write("## 📊 统计摘要\n\n")
            f.write(f"- 子域名: {len(self.results.get('subdomains', []))} 个\n")
            f.write(f"- 可访问 URL: {len(self.results.get('accessible_urls', []))} 个\n")
            f.write(f"- 错误 URL: {len(self.results.get('error_urls', []))} 个\n")
            f.write(f"- Web 服务 IP: {len(self.results.get('web_ips', []))} 个\n")
            
            # 关键发现
            f.write("\n## 🎯 关键发现\n\n")
            
            # 高价值目标
            if 'web_ips' in self.results and len(self.results['web_ips']) > 0:
                f.write("### 🔥 高价值主机\n\n")
                f.write("发现全端口开放或多个 Web 服务的主机:\n\n")
                for ip in self.results['web_ips'][:3]:
                    f.write(f"- {ip}\n")
            
            # 高风险问题
            f.write("\n### 🔴 高风险问题\n\n")
            f.write("按优先级排序:\n\n")
            
            # API 端点
            if 'api_endpoints' in self.results:
                api_categories = self._categorize_apis(self.results['api_endpoints'])
                
                f.write("登录认证:\n")
                if '登录认证' in api_categories and len(api_categories['登录认证']) > 0:
                    for api in api_categories['登录认证'][:5]:
                        f.write(f"- {api}\n")
                
                f.write("\n企业服务:\n")
                if '企业服务' in api_categories and len(api_categories['企业服务']) > 0:
                    for api in api_categories['企业服务'][:5]:
                        f.write(f"- {api}\n")
            
            # 路径
            if 'paths' in self.results:
                high_risk_paths = [p for p in self.results['paths'] if 'admin' in p.lower() or 'config' in p.lower()]
                if len(high_risk_paths) > 0:
                    f.write("\n### 🚨 高风险路径\n\n")
                    for path in high_r_paths[:10]:
                        f.write(f"- {path}\n")
            
            # 敏感信息
            if 'secrets' in self.results and self.results['secrets']:
                f.write("\n### 🔑 敏感信息\n\n")
                for secret in self.results['ysrc-recon/skills/src-recon/output/recon/jshbank.com/path_bruteforce_combined.txt" 2>&1 | head -20
                for secret in secrets:
                    f.write(f"- {secret[:50]}...\n")
            
            # 下一步建议
            f.write("\n## 🚀 下一步建议\n\n")
            
            # 优先级 1: 高风险问题修复
            f.write("### 优先级 1: 高风险问题修复 🔥🔥🔥\n")
            f.write("1. 修改管理密码\n")
            f.write("2. 配置 API 访问控制\n")
            f.write("3. 禁止公网访问开发端口\n")
            
            # 优先级 2: 中风险问题修复
            f.write("\n### 优先级 2: 中风险问题修复 ⚠️\n")
            f.write("1. 配置强身份验证\n")
            f.write("2. 启用 Web 应用防火墙 (WAF)\n")
            f.write("3. 定期安全审计\n")
            
            # 优先级 3: 低风险问题修复
            f.write("\n### 优先级 3: 低风险问题修复 🟢\n")
            f.write("1. 更新安全策略\n")
            f.write("2. 安全加固\n")
            f.write("3. 安全培训")
            
            # 工具建议
            f.write("\n## 🛠️ 工具建议\n\n")
            f.write("- 使用 Burp Suite 进行渗透测试\n")
            f.write("- 使用 SQLMap 进行数据库扫描\n")
            f.write("- 使用 Nuclei 进行漏洞扫描\n")
            f.write("- 使用 Metasploit 进行漏洞利用\n")
            f.write("- 生成渗透测试报告\n")
            
            # 持续监控建议
            f.write("\n## 🔄 持续监控建议\n\n")
            f.write("1. 配置日志监控\n")
            f.write("2. 配置告警规则\n")
            f.write("3. 定期重新评估\n")
            f.write("4. 更新漏洞库\n")
            
            f.write("\n---\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**生成工具**: 小牛的 SRC 信息收集技能 v2.1 🦞\n")
        
        print(f"[+] 最终报告已生成: {report_path}")

# 使用示例
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 smart_analyzer.py <output_directory>")
        sys.exit(1)
    
    analyzer = SRCAnalyzer(sys.argv[1])
    analyzer.analyze()
```

---

## 🎯 **使用示例**

### **对 jshbank.com 进行智能分析**

```bash
cd /root/.openclaw/workspace/skills/src-recon

# 智能分析
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from smart_analyzer import SRCAnalyzer

# 初始化分析器
analyzer = SRCAnalyzer("output/recon/jshbank.com")

# 执行分析
analyzer.analyze()
EOF
```

---

## 🦞 **总结**

牛哥哥，**SRC 信息收集技能的最终输出非常全面**！🦞

**核心文件**：
1. ✅ **阶段 1**: 子域名收集（all_subs_unique.txt, all_ips_unique.txt）
2. ✅ **阶段 2**: 服务探测（http_services.txt, http_accessible_urls.txt）
3. **✅ 阶段 3**: 然口扫描（port_scan.gnmap, web_ips.txt）
4. ✅ **阶段 4**: 深度分析（jsfind_results/, vulnerability_analysis.txt）
5. ✅ **最终报告**: REPORT.md, ANALYSIS_REPORT.md

**智能分析**：
- 🔍 子域名分类（业务域名、微信小程序、其他）
- 🔍 服务分析（可访问、错误类型、服务器类型）
- 🔍 端口分析（端口分布、开放端口统计）
- 🔍 深度分析（API 端点、路径、敏感信息、高风险问题）
- 🎯 下一步建议（优先级 1/2/3）

**特点**：
- ✅ 全面覆盖 4 个阶段
- ✅ 自动化智能分析
- ✅ 风险评估和优先级排序
- ✅ 详细的修复建议
- ✅ 工具推荐和持续监控建议

**这个技能包非常适合用于 SRC 众测项目的资产收集！🦞**