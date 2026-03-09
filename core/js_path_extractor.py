#!/usr/bin/env python3
"""
JS 路径提取器 - 从 JavaScript 文件中提取所有路径
即使站点是空白页面或 400 状态，只要能访问 JS 文件就进行提取
"""

import requests
import re
import sys
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class JSPathExtractor:
    """JavaScript 路径提取器"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = {
            'extracted_paths': set(),
            'js_files': set(),
            'failed_urls': []
        }

    # 路径提取正则模式
    PATH_PATTERNS = [
        # 基本路径模式
        r'/(?:[\w-]+/)*[\w-]+',
        
        # API 端点模式
        r'["\']/(?:api|v1|v2|v3)[/\w-]*["\']',
        r'["\']/?[\w-]+/[\w-]+["\']',
        
        # Router 模式
        r'path:\s*["\']([^"\']+)["\']',
        r'route:\s*["\']([^"\']+)["\']',
        r'["\']href["\']:\s*["\']([^"\']+)["\']',
        r'["\']to["\']:\s*["\']([^"\']+)["\']',
        
        # Fetch/Axios 调用
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        r'\$http\.(?:get|post)\(["\']([^"\']+)["\']',
        
        # REST API
        r'@GetMapping\(["\']([^"\']+)["\']',
        r'@PostMapping\(["\']([^"\']+)["\']',
        r'@RequestMapping\(["\']([^"\']+)["\']',
        
        # GraphQL
        r'["\']/(?:graphql|graph)[/\w-]*["\']',
        r'query\s+[a-zA-Z][a-zA-Z0-9_]*\s*\{',
        
        # URL 参数
        r'\?[a-zA-Z_]+=[^"\')\s]+',
    ]

    def find_js_files(self, base_url):
        """
        发现网站中的 JavaScript 文件

        Args:
            base_url: 基础 URL

        Returns:
            list: JS 文件 URL 列表
        """
        js_urls = set()

        # 常见 JS 文件路径
        common_paths = [
            '/app.js',
            '/main.js',
            '/index.js',
            '/bundle.js',
            '/vendor.js',
            '/chunk.js',
            '/runtime.js',
            '/polyfills.js',
            '/styles.js',
            '/common.js',
            '/static/js/app.js',
            '/assets/js/main.js',
            '/assets/index.js',
            '/dist/build.js',
            '/dist/bundle.js',
            '/webpack/bundle.js',
            '/js/app.js',
            '/js/chunk.js',
            '/js/bundle.js',
            '/_next/static/chunks/main.js',
            '/_next/static/chunks/framework.js',
            '/_next/static/chunks/pages/_app.js',
            # Next.js
            '/_next/static/chunks/main-*.js',
            '/_next/static/chunks/framework-*.js',
            # Nuxt.js
            '/_nuxt/*.js',
            '/_nuxt/static/*.js',
        ]

        # 尝试发现 JS 文件
        for path in common_paths:
            js_url = urljoin(base_url, path)
            try:
                response = requests.head(
                    js_url,
                    timeout=5,
                    verify=False,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                if response.status_code == 200:
                    js_urls.add(js_url)
            except:
                pass

        # 如果没有找到，尝试访问主页查找 JS 引用
        if not js_urls:
            try:
                response = requests.get(
                    base_url,
                    timeout=self.timeout,
                    verify=False,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                if response.status_code in [200, 400, 404, 500]:
                    # 从 HTML 中提取 JS 文件引用
                    js_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
                    js_files = re.findall(js_pattern, response.text)
                    for js_file in js_files:
                        if js_file.startswith('http'):
                            js_urls.add(js_file)
                        else:
                            js_urls.add(urljoin(base_url, js_file))
            except:
                pass

        return list(js_urls)

    def extract_paths_from_js(self, js_content):
        """
        从 JavaScript 内容中提取路径

        Args:
            js_content: JavaScript 文件内容

        Returns:
            set: 提取的路径集合
        """
        paths = set()

        for pattern in self.PATH_PATTERNS:
            matches = re.findall(pattern, js_content)
            for match in matches:
                # 清理路径
                if isinstance(match, tuple):
                    match = match[0] if match else ''
                
                # 确保是路径格式
                if match and (match.startswith('/') or match.startswith('?')):
                    # 移除查询字符串后的内容
                    if '?' in match:
                        match = match.split('?')[0]
                    
                    # 只保留合理的路径
                    if len(match) > 2 and len(match) < 200:
                        paths.add(match)

        return paths

    def extract_from_js_file(self, js_url):
        """
        从单个 JS 文件中提取路径

        Args:
            js_url: JS 文件 URL

        Returns:
            dict: 提取结果
        """
        try:
            response = requests.get(
                js_url,
                timeout=self.timeout,
                verify=False,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            if response.status_code != 200:
                return {
                    'js_url': js_url,
                    'status': response.status_code,
                    'paths': [],
                    'error': 'Not accessible'
                }

            js_content = response.text
            paths = self.extract_paths_from_js(js_content)

            return {
                'js_url': js_url,
                'status': response.status_code,
                'paths': list(paths),
                'size': len(js_content)
            }

        except requests.exceptions.Timeout:
            return {
                'js_url': js_url,
                'status': 'TIMEOUT',
                'paths': [],
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'js_url': js_url,
                'status': 'ERROR',
                'paths': [],
                'error': str(e)
            }

    def scan_site(self, url):
        """
        扫描站点并提取所有 JS 文件中的路径

        Args:
            url: 站点 URL

        Returns:
            dict: 扫描结果
        """
        url = url.rstrip('/')
        print(f"[*] 正在扫描: {url}")

        # 发现 JS 文件
        print("    [*] 发现 JS 文件...")
        js_files = self.find_js_files(url)
        
        if not js_files:
            print(f"    [-] 未发现 JS 文件")
            return {
                'url': url,
                'js_files': 0,
                'extracted_paths': 0,
                'message': '未发现 JS 文件'
            }

        print(f"    [+] 发现 {len(js_files)} 个 JS 文件")

        # 提取路径
        print("    [*] 提取路径...")
        all_paths = set()

        for js_url in js_files:
            result = self.extract_from_js_file(js_url)
            
            if result['paths']:
                all_paths.update(result['paths'])
                self.results['js_files'].add(js_url)
            
            # 进度显示
            if len(all_paths) > 0:
                print(f"      {js_url.split('/')[-1]}: {len(result['paths'])} 个路径")

        self.results['extracted_paths'] = all_paths

        print(f"    [+] 总共提取 {len(all_paths)} 个路径")

        return {
            'url': url,
            'js_files': len(js_files),
            'extracted_paths': len(all_paths),
            'unique_paths': len(all_paths)
        }

    def save_results(self, output_file='extracted_paths.txt'):
        """保存提取的路径"""
        # 保存所有路径
        with open(output_file, 'w') as f:
            for path in sorted(self.results['extracted_paths']):
                f.write(f"{path}\n")

        # 保存 JS 文件列表
        with open('js_files_scanned.txt', 'w') as f:
            for js_file in sorted(self.results['js_files']):
                f.write(f"{js_file}\n")

        print(f"\n[+] 结果已保存:")
        print(f"    - {output_file}: {len(self.results['extracted_paths'])} 个路径")
        print(f"    - js_files_scanned.txt: {len(self.results['js_files'])} 个 JS 文件")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 js_path_extractor.py <url_list.txt> [output_file]")
        print("")
        print("示例:")
        print("  python3 js_path_extractor.py urls.txt")
        print("  python3 js_path_extractor.py urls.txt paths.txt")
        print("")
        print("url_list.txt 格式:")
        print("  https://example.com")
        print("  https://api.example.com")
        print("  https://blank.example.com")
        print("")
        print("说明:")
        print("  此工具会提取所有 JS 文件中的路径，即使站点返回 400 或空白页面")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'extracted_paths.txt'

    # 读取 URL 列表
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    # 创建提取器
    extractor = JSPathExtractor(timeout=10, max_workers=30)

    # 扫描所有站点
    print(f"[*] 开始扫描 {len(urls)} 个站点...\n")

    for url in urls:
        try:
            result = extractor.scan_site(url)
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"[-] 扫描 {url} 时出错: {e}")

    # 保存结果
    print(f"\n[*] 生成报告...")
    extractor.save_results(output_file)

    # 打印统计
    print(f"\n{'='*80}")
    print("JS 路径提取完成")
    print(f"{'='*80}")
    print(f"扫描的 JS 文件: {len(extractor.results['js_files'])}")
    print(f"提取的路径: {len(extractor.results['extracted_paths'])}")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
