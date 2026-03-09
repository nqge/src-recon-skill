#!/usr/bin/env python3
"""
API 参数测试工具 - 从 JS 中提取参数并进行构造测试
功能：使用 JS 中提取的 API 端点和参数，构造请求数据包，检测敏感信息泄露
"""

import requests
import urllib3
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class APIParameterTester:
    def __init__(self, target_url, jsfind_dir, max_workers=10):
        self.target_url = target_url.rstrip('/')
        self.jsfind_dir = Path(jsfind_dir)
        self.max_workers = max_workers
        self.results = []
        self.session = requests.Session()
        self.session.verify = False
        
        # 测试参数模板
        self.test_payloads = self._generate_test_payloads()
    
    def _generate_test_payloads(self):
        """生成测试参数模板"""
        # 尝试从外部文件加载 payload
        payload_file = Path(__file__).parent / "payloads.json"
        
        if payload_file.exists():
            try:
                with open(payload_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] 加载外部 payload 文件失败: {e}")
                print(f"[*] 使用默认 payload")
        
        # 默认 payload
        return {
            '通用测试参数': {
                'id': '1',
                'userId': '1',
                'username': 'admin',
                'password': '123456',
                'email': 'test@test.com',
                'phone': '13800138000',
                'token': 'test_token_123',
                'page': '1',
                'size': '10',
                'keyword': 'test',
            },
            'SQL 注入测试': {
                'id': "1' OR '1'='1",
                'userId': "1 UNION SELECT 1,2,3--",
                'username': "admin' OR '1'='1",
                'email': "test@test.com' OR '1'='1",
            },
            'XSS 测试': {
                'keyword': '<script>alert(1)</script>',
                'search': '<img src=x onerror=alert(1)>',
                'content': '<svg onload=alert(1)>',
            },
            '路径遍历测试': {
                'file': '../../../../etc/passwd',
                'path': '../../../etc/passwd',
                'filename': '....//....//....//etc/passwd',
            },
            'SSRF 测试': {
                'url': 'http://127.0.0.1:22',
                'target': 'http://localhost:8080',
                'callback': 'http://169.254.169.254/latest/meta-data/',
            },
            '未授权访问测试': {
                'id': '1',
                'userId': '1',
                'page': '1',
                'size': '100',
            }
        }
    
    def load_api_endpoints(self, api_file=None):
        """加载 API 端点"""
        if api_file is None:
            api_file = self.jsfind_dir / "api_endpoints.txt"
        else:
            api_file = Path(api_file)
        
        if not api_file.exists():
            print(f"[-] API 端点文件不存在: {api_file}")
            return []
        
        with open(api_file, 'r', encoding='utf-8') as f:
            endpoints = [line.strip() for line in f if line.strip()]
        
        print(f"[+] 加载了 {len(endpoints)} 个 API 端点")
        return endpoints
    
    def load_secrets(self):
        """加载敏感信息"""
        secrets_file = self.jsfind_dir / "secrets.txt"
        secrets = {}
        
        if secrets_file.exists():
            with open(secrets_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        secrets[key.strip()] = value.strip()
        
        print(f"[+] 加载了 {len(secrets)} 个敏感信息")
        return secrets
    
    def extract_parameters_from_endpoint(self, endpoint):
        """从 API 端点中提取参数"""
        parameters = []
        
        # 提取路径参数 (例如: /api/users/{id})
        path_params = re.findall(r'\{(\w+)\}', endpoint)
        for param in path_params:
            parameters.append({
                'name': param,
                'type': 'path',
                'required': True
            })
        
        # 提取查询参数 (例如: /api/users?id=1&page=1)
        if '?' in endpoint:
            query_string = endpoint.split('?', 1)[1]
            query_params = query_string.split('&')
            for param in query_params:
                if '=' in param:
                    param_name = param.split('=', 1)[0]
                    parameters.append({
                        'name': param_name,
                        'type': 'query',
                        'required': False
                    })
        
        # 从端点路径推断常见参数
        if 'user' in endpoint.lower():
            parameters.extend([
                {'name': 'userId', 'type': 'query', 'required': False},
                {'name': 'username', 'type': 'query', 'required': False},
            ])
        
        if 'list' in endpoint.lower() or 'query' in endpoint.lower():
            parameters.extend([
                {'name': 'page', 'type': 'query', 'required': False},
                {'name': 'size', 'type': 'query', 'required': False},
                {'name': 'keyword', 'type': 'query', 'required': False},
            ])
        
        return parameters
    
    def construct_request(self, endpoint, payload_type='通用测试参数'):
        """构造请求数据包"""
        # 构造完整 URL
        if endpoint.startswith('/'):
            url = self.target_url + endpoint
        else:
            url = endpoint
        
        # 提取参数
        parameters = self.extract_parameters_from_endpoint(endpoint)
        
        # 构造请求数据包
        request_data = {
            'url': url,
            'method': 'GET',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            },
            'params': {},
            'data': None,
            'json': None,
        }
        
        # 添加测试参数
        payload = self.test_payloads.get(payload_type, self.test_payloads['通用测试参数'])
        
        for param in parameters:
            if param['name'] in payload:
                request_data['params'][param['name']] = payload[param['name']]
        
        # 从端点路径推断 HTTP 方法
        if any(word in endpoint.lower() for word in ['create', 'add', 'save', 'update', 'delete', 'modify']):
            request_data['method'] = 'POST'
            request_data['json'] = payload
        else:
            request_data['method'] = 'GET'
            request_data['params'].update(payload)
        
        return request_data
    
    def send_request(self, request_data):
        """发送请求"""
        try:
            response = self.session.request(
                method=request_data['method'],
                url=request_data['url'],
                headers=request_data['headers'],
                params=request_data['params'],
                data=request_data['data'],
                json=request_data['json'],
                timeout=10,
                allow_redirects=False
            )
            
            return {
                'success': True,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'content_length': len(response.content),
                'request': request_data,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'request': request_data,
            }
    
    def check_sensitive_info(self, response_data):
        """检测敏感信息"""
        sensitive_info = []
        
        if not response_data['success']:
            return sensitive_info
        
        content = response_data['content']
        
        # 敏感信息模式
        patterns = {
            '手机号': r'1[3-9]\d{9}',
            '身份证号': r'\d{17}[\dXx]',
            '银行卡号': r'\d{16,19}',
            '密码': r'(?i)password["\s:]+["\s]*[^\s"\'<>]{6,}',
            'Token': r'(?i)(token|jwt|bearer)["\s:]+["\s]*[^\s"\'<>]{20,}',
            'API Key': r'(?i)(api[_-]?key|access[_-]?token)["\s:]+["\s]*[^\s"\'<>]{20,}',
            '邮箱': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'IP 地址': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            '数据库连接': r'(?i)(mysql|postgresql|mongodb|redis)://[^\s"\'<>]+',
            '内部路径': r'(?i)/(?:home|var|usr|etc|root)/[^\s"\'<>]+',
        }
        
        for info_type, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                sensitive_info.append({
                    'type': info_type,
                    'count': len(matches),
                    'samples': matches[:3],  # 只保存前 3 个样本
                })
        
        return sensitive_info
    
    def test_endpoint(self, endpoint, payload_type='通用测试参数'):
        """测试单个端点"""
        # 构造请求
        request_data = self.construct_request(endpoint, payload_type)
        
        # 发送请求
        response_data = self.send_request(request_data)
        
        # 检测敏感信息
        sensitive_info = self.check_sensitive_info(response_data)
        
        # 评估风险等级
        risk_level = 'INFO'
        if response_data['success']:
            if response_data['status_code'] == 200:
                if sensitive_info:
                    risk_level = 'HIGH'
                elif len(response_data['content']) > 1000:
                    risk_level = 'MEDIUM'
                else:
                    risk_level = 'LOW'
            elif response_data['status_code'] in [401, 403]:
                risk_level = 'LOW'
            elif response_data['status_code'] >= 500:
                risk_level = 'MEDIUM'
        else:
            risk_level = 'ERROR'
        
        return {
            'endpoint': endpoint,
            'payload_type': payload_type,
            'request': request_data,
            'response': response_data,
            'sensitive_info': sensitive_info,
            'risk_level': risk_level,
        }
    
    def run_tests(self, endpoints=None):
        """运行所有测试"""
        if endpoints is None:
            endpoints = self.load_api_endpoints()
        
        print(f"\n[*] 开始测试 {len(endpoints)} 个 API 端点...")
        
        # 测试类型
        test_types = ['通用测试参数', '未授权访问测试', 'SQL 注入测试', 'XSS 测试']
        
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for endpoint in endpoints:
                for test_type in test_types:
                    future = executor.submit(self.test_endpoint, endpoint, test_type)
                    futures.append(future)
            
            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)
                
                # 打印实时结果
                risk_icon = {
                    'HIGH': '🔴',
                    'MEDIUM': '🟡',
                    'LOW': '🟢',
                    'INFO': 'ℹ️',
                    'ERROR': '❌',
                }.get(result['risk_level'], '❓')
                
                print(f"[{risk_icon}] {result['endpoint'][:50]:50s} | {result['payload_type']:20s} | {result['risk_level']:5s}")
        
        self.results = all_results
        return all_results
    
    def generate_report(self, output_file=None):
        """生成测试报告"""
        if not self.results:
            print("[-] 没有测试结果")
            return
        
        # 统计结果
        total = len(self.results)
        high_risk = [r for r in self.results if r['risk_level'] == 'HIGH']
        medium_risk = [r for r in self.results if r['risk_level'] == 'MEDIUM']
        low_risk = [r for r in self.results if r['risk_level'] == 'LOW']
        errors = [r for r in self.results if r['risk_level'] == 'ERROR']
        
        # 生成报告
        report_lines = []
        report_lines.append("# API 参数测试报告")
        report_lines.append("")
        report_lines.append(f"**目标**: {self.target_url}")
        report_lines.append(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # 统计摘要
        report_lines.append("## 📊 统计摘要")
        report_lines.append("")
        report_lines.append(f"- **总测试数**: {total}")
        report_lines.append(f"- **高风险**: {len(high_risk)} 🔴")
        report_lines.append(f"- **中风险**: {len(medium_risk)} 🟡")
        report_lines.append(f"- **低风险**: {len(low_risk)} 🟢")
        report_lines.append(f"- **错误**: {len(errors)} ❌")
        report_lines.append("")
        
        # 高风险问题
        if high_risk:
            report_lines.append("## 🔴 高风险问题（敏感信息泄露）")
            report_lines.append("")
            
            for idx, result in enumerate(high_risk, 1):
                report_lines.append(f"### {idx}. {result['endpoint']}")
                report_lines.append("")
                report_lines.append(f"**测试类型**: {result['payload_type']}")
                report_lines.append(f"**风险等级**: {result['risk_level']}")
                report_lines.append("")
                
                # 请求数据包
                report_lines.append("**请求数据包**:")
                report_lines.append("```http")
                report_lines.append(f"{result['request']['method']} {result['request']['url']} HTTP/1.1")
                for header, value in result['request']['headers'].items():
                    report_lines.append(f"{header}: {value}")
                
                if result['request']['params']:
                    report_lines.append("")
                    report_lines.append(f"Query Parameters:")
                    for key, value in result['request']['params'].items():
                        report_lines.append(f"  {key}={value}")
                
                if result['request']['json']:
                    report_lines.append("")
                    report_lines.append(f"JSON Body:")
                    report_lines.append(json.dumps(result['request']['json'], indent=2, ensure_ascii=False))
                
                report_lines.append("```")
                report_lines.append("")
                
                # 响应状态
                report_lines.append("**响应状态**:")
                report_lines.append(f"- 状态码: {result['response']['status_code']}")
                report_lines.append(f"- 响应大小: {result['response']['content_length']} bytes")
                report_lines.append("")
                
                # 回显内容
                report_lines.append("**回显内容** (前 500 字符):")
                report_lines.append("```json")
                content = result['response']['content']
                report_lines.append(content[:500])
                if len(content) > 500:
                    report_lines.append(f"... (还有 {len(content) - 500} 字符)")
                report_lines.append("```")
                report_lines.append("")
                
                # 敏感信息
                if result['sensitive_info']:
                    report_lines.append("**敏感信息**:")
                    for info in result['sensitive_info']:
                        report_lines.append(f"- {info['type']}: {info['count']} 个")
                        for sample in info['samples']:
                            # 脱敏处理
                            if info['type'] in ['手机号', '身份证号', '银行卡号']:
                                sample = sample[:3] + '*' * (len(sample) - 6) + sample[-3:]
                            report_lines.append(f"  - {sample}")
                    report_lines.append("")
        
        # 中风险问题
        if medium_risk:
            report_lines.append("## 🟡 中风险问题")
            report_lines.append("")
            report_lines.append(f"发现 {len(medium_risk)} 个中风险问题")
            report_lines.append("")
            
            for idx, result in enumerate(medium_risk[:10], 1):  # 只显示前 10 个
                report_lines.append(f"{idx}. {result['endpoint']}")
                report_lines.append(f"   - 状态码: {result['response']['status_code']}")
                report_lines.append(f"   - 响应大小: {result['response']['content_length']} bytes")
                report_lines.append("")
            
            if len(medium_risk) > 10:
                report_lines.append(f"... 还有 {len(medium_risk) - 10} 个中风险问题")
                report_lines.append("")
        
        # 错误
        if errors:
            report_lines.append("## ❌ 错误")
            report_lines.append("")
            report_lines.append(f"发现 {len(errors)} 个错误")
            report_lines.append("")
            
            for idx, result in enumerate(errors[:5], 1):  # 只显示前 5 个
                report_lines.append(f"{idx}. {result['endpoint']}")
                report_lines.append(f"   - 错误: {result['response']['error']}")
                report_lines.append("")
            
            if len(errors) > 5:
                report_lines.append(f"... 还有 {len(errors) - 5} 个错误")
                report_lines.append("")
        
        # 建议
        report_lines.append("## 🚀 修复建议")
        report_lines.append("")
        report_lines.append("### 高优先级")
        report_lines.append("")
        report_lines.append("1. **立即修复敏感信息泄露**")
        report_lines.append("   - 检查所有返回数据的 API 端点")
        report_lines.append("   - 移除敏感信息（手机号、身份证、密码等）")
        report_lines.append("   - 实施数据脱敏")
        report_lines.append("")
        
        report_lines.append("2. **加强访问控制**")
        report_lines.append("   - 为所有 API 端点配置身份验证")
        report_lines.append("   - 实施基于角色的访问控制 (RBAC)")
        report_lines.append("   - 限制未授权访问")
        report_lines.append("")
        
        report_lines.append("3. **输入验证**")
        report_lines.append("   - 验证所有输入参数")
        report_lines.append("   - 防止 SQL 注入和 XSS 攻击")
        report_lines.append("   - 使用参数化查询")
        report_lines.append("")
        
        report_lines.append("### 中优先级")
        report_lines.append("")
        report_lines.append("1. **错误处理**")
        report_lines.append("   - 统一错误响应格式")
        report_lines.append("   - 避免在错误信息中泄露敏感信息")
        report_lines.append("   - 记录详细的错误日志")
        report_lines.append("")
        
        report_lines.append("2. **响应大小限制**")
        report_lines.append("   - 限制 API 响应大小")
        report_lines.append("   - 实施分页")
        report_lines.append("   - 过滤不必要的字段")
        report_lines.append("")
        
        # 保存报告
        report_content = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"[+] 报告已保存: {output_file}")
        
        return report_content


def main():
    if len(sys.argv) < 3:
        print("用法: python3 api_parameter_tester.py <target_url> <jsfind_directory_or_api_file>")
        print("示例: python3 api_parameter_tester.py https://example.com jsfind_results")
        print("      python3 api_parameter_tester.py https://example.com api_endpoints.txt")
        sys.exit(1)
    
    target_url = sys.argv[1]
    input_path = sys.argv[2]
    
    # 创建测试器
    tester = APIParameterTester(target_url, input_path)
    
    # 判断输入是目录还是文件
    input_path_obj = Path(input_path)
    if input_path_obj.is_file():
        # 直接指定 API 端点文件
        endpoints = tester.load_api_endpoints(input_path)
    else:
        # 指定 jsfind_results 目录
        endpoints = tester.load_api_endpoints()
    
    if not endpoints:
        print("[-] 没有找到 API 端点，退出")
        sys.exit(1)
    
    # 运行测试
    tester.run_tests(endpoints=endpoints)
    
    # 生成报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"api_parameter_test_report_{timestamp}.md"
    report = tester.generate_report(report_file)
    
    # 打印摘要
    if report:
        print(f"\n{'='*80}")
        print("测试完成！")
        print(f"{'='*80}")
        print(report[:500])
        print(f"\n完整报告已保存: {report_file}")


if __name__ == "__main__":
    main()
