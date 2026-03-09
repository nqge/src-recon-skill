#!/usr/bin/env python3
"""
改进的 HTTP/HTTPS 访问测试工具
支持多种 SSL 配置和连接方法
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
import ssl
import subprocess
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class FlexibleSSLAdapter(HTTPAdapter):
    """灵活的 SSL 适配器 - 支持多种 SSL 配置"""

    def __init__(self, ssl_options=None):
        self.ssl_options = ssl_options or {}
        super().__init__()

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        
        # 应用 SSL 选项
        if 'check_hostname' in self.ssl_options:
            context.check_hostname = self.ssl_options['check_hostname']
        
        if 'verify_mode' in self.ssl_options:
            context.verify_mode = self.ssl_options['verify_mode']
        
        # 启用旧版本服务器连接
        context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

class HTTPAccessTester:
    """HTTP 访问测试器"""

    def __init__(self, timeout=15, max_workers=10):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []

    def test_url_with_requests(self, url):
        """
        使用 requests 库测试 URL（多种方法）

        Args:
            url: 目标 URL

        Returns:
            dict: 测试结果
        """
        result = {
            'url': url,
            'accessible': False,
            'working_method': None,
            'all_methods': []
        }

        # 方法 1: 标准 requests
        try:
            response = requests.get(url, timeout=self.timeout)
            result['all_methods'].append({
                'method': 'requests',
                'status': 'success',
                'status_code': response.status_code,
                'title': self.extract_title(response)
            })
            result['accessible'] = True
            result['working_method'] = 'requests'
        except Exception as e:
            result['all_methods'].append({
                'method': 'requests',
                'status': 'failed',
                'error': str(e)[:100]
            })

        # 方法 2: requests + verify=False
        if not result['accessible']:
            try:
                response = requests.get(url, verify=False, timeout=self.timeout)
                result['all_methods'].append({
                    'method': 'requests (verify=False)',
                    'status': 'success',
                    'status_code': response.status_code,
                    'title': self.extract_title(response)
                })
                result['accessible'] = True
                result['working_method'] = 'requests (verify=False)'
            except Exception as e:
                result['all_methods'].append({
                    'method': 'requests (verify=False)',
                    'status': 'failed',
                    'error': str(e)[:100]
                })

        # 方法 3: requests + 自定义 SSL 适配器
        if not result['accessible']:
            try:
                session = requests.Session()
                session.mount('https://', FlexibleSSLAdapter({
                    'check_hostname': False,
                    'verify_mode': ssl.CERT_NONE
                }))
                response = session.get(url, timeout=self.timeout)
                result['all_methods'].append({
                    'method': 'requests (custom SSL)',
                    'status': 'success',
                    'status_code': response.status_code,
                    'title': self.extract_title(response)
                })
                result['accessible'] = True
                result['working_method'] = 'requests (custom SSL)'
            except Exception as e:
                result['all_methods'].append({
                    'method': 'requests (custom SSL)',
                    'status': 'failed',
                    'error': str(e)[:100]
                })

        # 方法 4: curl -k
        if not result['accessible']:
            try:
                cmd = ['curl', '-k', '-I', '-s', '-m', str(self.timeout), url]
                proc = subprocess.run(cmd, capture_output=True, timeout=self.timeout + 5)
                if proc.returncode == 0:
                    status_line = proc.stdout.decode('utf-8', errors='ignore').split('\n')[0]
                    result['all_methods'].append({
                        'method': 'curl -k',
                        'status': 'success',
                        'response': status_line[:100]
                    })
                    result['accessible'] = True
                    result['working_method'] = 'curl -k'
                else:
                    result['all_methods'].append({
                        'method': 'curl -k',
                        'status': 'failed',
                        'error': proc.stderr.decode('utf-8', errors='ignore')[:100]
                    })
            except Exception as e:
                result['all_methods'].append({
                    'method': 'curl -k',
                    'status': 'failed',
                    'error': str(e)[:100]
                })

        # 方法 5: HTTP 而不是 HTTPS
        if not result['accessible'] and url.startswith('https://'):
            http_url = url.replace('https://', 'http://')
            try:
                response = requests.get(http_url, timeout=self.timeout)
                result['all_methods'].append({
                    'method': 'HTTP',
                    'status': 'success',
                    'status_code': response.status_code,
                    'title': self.extract_title(response)
                })
                result['accessible'] = True
                result['working_method'] = 'HTTP'
            except Exception as e:
                result['all_methods'].append({
                    'method': 'HTTP',
                    'status': 'failed',
                    'error': str(e)[:100]
                })

        return result

    def extract_title(self, response):
        """从响应中提取标题"""
        try:
            import re
            match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:100]
        except:
            pass
        return None

    def test_urls(self, urls):
        """
        批量测试 URL

        Args:
            urls: URL 列表

        Returns:
            list: 测试结果列表
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.test_url_with_requests, url): url 
                for url in urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 实时输出
                    if result['accessible']:
                        print(f"[✅] {url}")
                        if result.get('working_method'):
                            print(f"    方法: {result['working_method']}")
                    else:
                        print(f"[-] {url}")
                except Exception as e:
                    print(f"[-] {url} - 测试失败: {e}")
                    results.append({
                        'url': url,
                        'accessible': False,
                        'error': str(e)
                    })

        return results

    def generate_report(self, results, output_file):
        """
        生成测试报告

        Args:
            results: 测试结果列表
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# HTTP/HTTPS 访问测试报告\n\n")
            f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试**: {len(results)} 个 URL\n\n")

            # 统计
            accessible = sum(1 for r in results if r.get('accessible', False))
            f.write("## 📊 统计\n\n")
            f.write(f"- 可访问: {accessible} 个\n")
            f.write(f"- 不可访问: {len(results) - accessible} 个\n\n")

            # 可访问的 URL
            f.write("## ✅ 可访问的 URL\n\n")
            for result in results:
                if result.get('accessible', False):
                    f.write(f"### {result['url']}\n\n")
                    f.write(f"**可用方法**: {result.get('working_method', 'N/A')}\n\n")
                    f.write("**测试方法**:\n\n")
                    for method in result.get('all_methods', []):
                        status_icon = "✅" if method['status'] == 'success' else "❌"
                        f.write(f"- {status_icon} **{method['method']}**: ")
                        if method['status'] == 'success':
                            if 'status_code' in method:
                                f.write(f"状态码 {method['status_code']}")
                            if 'title' in method:
                                f.write(f", 标题: {method['title']}")
                            if 'response' in method:
                                f.write(f", {method['response']}")
                            f.write("\n\n")
                        else:
                            f.write(f"{method.get('error', 'Unknown error')}\n\n")
                    f.write("---\n\n")

            # 不可访问的 URL
            f.write("## ❌ 不可访问的 URL\n\n")
            for result in results:
                if not result.get('accessible', False):
                    f.write(f"### {result['url']}\n\n")
                    f.write("**测试方法**:\n\n")
                    for method in result.get('all_methods', []):
                        status_icon = "✅" if method['status'] == 'success' else "❌"
                        f.write(f"- {status_icon} **{method['method']}**: ")
                        if method['status'] == 'success':
                            if 'status_code' in method:
                                f.write(f"状态码 {method['status_code']}")
                            if 'title' in method:
                                f.write(f", 标题: {method['title']}")
                            f.write("\n\n")
                        else:
                            f.write(f"{method.get('error', 'Unknown error')}\n\n")
                    f.write("---\n\n")

            f.write("\n---\n\n")
            f.write("**生成工具**: HTTP/HTTPS 访问测试工具 🦞\n")

def main():
    if len(sys.argv) < 3:
        print("使用方法: python3 http_access_tester.py <input_file> <output_file>")
        print("")
        print("参数:")
        print("  input_file  - 包含 URL 列表的文件（每行一个 URL）")
        print("  output_file - 输出报告文件路径（Markdown 格式）")
        print("")
        print("环境变量:")
        print("  TIMEOUT=15    - 请求超时时间（秒，默认：15）")
        print("  MAX_WORKERS=10 - 并发线程数（默认：10）")
        print("")
        print("示例:")
        print("  python3 http_access_tester.py urls.txt report.md")
        print("  TIMEOUT=30 python3 http_access_tester.py urls.txt report.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # 环境变量
    timeout = int(os.getenv('TIMEOUT', '15'))
    max_workers = int(os.getenv('MAX_WORKERS', '10'))

    # 读取 URL
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    if not urls:
        print("[-] 没有找到 URL")
        sys.exit(1)

    print(f"[*] HTTP/HTTPS 访问测试工具")
    print(f"[*] 测试 {len(urls)} 个 URL")
    print(f"[*] 超时时间: {timeout} 秒")
    print(f"[*] 并发线程: {max_workers}")
    print(f"[*] 开始测试...\n")

    # 测试
    tester = HTTPAccessTester(timeout=timeout, max_workers=max_workers)
    results = tester.test_urls(urls)

    # 生成报告
    tester.generate_report(results, output_file)

    # 统计
    accessible = sum(1 for r in results if r.get('accessible', False))

    print(f"\n[*] 测试完成")
    print(f"[+] 可访问: {accessible} 个")
    print(f"[+] 不可访问: {len(results) - accessible} 个")
    print(f"[+] 报告已保存到: {output_file}")

if __name__ == "__main__":
    main()
