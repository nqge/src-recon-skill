#!/usr/bin/env python3
"""
HTTP/HTTPS 服务扫描器
用于端口扫描后测试 HTTP 和 HTTPS 服务的访问情况
"""

import requests
import sys
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class HTTPScanner:
    """HTTP/HTTPS 服务扫描器"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []

    def extract_title(self, html):
        """提取 HTML 标题"""
        if not html:
            return "N/A"

        # 尝试多种方式提取标题
        patterns = [
            r'<title[^>]*>(.*?)</title>',
            r'<Title[^>]*>(.*?)</Title>',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()
                # 清理标题中的 HTML 实体和多余空格
                title = re.sub(r'<[^>]+>', '', title)
                title = ' '.join(title.split())
                return title[:100]  # 限制长度

        return "N/A"

    def check_url(self, url):
        """
        检查单个 URL 的访问情况

        Returns:
            dict: {
                'url': str,
                'status_code': int,
                'title': str,
                'content_length': int,
                'server': str,
                'error': str (if any)
            }
        """
        result = {
            'url': url,
            'status_code': None,
            'title': 'N/A',
            'content_length': 0,
            'server': 'N/A',
            'error': None
        }

        try:
            # 发送请求
            response = requests.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=False,  # 忽略 SSL 证书验证
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            result['status_code'] = response.status_code
            result['content_length'] = len(response.content)
            result['server'] = response.headers.get('Server', 'N/A')

            # 提取标题
            if 'text/html' in response.headers.get('Content-Type', ''):
                result['title'] = self.extract_title(response.text)

        except requests.exceptions.Timeout:
            result['error'] = 'Timeout'
        except requests.exceptions.SSLError:
            result['error'] = 'SSL Error'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection Error'
        except Exception as e:
            result['error'] = str(e)

        return result

    def scan_urls(self, urls):
        """
        批量扫描 URL 列表

        Args:
            urls: URL 列表

        Returns:
            list: 扫描结果列表
        """
        results = []

        print(f"[*] 开始扫描 {len(urls)} 个 URL...")
        print(f"[*] 并发数: {self.max_workers}, 超时: {self.timeout}s")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_url = {executor.submit(self.check_url, url): url for url in urls}

            # 收集结果
            for i, future in enumerate(as_completed(future_to_url), 1):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)

                    # 进度显示
                    if i % 10 == 0 or i == len(urls):
                        print(f"[*] 进度: {i}/{len(urls)} ({i*100//len(urls)}%)")

                except Exception as e:
                    print(f"[-] 扫描 {url} 时出错: {e}")

        return results

    def print_results(self, results):
        """打印扫描结果"""
        # 按状态码分类
        by_status = {}
        for result in results:
            status = result['status_code'] if result['status_code'] else 'ERROR'
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(result)

        print("\n" + "="*80)
        print("HTTP/HTTPS 服务扫描结果")
        print("="*80)

        # 统计信息
        print(f"\n📊 统计信息:")
        print(f"  总计: {len(results)}")
        for status, items in sorted(by_status.items(), key=lambda x: x[0] if isinstance(x[0], int) else 999):
            print(f"  {status}: {len(items)}")

        # 200 OK
        if 200 in by_status:
            print(f"\n✅ 200 OK ({len(by_status[200])} 个):")
            for result in by_status[200][:20]:  # 只显示前 20 个
                print(f"  [{result['status_code']}] {result['url']}")
                print(f"      标题: {result['title']}")
                print(f"      大小: {result['content_length']} bytes, 服务器: {result['server']}")
            if len(by_status[200]) > 20:
                print(f"  ... 还有 {len(by_status[200]) - 20} 个")

        # 3xx 重定向
        for status in sorted([s for s in by_status.keys() if isinstance(s, int) and 300 <= s < 400]):
            print(f"\n🔄 {status} 重定向 ({len(by_status[status])} 个):")
            for result in by_status[status][:10]:
                print(f"  [{result['status_code']}] {result['url']}")

        # 4xx 客户端错误
        for status in sorted([s for s in by_status.keys() if isinstance(s, int) and 400 <= s < 500]):
            print(f"\n⚠️  {status} 客户端错误 ({len(by_status[status])} 个):")
            for result in by_status[status][:10]:
                print(f"  [{result['status_code']}] {result['url']}")

        # 5xx 服务器错误
        for status in sorted([s for s in by_status.keys() if isinstance(s, int) and 500 <= s < 600]):
            print(f"\n🔥 {status} 服务器错误 ({len(by_status[status])} 个):")
            for result in by_status[status][:10]:
                print(f"  [{result['status_code']}] {result['url']}")

        # 错误
        if 'ERROR' in by_status:
            print(f"\n❌ 错误 ({len(by_status['ERROR'])} 个):")
            for result in by_status['ERROR'][:10]:
                print(f"  [ERROR] {result['url']}")
                print(f"      原因: {result['error']}")

        print("\n" + "="*80)

    def save_report(self, results, output_file='http_scan_report.txt'):
        """保存扫描报告"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# HTTP/HTTPS 服务扫描报告\n\n")
                f.write(f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**总计**: {len(results)} 个 URL\n\n")

                # 按状态码排序
                sorted_results = sorted(
                    results,
                    key=lambda x: x['status_code'] if x['status_code'] else 999
                )

                for result in sorted_results:
                    status = result['status_code'] if result['status_code'] else 'ERROR'
                    f.write(f"[{status}] {result['url']}\n")
                    f.write(f"    标题: {result['title']}\n")
                    f.write(f"    大小: {result['content_length']} bytes\n")
                    f.write(f"    服务器: {result['server']}\n")
                    if result['error']:
                        f.write(f"    错误: {result['error']}\n")
                    f.write("\n")

            print(f"[+] 报告已保存到: {output_file}")

        except Exception as e:
            print(f"[-] 保存报告失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 http_scanner.py <url_list.txt> [output_file]")
        print("")
        print("示例:")
        print("  python3 http_scanner.py urls.txt")
        print("  python3 http_scanner.py urls.txt report.txt")
        print("")
        print("url_list.txt 格式:")
        print("  http://example.com")
        print("  https://example.com")
        print("  https://api.example.com")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'http_scan_report.txt'

    # 读取 URL 列表
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]

        if not urls:
            print("[-] URL 列表为空")
            sys.exit(1)

    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    # 创建扫描器
    scanner = HTTPScanner(timeout=10, max_workers=50)

    # 扫描
    results = scanner.scan_urls(urls)

    # 打印结果
    scanner.print_results(results)

    # 保存报告
    scanner.save_report(results, output_file)

if __name__ == '__main__':
    # 忽略 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
