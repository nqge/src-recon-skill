#!/usr/bin/env python3
"""
路径爆破工具 - 自动将提取的路径拼接到站点的目录结构中进行未授权访问测试
"""

import requests
import re
import sys
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json

class PathBruteforcer:
    """路径爆破工具"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = {
            'accessible_urls': [],
            'forbidden_urls': [],
            'error_urls': [],
            'all_tested_urls': []
        }

    def discover_site_structure(self, base_url):
        """
        发现站点的目录结构

        Args:
            base_url: 基础 URL

        Returns:
            list: 目录列表
        """
        directories = set()

        # 基础目录
        common_dirs = [
            '',
            '/api',
            '/v1',
            '/v2',
            '/admin',
            '/api/v1',
            '/api/v2',
            '/graphql',
            '/internal',
            '/management',
            '/console',
            '/dashboard',
            '/config',
            '/test',
            '/debug',
        ]

        directories.update(common_dirs)

        # 尝试发现更多目录
        try:
            response = requests.get(
                base_url,
                timeout=self.timeout,
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            if response.status_code == 200:
                content = response.text

                # 从 HTML 中提取目录
                dir_pattern = r'href=["\'](/[\w-]+/?)["\']'
                dirs = re.findall(dir_pattern, content)
                for dir in dirs:
                    if dir.endswith('/'):
                        directories.add(dir.rstrip('/'))
                    else:
                        # 获取父目录
                        parts = dir.split('/')
                        if len(parts) > 1:
                            parent = '/'.join(parts[:-1])
                            directories.add(parent)
        except:
            pass

        return list(directories)

    def load_paths(self, path_file):
        """
        从文件加载路径列表

        Args:
            path_file: 路径文件路径

        Returns:
            list: 路径列表
        """
        try:
            with open(path_file, 'r') as f:
                paths = [line.strip() for line in f if line.strip()]
            return paths
        except Exception as e:
            print(f"[-] 读取路径文件失败: {e}")
            return []

    def bruteforce_paths(self, base_url, directories, paths):
        """
        对站点的目录结构进行路径拼接和爆破

        Args:
            base_url: 基础 URL
            directories: 目录列表
            paths: 路径列表

        Returns:
            dict: 爆破结果
        """
        print(f"[*] 开始路径拼接和爆破测试...")
        print(f"    目录数: {len(directories)}")
        print(f"    路径数: {len(paths)}")
        print(f"    理论测试数: {len(directories) * len(paths)}")

        # 生成所有测试 URL
        test_urls = []

        for directory in directories:
            for path in paths:
                # 清理路径
                clean_path = path.strip().lstrip('/')

                # 拼接
                if directory:
                    if directory == '':
                        full_path = f"/{clean_path}"
                    else:
                        full_path = f"{directory}/{clean_path}"
                else:
                    full_path = f"/{clean_path}"

                # 确保以 / 开头
                full_path = f"/{full_path.lstrip('/')}"

                test_url = urljoin(base_url, full_path)
                test_urls.append(test_url)

        print(f"    实际测试数: {len(test_urls)}")

        # 去重
        test_urls = list(set(test_urls))
        print(f"    去重后: {len(test_urls)}")

        # 并发测试
        print("    [*] 开始并发测试...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.test_url, url): url for url in test_urls}

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()

                self.results['all_tested_urls'].append(result)

                if result['accessible']:
                    self.results['accessible_urls'].append(result)
                elif result['status'] in [401, 403]:
                    self.results['forbidden_urls'].append(result)
                else:
                    self.results['error_urls'].append(result)

                # 进度显示
                if i % 100 == 0 or i == len(test_urls):
                    print(f"        进度: {i}/{len(test_urls)}")

        return {
            'total_tested': len(test_urls),
            'accessible': len(self.results['accessible_urls']),
            'forbidden': len(self.results['forbidden_urls']),
            'error': len(self.results['error_urls'])
        }

    def test_url(self, url):
        """
        测试单个 URL 的可访问性

        Args:
            url: 完整的 URL

        Returns:
            dict: 测试结果
        """
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=False,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json, text/html'
                }
            )

            return {
                'url': url,
                'status': response.status_code,
                'accessible': response.status_code == 200,
                'size': len(response.content),
                'content_type': response.headers.get('Content-Type', ''),
                'location': response.headers.get('Location', '') if response.status_code in [301, 302, 303, 307, 308] else ''
            }

        except requests.exceptions.Timeout:
            return {
                'url': url,
                'status': 'TIMEOUT',
                'accessible': False,
                'error': 'Timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'url': url,
                'status': 'ERROR',
                'accessible': False,
                'error': 'Connection Error'
            }
        except Exception as e:
            return {
                'url': url,
                'status': 'ERROR',
                'accessible': False,
                'error': str(e)
            }

    def scan_site(self, base_url, path_file):
        """
        扫描站点的路径爆破

        Args:
            base_url: 基础 URL
            path_file: 路径文件

        Returns:
            dict: 扫描结果
        """
        base_url = base_url.rstrip('/')
        print(f"[*] 正在扫描: {base_url}")

        # 发现目录结构
        print("    [*] 发现目录结构...")
        directories = self.discover_site_structure(base_url)
        print(f"    [+] 发现 {len(directories)} 个目录")

        # 加载路径
        print("    [*] 加载路径列表...")
        paths = self.load_paths(path_file)
        print(f"    [+] 加载 {len(paths)} 个路径")

        if not paths:
            print("    [-] 路径文件为空")
            return {
                'url': base_url,
                'tested': 0,
                'accessible': 0,
                'message': '路径文件为空'
            }

        # 路径爆破
        results = self.bruteforce_paths(base_url, directories, paths)

        return {
            'url': base_url,
            'tested': results['total_tested'],
            'accessible': results['accessible'],
            'forbidden': results['forbidden'],
            'error': results['error']
        }

    def save_report(self, output_file='path_bruteforce_report.txt'):
        """保存爆破报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 路径爆破测试报告\n\n")
            f.write(f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(f"**统计信息**:\n")
            f.write(f"- 测试的 URL: {len(self.results['all_tested_urls'])}\n")
            f.write(f"- 可访问: {len(self.results['accessible_urls'])}\n")
            f.write(f"- 需要认证: {len(self.results['forbidden_urls'])}\n")
            f.write(f"- 其他: {len(self.results['error_urls'])}\n\n")

            # 可访问的 URL
            f.write("## ✅ 可访问的 URL (200 OK)\n\n")
            for r in sorted(self.results['accessible_urls'], key=lambda x: x['size'], reverse=True)[:50]:
                f.write(f"- [{r['status']}] {r['url']}\n")
                f.write(f"  大小: {r['size']} bytes\n")
                f.write(f"  Content-Type: {r['content_type']}\n")
                if r.get('location'):
                    f.write(f"  重定向: {r['location']}\n")
                f.write("\n")

            if len(self.results['accessible_urls']) > 50:
                f.write(f"... 还有 {len(self.results['accessible_urls']) - 50} 个可访问的 URL\n\n")

            # 需要认证
            f.write("## ⚠️  需要认证 (401/403)\n\n")
            for r in self.results['forbidden_urls'][:20]:
                f.write(f"- [{r['status']}] {r['url']}\n")
            f.write("\n")

            if len(self.results['forbidden_urls']) > 20:
                f.write(f"... 还有 {len(self.results['forbidden_urls']) - 20} 个需要认证的 URL\n\n")

            # 错误
            f.write("## ❌ 错误\n\n")
            for r in self.results['error_urls'][:20]:
                f.write(f"- [{r['status']}] {r['url']}\n")
                if r.get('error'):
                    f.write(f"  错误: {r['error']}\n")
            f.write("\n")

        print(f"[+] 报告已保存到: {output_file}")

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 path_bruteforcer.py <base_url> <path_file> [output_file]")
        print("")
        print("示例:")
        print("  python3 path_bruteforcer.py https://example.com extracted_paths.txt")
        print("  python3 path_bruteforcer.py https://example.com paths.txt report.txt")
        print("")
        print("说明:")
        print("  此工具会自动发现站点的目录结构，并将提取的路径拼接到目录中进行未授权访问测试")
        sys.exit(1)

    base_url = sys.argv[1]
    path_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else 'path_bruteforce_report.txt'

    # 创建爆破器
    bruteforcer = PathBruteforcer(timeout=10, max_workers=30)

    # 扫描站点
    print(f"[*] 开始路径爆破测试\n")

    result = bruteforcer.scan_site(base_url, path_file)

    # 保存报告
    print(f"\n[*] 生成报告...")
    bruteforcer.save_report(output_file)

    # 打印统计
    print(f"\n{'='*80}")
    print("路径爆破测试完成")
    print(f"{'='*80}")
    print(f"测试的 URL: {result['tested']}")
    print(f"可访问: {result['accessible']}")
    print(f"需要认证: {result['forbidden']}")
    print(f"错误: {result['error']}")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
