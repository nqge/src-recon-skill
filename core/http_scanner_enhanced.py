#!/usr/bin/env python3
"""
增强版 HTTP/HTTPS 服务扫描器
- 同时测试 HTTP 和 HTTPS
- 解析子域名的 IP 地址
- 为端口扫描提供 IP 列表
"""

import requests
import socket
import sys
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json

class EnhancedHTTPScanner:
    """增强版 HTTP/HTTPS 服务扫描器"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []
        self.ip_results = {}  # 存储域名到 IP 的映射

    def extract_title(self, html):
        """提取 HTML 标题"""
        if not html:
            return "N/A"

        patterns = [
            r'<title[^>]*>(.*?)</title>',
            r'<Title[^>]*>(.*?)</Title>',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()
                title = re.sub(r'<[^>]+>', '', title)
                title = ' '.join(title.split())
                return title[:100]

        return "N/A"

    def resolve_domain(self, domain):
        """
        解析域名到 IP 地址

        Args:
            domain: 域名（不含协议）

        Returns:
            list: IP 地址列表
        """
        try:
            # 移除端口号（如果有）
            clean_domain = domain.split(':')[0]

            # DNS 解析
            ips = socket.getaddrinfo(clean_domain, None)

            # 提取唯一 IP
            ip_list = list(set([ip[4][0] for ip in ips]))

            return ip_list
        except socket.gaierror:
            return []
        except Exception:
            return []

    def check_url(self, url):
        """
        检查单个 URL 的访问情况

        Args:
            url: 完整 URL（含协议）

        Returns:
            dict: 扫描结果
        """
        result = {
            'url': url,
            'status_code': None,
            'title': 'N/A',
            'content_length': 0,
            'server': 'N/A',
            'content_type': 'N/A',
            'ip_addresses': [],
            'error': None
        }

        try:
            # 解析 URL
            parsed = urlparse(url)
            domain = parsed.netloc

            # 解析 IP
            ips = self.resolve_domain(domain)
            result['ip_addresses'] = ips

            # 存储域名到 IP 的映射
            if ips:
                if domain not in self.ip_results:
                    self.ip_results[domain] = []
                self.ip_results[domain].extend(ips)
                self.ip_results[domain] = list(set(self.ip_results[domain]))

            # 发送请求
            response = requests.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=False,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            result['status_code'] = response.status_code
            result['content_length'] = len(response.content)
            result['server'] = response.headers.get('Server', 'N/A')
            result['content_type'] = response.headers.get('Content-Type', 'N/A')

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

    def scan_domains(self, domains):
        """
        扫描域名列表（同时测试 HTTP 和 HTTPS）

        Args:
            domains: 域名列表（不含协议）

        Returns:
            list: 扫描结果
        """
        urls = []

        # 为每个域名生成 HTTP 和 HTTPS URL
        for domain in domains:
            domain = domain.strip()
            if not domain:
                continue

            # 清理域名（移除协议）
            domain = re.sub(r'^https?://', '', domain)

            # 添加 HTTP 和 HTTPS
            urls.append(f'http://{domain}')
            urls.append(f'https://{domain}')

        print(f"[*] 生成 {len(urls)} 个 URL（HTTP + HTTPS）")

        # 扫描 URLs
        return self.scan_urls(urls)

    def scan_urls(self, urls):
        """
        批量扫描 URL 列表

        Args:
            urls: URL 列表

        Returns:
            list: 扫描结果
        """
        print(f"[*] 开始扫描 {len(urls)} 个 URL...")
        print(f"[*] 并发数: {self.max_workers}, 超时: {self.timeout}s")

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.check_url, url): url for url in urls}

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                results.append(result)

                # 进度显示
                if i % 10 == 0 or i == len(urls):
                    print(f"[*] 进度: {i}/{len(urls)} ({i*100//len(urls)}%)")

        self.results = results
        return results

    def get_all_ips(self):
        """
        获取所有解析到的 IP 地址

        Returns:
            list: 唯一的 IP 地址列表
        """
        all_ips = set()

        for ips in self.ip_results.values():
            all_ips.update(ips)

        return sorted(list(all_ips))

    def get_ip_mapping(self):
        """
        获取域名到 IP 的映射

        Returns:
            dict: {domain: [ip1, ip2, ...]}
        """
        return self.ip_results

    def save_results(self, output_file='http_services.txt'):
        """保存扫描结果"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# HTTP/HTTPS 服务扫描报告\n")
            f.write(f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**总计**: {len(self.results)} 个 URL\n\n")

            # 统计
            status_count = {}
            error_count = {}

            for result in self.results:
                if result['error']:
                    error_count[result['error']] = error_count.get(result['error'], 0) + 1
                elif result['status_code']:
                    status_code = result['status_code']
                    if 200 <= status_code < 300:
                        category = "2xx"
                    elif 300 <= status_code < 400:
                        category = "3xx"
                    elif 400 <= status_code < 500:
                        category = f"{status_code}"
                    elif 500 <= status_code < 600:
                        category = f"{status_code}"
                    else:
                        category = str(status_code)
                    status_count[category] = status_count.get(category, 0) + 1

            f.write(f"## 📊 状态码统计\n\n")
            for status, count in sorted(status_count.items()):
                f.write(f"- {status}: {count}\n")

            if error_count:
                f.write(f"\n## ❌ 错误统计\n\n")
                for error, count in sorted(error_count.items()):
                    f.write(f"- {error}: {count}\n")

            # 详细结果
            f.write(f"\n## 📋 详细结果\n\n")

            for result in self.results:
                url = result['url']
                status = result['status_code']
                error = result['error']
                title = result['title']
                size = result['content_length']
                server = result['server']
                ips = result['ip_addresses']

                if error:
                    f.write(f"[ERROR] {url}\n")
                    f.write(f"    标题: {title}\n")
                    f.write(f"    大小: {size} bytes\n")
                    f.write(f"    服务器: {server}\n")
                    f.write(f"    错误: {error}\n")
                else:
                    f.write(f"[{status}] {url}\n")
                    f.write(f"    标题: {title}\n")
                    f.write(f"    大小: {size} bytes\n")
                    f.write(f"    服务器: {server}\n")
                    if ips:
                        f.write(f"    IP: {', '.join(ips)}\n")
                f.write("\n")

        print(f"[+] 报告已保存到: {output_file}")

    def save_ip_list(self, output_file='resolved_ips.txt'):
        """保存解析的 IP 列表"""
        ips = self.get_all_ips()

        with open(output_file, 'w') as f:
            for ip in ips:
                f.write(ip + '\n')

        print(f"[+] IP 列表已保存到: {output_file} ({len(ips)} 个 IP)")

    def save_ip_mapping(self, output_file='domain_ip_mapping.json'):
        """保存域名到 IP 的映射"""
        with open(output_file, 'w') as f:
            json.dump(self.ip_results, f, indent=2)

        print(f"[+] IP 映射已保存到: {output_file}")

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 http_scanner_enhanced.py <input_file> <output_file> [ips_file] [mapping_file]")
        print("")
        print("示例:")
        print("  python3 http_scanner_enhanced.py subdomains.txt http_services.txt")
        print("  python3 http_scanner_enhanced.py subdomains.txt http_services.txt resolved_ips.txt")
        print("  python3 http_scanner_enhanced.py subdomains.txt http_services.txt resolved_ips.txt mapping.json")
        print("")
        print("说明:")
        print("  input_file - 域名列表（每行一个域名）")
        print("  output_file - HTTP 扫描结果输出文件")
        print("  ips_file - (可选) 解析的 IP 列表输出文件")
        print("  mapping_file - (可选) 域名到 IP 的映射输出文件（JSON 格式）")
        print("")
        print("功能:")
        print("  1. 同时测试 HTTP 和 HTTPS")
        print("  2. 解析域名到 IP 地址")
        print("  3. 为端口扫描提供 IP 列表")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    ips_file = sys.argv[3] if len(sys.argv) > 3 else 'resolved_ips.txt'
    mapping_file = sys.argv[4] if len(sys.argv) > 4 else 'domain_ip_mapping.json'

    # 读取域名列表
    try:
        with open(input_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    # 创建扫描器
    scanner = EnhancedHTTPScanner(timeout=10, max_workers=15)

    # 扫描域名
    print(f"[*] 增强版 HTTP/HTTPS 服务扫描")
    print(f"[*] 输入文件: {input_file} ({len(domains)} 个域名)")
    print(f"[*] 输出文件: {output_file}")
    print("")

    results = scanner.scan_domains(domains)

    # 保存结果
    scanner.save_results(output_file)
    
    # 保存 IP 文件到输出目录
    import os
    output_dir = os.path.dirname(output_file)
    if output_dir:
        ips_file_path = os.path.join(output_dir, os.path.basename(ips_file))
        mapping_file_path = os.path.join(output_dir, os.path.basename(mapping_file))
    else:
        ips_file_path = ips_file
        mapping_file_path = mapping_file
    
    scanner.save_ip_list(ips_file_path)
    scanner.save_ip_mapping(mapping_file_path)

    # 统计
    status_count = {}
    error_count = {}

    for result in results:
        if result['error']:
            error_count[result['error']] = error_count.get(result['error'], 0) + 1
        elif result['status_code']:
            status_code = result['status_code']
            if 200 <= status_code < 300:
                category = "2xx"
            elif 300 <= status_code < 400:
                category = "3xx"
            else:
                category = str(status_code)
            status_count[category] = status_count.get(category, 0) + 1

    # 打印统计
    print(f"\n{'='*80}")
    print("扫描完成")
    print(f"{'='*80}")
    print(f"总计: {len(results)} 个 URL")

    if status_count:
        print("\n状态码统计:")
        for status, count in sorted(status_count.items()):
            print(f"  {status}: {count}")

    if error_count:
        print("\n错误统计:")
        for error, count in sorted(error_count.items()):
            print(f"  {error}: {count}")

    # IP 统计
    ips = scanner.get_all_ips()
    print(f"\n解析的唯一 IP: {len(ips)} 个")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
