#!/usr/bin/env python3
"""
连接错误和 SSL 错误改进工具
提供多种方法解决常见的网络连接问题
"""

import requests
import socket
import ssl
import OpenSSL
from urllib3.util.ssl_ import create_urllib3_context
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

class ConnectionImprover:
    """连接错误和 SSL 错误改进器"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []

    def diagnose_ssl_error(self, url):
        """
        诊断 SSL 错误

        Args:
            url: 目标 URL

        Returns:
            dict: 诊断结果
        """
        result = {
            'url': url,
            'ssl_issues': [],
            'recommendations': []
        }

        try:
            # 尝试获取证书
            hostname = url.replace('https://', '').split('/')[0]

            # 获取证书
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    # 检查证书过期
                    cert_dict = {k: v for k, v in cert.items() if isinstance(v, (list, tuple, str))}
                    result['certificate'] = cert_dict

                    # 检查证书链
                    try:
                        ssl.match_hostname = lambda cert, hostname: None
                        result['ssl_valid'] = True
                    except Exception as e:
                        result['ssl_issues'].append(f"证书不匹配: {e}")
                        result['ssl_valid'] = False

        except ssl.SSLCertVerificationError as e:
            result['ssl_issues'].append(f"SSL 证书验证失败: {e}")
            result['recommendations'].append("1. 使用 --insecure 跳过证书验证")
            result['recommendations'].append("2. 添加证书到信任存储")
            result['ssl_valid'] = False

        except ssl.SSLError as e:
            result['ssl_issues'].append(f"SSL 错误: {e}")
            result['ssl_valid'] = False

        except Exception as e:
            result['ssl_issues'].append(f"其他错误: {e}")
            result['ssl_valid'] = False

        return result

    def diagnose_connection_error(self, url):
        """
        诊断连接错误

        Args:
            url: 目标 URL

        Returns:
            dict: 诊断结果
        """
        result = {
            'url': url,
            'connection_issues': [],
            'recommendations': []
        }

        hostname = url.replace('http://', '').replace('https://', '').split('/')[0]

        # 测试 DNS 解析
        try:
            ip = socket.gethostbyname(hostname)
            result['dns_ip'] = ip
        except socket.gaierror:
            result['connection_issues'].append("DNS 解析失败")
            result['recommendations'].append("1. 检查域名拼写")
            result['recommendations'].append("2. 尝试使用 IP 地址")
            result['recommendations'].append("3. 检查 DNS 配置")
            return result

        # 测试端口连接
        for port in [80, 443, 8080, 8443]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect((hostname, port))
                sock.close()
                result[f'port_{port}'] = 'open'
            except:
                result[f'port_{port}'] = 'closed'

        # 检查常见问题
        if 'port_80' in result and result['port_80'] == 'closed':
            result['connection_issues'].append("端口 80 关闭")

        if 'port_443' in result and result['port_443'] == 'closed':
            result['connection_issues'].append("端口 443 关闭")

        # 生成建议
        if result['connection_issues']:
            if any('closed' in v for v in result['connection_issues']):
                result['recommendations'].append("1. 端口可能被防火墙阻止")
                result['recommendations'].append("2. 尝试使用 VPN")
                result['recommendations'].append("3. 检查服务器是否运行")

        return result

    def try_multiple_protocols(self, hostname):
        """
        尝试多种协议和端口

        Args:
            hostname: 主机名（不含协议）

        Returns:
            list: 成功的 URL 列表
        """
        successful_urls = []

        # 尝试的协议和端口组合
        combinations = [
            ('http', 80),
            ('https', 443),
            ('http', 8080),
            ('https', 8443),
            ('http', 8888),
            ('https', 9443),
        ]

        for protocol, port in combinations:
            url = f"{protocol}://{hostname}:{port}"

            try:
                response = requests.get(
                    url,
                    timeout=5,
                    verify=False,
                    allow_redirects=True,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )

                if response.status_code in [200, 301, 302, 403, 404]:
                    successful_urls.append({
                        'url': url,
                        'status_code': response.status_code,
                        'protocol': protocol,
                        'port': port
                    })

            except Exception as e:
                pass

        return successful_urls

    def check_with_different_methods(self, url):
        """
        使用不同方法检查 URL

        Args:
            url: 目标 URL

        Returns:
            dict: 检查结果
        """
        result = {
            'url': url,
            'methods': {}
        }

        # 方法 1: 标准 HTTPS（验证证书）
        result['methods']['https_verify'] = self._try_request(url, verify=True)

        # 方法 2: HTTPS（跳过证书验证）
        result['methods']['https_no_verify'] = self._try_request(url, verify=False)

        # 方法 3: HTTP
        http_url = url.replace('https://', 'http://')
        result['methods']['http'] = self._try_request(http_url, verify=False)

        # 方法 4: 使用不同的 User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X)',
            'curl/7.68.0'
        ]

        for ua in user_agents:
            result['methods'][f'ua_{ua[:10]}'] = self._try_request(
                url, verify=False, headers={'User-Agent': ua}
            )

        return result

    def _try_request(self, url, verify=True, headers=None):
        """尝试发送请求"""
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=verify,
                allow_redirects=True,
                headers=headers or {}
            )
            return {
                'success': True,
                'status_code': response.status_code,
                'content_length': len(response.content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def scan_and_improve(self, urls):
        """
        扫描 URL 并尝试改进连接

        Args:
            urls: URL 列表

        Returns:
            list: 改进结果
        """
        print(f"[*] 连接改进扫描")
        print(f"[*] 输入: {len(urls)} 个 URL")
        print("")

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            # 诊断 SSL 错误
            for url in urls:
                if url.startswith('https://'):
                    future = executor.submit(self.diagnose_ssl_error, url)
                    futures[future] = ('ssl', url)

            # 诊断连接错误
            for url in urls:
                future = executor.submit(self.diagnose_connection_error, url)
                futures[future] = ('conn', url)

            # 尝试多种方法
            for url in urls:
                future = executor.submit(self.check_with_different_methods, url)
                futures[future] = ('methods', url)

            for i, future in enumerate(as_completed(futures), 1):
                result_type, url = futures[future]
                result = future.result()
                result['type'] = result_type
                results.append(result)

                # 进度
                if i % 10 == 0 or i == len(futures):
                    print(f"[*] 进度: {i}/{len(futures)}")

        self.results = results
        return results

    def save_report(self, output_file='connection_improvement.txt'):
        """保存改进报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 连接错误和 SSL 错误改进报告\n\n")
            f.write(f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**扫描**: {len(self.results)} 个 URL\n\n")

            # 统计
            ssl_errors = [r for r in self.results if r['type'] == 'ssl']
            conn_errors = [r for r in self.results if r['type'] == 'conn']
            methods_results = [r for r in self.results if r['type'] == 'methods']

            f.write(f"## 📊 统计\n\n")
            f.write(f"- SSL 错误: {len(ssl_errors)} 个\n")
            f.write(f"- 连接错误: {len(conn_errors)} 个\n")
            f.write(f"- 方法测试: {len(methods_results)} 个\n\n")

            # SSL 错误详情
            if ssl_errors:
                f.write(f"## 🔒 SSL 错误分析\n\n")
                for r in ssl_errors[:10]:
                    f.write(f"### {r['url']}\n\n")
                    f.write(f"**问题**:\n")
                    for issue in r.get('ssl_issues', []):
                        f.write(f"- {issue}\n")
                    f.write(f"\n**建议**:\n")
                    for rec in r.get('recommendations', []):
                        f.write(f"{rec}\n")
                    f.write(f"\n")

            # 连接错误详情
            if conn_errors:
                f.write(f"## 🔌 连接错误分析\n\n")
                for r in conn_errors[:10]:
                    f.write(f"### {r['url']}\n\n")
                    f.write(f"**问题**:\n")
                    for issue in r.get('connection_issues', []):
                        f.write(f"- {issue}\n")
                    if 'dns_ip' in r:
                        f.write(f"- DNS 解析: {r['dns_ip']}\n")
                    f.write(f"\n**端口状态**:\n")
                    for port, status in r.items():
                        if port.startswith('port_'):
                            f.write(f"- {port.replace('port_', 'Port ')}: {status}\n")
                    f.write(f"\n**建议**:\n")
                    for rec in r.get('recommendations', []):
                        f.write(f"{rec}\n")
                    f.write(f"\n")

            # 方法测试结果
            if methods_results:
                f.write(f"## 🧪 多方法测试结果\n\n")
                for r in methods_results[:10]:
                    f.write(f"### {r['url']}\n\n")
                    f.write(f"**测试方法**:\n")
                    for method, result in r.get('methods', {}).items():
                        if result.get('success'):
                            f.write(f"- {method}: ✅ {result['status_code']}\n")
                        else:
                            f.write(f"- {method}: ❌ {result.get('error', 'Unknown')}\n")
                    f.write(f"\n")

        print(f"[+] 报告已保存到: {output_file}")

    def generate_solutions_summary(self):
        """生成解决方案摘要"""
        solutions = {}

        for result in self.results:
            if result['type'] == 'ssl':
                for rec in result.get('recommendations', []):
                    solutions[rec] = solutions.get(rec, 0) + 1

            elif result['type'] == 'conn':
                for rec in result.get('recommendations', []):
                    solutions[rec] = solutions.get(rec, 0) + 1

        return sorted(solutions.items(), key=lambda x: x[1], reverse=True)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 connection_improver.py <input_file> [output_file]")
        print("")
        print("功能:")
        print("  1. 诊断 SSL 错误并提供解决方案")
        print("  2. 诊断连接错误并提供解决方案")
        print("  3. 尝试多种协议和端口")
        print("  4. 测试不同的请求方法")
        print("")
        print("示例:")
        print("  python3 connection_improver.py http_services.txt")
        print("  python3 connection_improver.py failed_urls.txt solutions.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'connection_improvement.txt'

    # 读取 URL 列表
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()

        # 提取 URL
        urls = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('http'):
                # 假设是域名，添加协议
                line = f'https://{line}'
            urls.append(line)

    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    # 创建改进器
    improver = ConnectionImprover()

    # 扫描并改进
    results = improver.scan_and_improve(urls)

    # 保存报告
    improver.save_report(output_file)

    # 生成解决方案摘要
    solutions = improver.generate_solutions_summary()

    print(f"\n{'='*80}")
    print("连接改进扫描完成")
    print(f"{'='*80}")
    print(f"扫描: {len(urls)} 个 URL")
    print(f"结果: {len(results)} 项")

    if solutions:
        print(f"\n常见解决方案:")
        for solution, count in solutions[:10]:
            print(f"  {solution} ({count} 次)")

if __name__ == '__main__':
    import time
    main()
