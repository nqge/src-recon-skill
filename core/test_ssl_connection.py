#!/usr/bin/env python3
"""
使用 requests 库测试连接 - 支持自定义 SSL 配置
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
import ssl
import subprocess
import sys
from datetime import datetime

class SSLAdapter(HTTPAdapter):
    """自定义 SSL 适配器 - 支持旧版本 SSL"""

    def init_poolmanager(self, *args, **kwargs):
        # 创建支持旧版本重协商的 SSL 上下文
        context = create_urllib3_context()
        context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

def test_url_with_requests(url):
    """
    使用 requests 库测试 URL（支持旧版本 SSL）

    Args:
        url: 目标 URL

    Returns:
        dict: 测试结果
    """
    result = {
        'url': url,
        'methods': []
    }

    # 方法 1: 标准 requests
    try:
        response = requests.get(url, timeout=10)
        result['methods'].append({
            'method': 'requests',
            'status': 'success',
            'status_code': response.status_code
        })
    except Exception as e:
        result['methods'].append({
            'method': 'requests',
            'status': 'failed',
            'error': str(e)
        })

    # 方法 2: requests + verify=False
    try:
        response = requests.get(url, verify=False, timeout=10)
        result['methods'].append({
            'method': 'requests (verify=False)',
            'status': 'success',
            'status_code': response.status_code
        })
    except Exception as e:
        result['methods'].append({
            'method': 'requests (verify=False)',
            'status': 'failed',
            'error': str(e)
        })

    # 方法 3: requests + 自定义 SSL 适配器
    try:
        session = requests.Session()
        session.mount('https://', SSLAdapter())
        response = session.get(url, timeout=10)
        result['methods'].append({
            'method': 'requests (custom SSL)',
            'status': 'success',
            'status_code': response.status_code
        })
    except Exception as e:
        result['methods'].append({
            'method': 'requests (custom SSL)',
            'status': 'failed',
            'error': str(e)
        })

    # 方法 4: curl -k
    try:
        cmd = ['curl', '-k', '-I', '-s', '-m', '10', url]
        proc = subprocess.run(cmd, capture_output=True, timeout=15)
        if proc.returncode == 0:
            status_line = proc.stdout.decode('utf-8', errors='ignore').split('\n')[0]
            result['methods'].append({
                'method': 'curl -k',
                'status': 'success',
                'response': status_line
            })
        else:
            result['methods'].append({
                'method': 'curl -k',
                'status': 'failed',
                'error': proc.stderr.decode('utf-8', errors='ignore')
            })
    except Exception as e:
        result['methods'].append({
            'method': 'curl -k',
            'status': 'failed',
            'error': str(e)
        })

    return result

def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 test_ssl_connection.py <url>")
        sys.exit(1)

    url = sys.argv[1]

    print(f"[*] 测试 URL: {url}\n")
    result = test_url_with_requests(url)

    print(f"测试结果:\n")
    for method_result in result['methods']:
        status_icon = "✅" if method_result['status'] == 'success' else "❌"
        print(f"{status_icon} {method_result['method']}")
        if method_result['status'] == 'success':
            if 'status_code' in method_result:
                print(f"   状态码: {method_result['status_code']}")
            if 'response' in method_result:
                print(f"   响应: {method_result['response']}")
        else:
            print(f"   错误: {method_result['error']}")
        print()

if __name__ == "__main__":
    main()
