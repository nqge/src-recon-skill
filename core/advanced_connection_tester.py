#!/usr/bin/env python3
"""
改进的连接测试工具 - 支持多种 SSL 配置
"""

import requests
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from datetime import datetime

class AdvancedConnectionTester:
    """高级连接测试器 - 支持多种 SSL 配置"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []

    def test_with_curl(self, url):
        """
        使用 curl 测试（支持更多 SSL 选项）

        Args:
            url: 目标 URL

        Returns:
            dict: 测试结果
        """
        result = {
            'url': url,
            'methods': []
        }

        # 方法 1: 标准 curl
        try:
            cmd = ['curl', '-I', '-s', '-m', str(self.timeout), url]
            proc = subprocess.run(cmd, capture_output=True, timeout=self.timeout + 5)
            if proc.returncode == 0:
                status_line = proc.stdout.decode('utf-8', errors='ignore').split('\n')[0]
                result['methods'].append({
                    'method': 'curl',
                    'status': 'success',
                    'response': status_line
                })
        except Exception as e:
            result['methods'].append({
                'method': 'curl',
                'status': 'failed',
                'error': str(e)
            })

        # 方法 2: curl -k (跳过证书验证)
        try:
            cmd = ['curl', '-k', '-I', '-s', '-m', str(self.timeout), url]
            proc = subprocess.run(cmd, capture_output=True, timeout=self.timeout + 5)
            if proc.returncode == 0:
                status_line = proc.stdout.decode('utf-8', errors='ignore').split('\n')[0]
                result['methods'].append({
                    'method': 'curl -k',
                    'status': 'success',
                    'response': status_line
                })
        except Exception as e:
            result['methods'].append({
                'method': 'curl -k',
                'status': 'failed',
                'error': str(e)
            })

        # 方法 3: curl --ssl-no-revoke (禁用证书吊销检查)
        try:
            cmd = ['curl', '--ssl-no-revoke', '-I', '-s', '-m', str(self.timeout), url]
            proc = subprocess.run(cmd, capture_output=True, timeout=self.timeout + 5)
            if proc.returncode == 0:
                status_line = proc.stdout.decode('utf-8', errors='ignore').split('\n')[0]
                result['methods'].append({
                    'method': 'curl --ssl-no-revoke',
                    'status': 'success',
                    'response': status_line
                })
        except Exception as e:
            result['methods'].append({
                'method': 'curl --ssl-no-revoke',
                'status': 'failed',
                'error': str(e)
            })

        # 方法 4: HTTP 而不是 HTTPS
        if url.startswith('https://'):
            http_url = url.replace('https://', 'http://')
            try:
                cmd = ['curl', '-I', '-s', '-m', str(self.timeout), http_url]
                proc = subprocess.run(cmd, capture_output=True, timeout=self.timeout + 5)
                if proc.returncode == 0:
                    status_line = proc.stdout.decode('utf-8', errors='ignore').split('\n')[0]
                    result['methods'].append({
                        'method': 'HTTP',
                        'status': 'success',
                        'response': status_line
                    })
            except Exception as e:
                result['methods'].append({
                    'method': 'HTTP',
                    'status': 'failed',
                    'error': str(e)
                })

        return result

    def test_url(self, url):
        """
        测试单个 URL 的多种连接方法

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

        # 使用 curl 测试多种方法
        curl_result = self.test_with_curl(url)
        result['all_methods'] = curl_result['methods']

        # 检查是否有成功的方法
        for method_result in curl_result['methods']:
            if method_result['status'] == 'success':
                result['accessible'] = True
                result['working_method'] = method_result['method']
                break

        return result

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
            future_to_url = {executor.submit(self.test_url, url): url for url in urls}

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
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
            f.write("# 高级连接测试报告\n\n")
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
                    f.write(f"**可用方法**: {result['working_method']}\n\n")
                    f.write("**测试方法**:\n\n")
                    for method in result['all_methods']:
                        status_icon = "✅" if method['status'] == 'success' else "❌"
                        f.write(f"- {status_icon} **{method['method']}**: ")
                        if method['status'] == 'success':
                            f.write(f"{method['response']}\n\n")
                        else:
                            f.write(f"{method.get('error', 'Unknown error')}\n\n")

            # 不可访问的 URL
            f.write("## ❌ 不可访问的 URL\n\n")
            for result in results:
                if not result.get('accessible', False):
                    f.write(f"### {result['url']}\n\n")
                    f.write("**测试方法**:\n\n")
                    for method in result['all_methods']:
                        status_icon = "✅" if method['status'] == 'success' else "❌"
                        f.write(f"- {status_icon} **{method['method']}**: ")
                        if method['status'] == 'success':
                            f.write(f"{method['response']}\n\n")
                        else:
                            f.write(f"{method.get('error', 'Unknown error')}\n\n")

            f.write("\n---\n\n")
            f.write("**生成工具**: 高级连接测试工具 🦞\n")

def main():
    if len(sys.argv) < 3:
        print("使用方法: python3 advanced_connection_tester.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # 读取 URL
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    # 测试
    tester = AdvancedConnectionTester(timeout=10, max_workers=15)
    results = tester.test_urls(urls)

    # 生成报告
    tester.generate_report(results, output_file)

    print(f"[+] 测试完成: {len(results)} 个 URL")
    accessible = sum(1 for r in results if r.get('accessible', False))
    print(f"[+] 可访问: {accessible} 个")
    print(f"[+] 报告已保存到: {output_file}")

if __name__ == "__main__":
    main()
