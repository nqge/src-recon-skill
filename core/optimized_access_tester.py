#!/usr/bin/env python3
"""
优化版 HTTP/HTTPS 访问测试工具
使用多种方法组合：requests, curl, 浏览器
最大化发现可访问的 URL
"""

import subprocess
import json
import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.ssl_ import create_urllib3_context
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class OptimizedAccessTester:
    """优化版访问测试器"""
    
    def __init__(self, timeout=15, max_workers=5):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []
        
        # 创建自定义 session（如果 requests 可用）
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            
            # 自定义 SSL 适配器（Legacy SSL 支持）
            class FlexibleSSLAdapter(HTTPAdapter):
                def init_poolmanager(self, *args, **kwargs):
                    context = create_urllib3_context()
                    context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
                    kwargs['ssl_context'] = context
                    return super().init_poolmanager(*args, **kwargs)
            
            # 挂载适配器
            self.session.mount('https://', FlexibleSSLAdapter())
            
            # 重试策略
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount('http://', adapter)
    
    def test_with_requests_custom_ssl(self, url):
        """使用 requests（自定义 SSL）测试"""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            return {
                'url': url,
                'method': 'requests (custom SSL)',
                'status_code': response.status_code,
                'title': self.extract_title(response.text),
                'size': len(response.content),
                'accessible': True
            }
        except Exception as e:
            return None
    
    def test_with_curl(self, url):
        """使用 curl 测试"""
        try:
            # 使用 curl -k（忽略 SSL 证书）
            cmd = [
                'curl', '-k', '-sI', 
                '--connect-timeout', str(self.timeout),
                '--max-time', str(self.timeout),
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 5
            )
            
            if result.returncode == 0:
                # 提取状态码
                status_match = re.search(r'HTTP/\d\.\d (\d+)', result.stdout)
                if status_match:
                    status_code = int(status_match.group(1))
                    
                    return {
                        'url': url,
                        'method': 'curl -k',
                        'status_code': status_code,
                        'title': 'N/A',
                        'size': 0,
                        'accessible': True
                    }
        except Exception as e:
            pass
        
        return None
    
    def test_with_curl_follow(self, url):
        """使用 curl -L（跟随重定向）测试"""
        try:
            # 使用 curl -kL（忽略 SSL 证书 + 跟随重定向）
            cmd = [
                'curl', '-kL', '-sI',
                '--connect-timeout', str(self.timeout),
                '--max-time', str(self.timeout),
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 5
            )
            
            if result.returncode == 0:
                # 提取状态码
                status_match = re.search(r'HTTP/\d\.\d (\d+)', result.stdout)
                if status_match:
                    status_code = int(status_match.group(1))
                    
                    return {
                        'url': url,
                        'method': 'curl -kL',
                        'status_code': status_code,
                        'title': 'N/A',
                        'size': 0,
                        'accessible': True
                    }
        except Exception as e:
            pass
        
        return None
    
    def test_with_http_fallback(self, url):
        """HTTP 回退测试（将 HTTPS 转为 HTTP）"""
        if not url.startswith('https://'):
            return None
        
        http_url = url.replace('https://', 'http://')
        
        try:
            response = self.session.get(http_url, timeout=self.timeout)
            return {
                'url': url,
                'method': f'HTTP fallback ({http_url})',
                'status_code': response.status_code,
                'title': self.extract_title(response.text),
                'size': len(response.content),
                'accessible': True
            }
        except Exception as e:
            return None
    
    def test_with_browser_simple(self, url):
        """使用浏览器测试（简化版，使用 curl 模拟）"""
        try:
            # 使用 curl -A 模拟浏览器
            cmd = [
                'curl', '-k', '-s',
                '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '--connect-timeout', str(self.timeout),
                '--max-time', str(self.timeout),
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 5
            )
            
            if result.returncode == 0 and result.stdout:
                # 提取状态码（如果有的话）
                if '200 OK' in result.stdout[:100]:
                    return {
                        'url': url,
                        'method': 'curl (browser UA)',
                        'status_code': 200,
                        'title': self.extract_title(result.stdout),
                        'size': len(result.stdout),
                        'accessible': True
                    }
        except Exception as e:
            pass
        
        return None
    
    def test_url(self, url):
        """使用所有方法测试 URL"""
        methods = [
            self.test_with_requests_custom_ssl,
            self.test_with_curl,
            self.test_with_curl_follow,
            self.test_with_http_fallback,
            self.test_with_browser_simple,
        ]
        
        for method in methods:
            try:
                result = method(url)
                if result and result.get('accessible'):
                    return result
            except:
                continue
        
        return None
    
    def test_urls(self, urls):
        """批量测试 URL"""
        results = {
            'accessible': [],
            'not_accessible': []
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.test_url, url): url for url in urls}
            
            for future in as_completed(futures):
                url = futures[future]
                
                try:
                    result = future.result(timeout=self.timeout + 10)
                    
                    if result:
                        results['accessible'].append(result)
                        print(f"[✅] {url}")
                        print(f"    方法: {result['method']}")
                        print(f"    状态码: {result.get('status_code', 'N/A')}")
                    else:
                        results['not_accessible'].append(url)
                        print(f"[-] {url}")
                        
                except Exception as e:
                    results['not_accessible'].append(url)
                    print(f"[-] {url}")
        
        return results
    
    def extract_title(self, text):
        """从 HTML 中提取标题"""
        title_match = re.search(r'<title>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            return title[:100]  # 限制长度
        return 'N/A'
    
    def save_results(self, output_file, results):
        """保存结果到 Markdown 文件"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# HTTP/HTTPS 访问测试报告（优化版）\n\n")
            f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**方法**: requests + curl + HTTP fallback + Browser UA\n\n")
            
            accessible_count = len(results['accessible'])
            not_accessible_count = len(results['not_accessible'])
            total_count = accessible_count + not_accessible_count
            
            f.write(f"## 📊 统计\n\n")
            f.write(f"- 总计: {total_count} 个 URL\n")
            f.write(f"- 可访问: {accessible_count} 个 ({accessible_count/total_count*100:.1f}%)\n")
            f.write(f"- 不可访问: {not_accessible_count} 个 ({not_accessible_count/total_count*100:.1f}%)\n\n")
            
            # 可访问的 URL
            if results['accessible']:
                f.write(f"## ✅ 可访问的 URL ({len(results['accessible'])} 个)\n\n")
                
                for i, result in enumerate(results['accessible'], 1):
                    f.write(f"### {i}. {result['url']}\n\n")
                    f.write(f"**方法**: {result['method']}\n\n")
                    f.write(f"**状态码**: {result.get('status_code', 'N/A')}\n\n")
                    f.write(f"**标题**: {result.get('title', 'N/A')}\n\n")
                    f.write(f"**大小**: {result.get('size', 0)} bytes\n\n")
                    f.write("---\n\n")
            
            # 不可访问的 URL
            if results['not_accessible']:
                f.write(f"## ❌ 不可访问的 URL ({len(results['not_accessible'])} 个)\n\n")
                
                for url in results['not_accessible']:
                    f.write(f"- {url}\n")
        
        print(f"\n[+] 报告已保存到: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='优化版 HTTP/HTTPS 访问测试工具')
    parser.add_argument('input_file', help='输入文件（每行一个 URL）')
    parser.add_argument('output_file', help='输出报告文件（Markdown 格式）')
    parser.add_argument('--timeout', type=int, default=15, help='超时时间（秒，默认：15）')
    parser.add_argument('--workers', type=int, default=5, help='并发线程数（默认：5）')
    
    args = parser.parse_args()
    
    # 读取 URL
    with open(args.input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"[*] 优化版 HTTP/HTTPS 访问测试工具")
    print(f"[*] 测试 {len(urls)} 个 URL")
    print(f"[*] 超时时间: {args.timeout} 秒")
    print(f"[*] 并发线程: {args.workers}")
    print(f"[*] 方法: requests + curl + HTTP fallback + Browser UA")
    print(f"[*] 开始测试...\n")
    
    # 创建测试器
    tester = OptimizedAccessTester(timeout=args.timeout, max_workers=args.workers)
    
    # 测试 URL
    start_time = time.time()
    results = tester.test_urls(urls)
    elapsed_time = time.time() - start_time
    
    # 统计
    accessible_count = len(results['accessible'])
    not_accessible_count = len(results['not_accessible'])
    total_count = accessible_count + not_accessible_count
    
    print(f"\n[*] 测试完成！")
    print(f"[*] 总耗时: {elapsed_time:.2f}秒")
    print(f"[+] 可访问: {accessible_count} 个")
    print(f"[-] 不可访问: {not_accessible_count} 个")
    
    # 保存结果
    tester.save_results(args.output_file, results)


if __name__ == '__main__':
    main()
