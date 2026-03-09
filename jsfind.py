#!/usr/bin/env python3
"""
JS 文件分析工具 - 提取 API 接口和敏感端点
用于分析 JavaScript 文件中隐藏的 API 接口和路径
"""

import re
import sys
import requests
import time
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

class JSFinder:
    """JavaScript 文件分析器"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = {
            'api_endpoints': set(),
            'paths': set(),
            'secrets': set(),
            'js_files': set(),
            'chunk_files': set()  # 新增：chunk 文件
        }

    # API 端点正则模式
    API_PATTERNS = [
        # REST API
        r'["\']([/a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)["\']',
        r'["\']/(?:api|v1|v2|v3)/[a-zA-Z0-9_-]+["\']',
        r'["\']https?://[^"\']+/api/[a-zA-Z0-9_-]+["\']',
        # GraphQL
        r'["\']/(?:graphql|graph)[a-zA-Z0-9_-]*["\']',
        r'query\s+[a-zA-Z][a-zA-Z0-9_]*\s*\{',
        r'mutation\s+[a-zA-Z][a-zA-Z0-9_]*\s*\(',
        # API 调用
        r'\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.(?:get|post|put|delete)\(["\']([^"\']+)["\']',
        r'\$http\.(?:get|post)\(["\']([^"\']+)["\']',
        # 路由定义
        r'path:\s*["\']([^"\']+)["\']',
        r'router\.[a-z]+\(["\']([^"\']+)["\']',
        r'@Route\(["\']([^"\']+)["\']',
        # Controller
        r'@RequestMapping\(["\']([^"\']+)["\']',
        r'@GetMapping\(["\']([^"\']+)["\']',
    ]

    # Chunk 文件映射模式（Webpack/Vite）
    CHUNK_PATTERNS = [
        r'"(chunk-[a-f0-9]+)":"([a-f0-9]+)"',
        r'"([a-f0-9]+)\.js":"([a-f0-9]+)"',
        r'"(\w+\.\w+)":"([a-f0-9]+)"',
    ]

    # 敏感信息正则模式
    SECRET_PATTERNS = [
        r'["\']([A-Za-z0-9_]{20,})["\']',  # 可能的 token/key
        r'["\'](?:Bearer|Token|API[_-]?KEY|SECRET|PASSWORD)["\']:\s*["\']([^"\']+)["\']',
        r'["\']https?://[^"\']*@[^"\']+["\']',  # URL with credentials
        r'["\'][a-f0-9]{32,}["\']',  # 可能的 hash/key
    ]

    def extract_from_js(self, js_content, url):
        """
        从 JavaScript 内容中提取 API 端点和敏感信息

        Args:
            js_content: JavaScript 文件内容
            url: JS 文件的 URL（用于记录来源）

        Returns:
            dict: 提取的结果
        """
        results = {
            'api_endpoints': set(),
            'paths': set(),
            'secrets': set(),
            'chunk_mappings': set()  # 新增：chunk 映射
        }

        # 提取 API 端点
        for pattern in self.API_PATTERNS:
            matches = re.findall(pattern, js_content)
            for match in matches:
                # 清理和标准化
                endpoint = match.strip().strip('"').strip("'")
                if endpoint and len(endpoint) > 3 and not endpoint.startswith('http'):
                    # 只保留路径类型的端点
                    results['api_endpoints'].add(endpoint)

        # 提取路径
        path_patterns = [
            r'["\'](/[a-zA-Z0-9_/-]+?)["\']',
            r'url:\s*["\']([^"\']+)["\']',
            r'href:\s*["\']([^"\']+)["\']',
        ]
        for pattern in path_patterns:
            matches = re.findall(pattern, js_content)
            for match in matches:
                path = match.strip().strip('"').strip("'")
                if path and path.startswith('/') and len(path) > 2:
                    results['paths'].add(path)

        # 提取敏感信息
        for pattern in self.SECRET_PATTERNS:
            matches = re.findall(pattern, js_content)
            for match in matches:
                if len(match) > 10:  # 过滤掉太短的
                    results['secrets'].add(match)

        # 提取 chunk 文件映射（新增）
        for pattern in self.CHUNK_PATTERNS:
            matches = re.findall(pattern, js_content)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    chunk_name, chunk_hash = match
                    results['chunk_mappings'].add((chunk_name, chunk_hash))

        return results

    def fetch_js(self, url):
        """获取 JavaScript 文件内容"""
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=False,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            if response.status_code == 200 and 'javascript' in response.headers.get('Content-Type', ''):
                return response.text
            return None
        except Exception as e:
            return None

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
            '/static/js/app.js',
            '/assets/js/main.js',
            '/dist/build.js',
            '/webpack/bundle.js',
            '/assets/index.js',  # Vite
            '/js/app.js',
            '/js/chunk.js',
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

        return list(js_urls)

    def extract_chunk_base_path(self, js_url):
        """
        从 JS 文件 URL 中提取 chunk 文件的基础路径

        Args:
            js_url: JS 文件的 URL

        Returns:
            str: chunk 文件的基础路径
        """
        parsed = urlparse(js_url)
        path = parsed.path

        # 提取 JS 文件所在目录
        if '/' in path:
            base_path = path.rsplit('/', 1)[0]
        else:
            base_path = '/'

        # 构造完整的 base URL
        chunk_base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}/"
        return chunk_base_url

    def verify_chunk_files(self, base_url, chunk_mappings, output_file):
        """
        验证和访问 chunk 文件

        Args:
            base_url: 基础 URL
            chunk_mappings: chunk 映射集合 {(chunk_name, chunk_hash)}
            output_file: 输出文件

        Returns:
            list: 可访问的 chunk 文件 URL
        """
        print(f"\n[*] 发现 {len(chunk_mappings)} 个 chunk 映射，开始验证...")

        accessible_chunks = []

        if not chunk_mappings:
            return accessible_chunks

        # 获取第一个 JS 文件的 URL 作为基础（假设所有 chunk 在同一目录）
        # 在实际调用时应该传入具体的主 JS 文件 URL
        chunk_base_url = base_url

        def check_chunk(chunk_mapping):
            try:
                chunk_name, chunk_hash = chunk_mapping

                # 构造 chunk 文件 URL
                # 格式：chunk-xxxxxx.js 或 chunk-xxxxxx.yyyyyy.js
                chunk_url = urljoin(chunk_base_url, f"{chunk_name}.js")

                response = requests.get(
                    chunk_url,
                    timeout=5,
                    verify=False,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )

                return {
                    'chunk_name': chunk_name,
                    'chunk_hash': chunk_hash,
                    'url': chunk_url,
                    'status': response.status_code,
                    'accessible': response.status_code == 200,
                    'size': len(response.content) if response.status_code == 200 else 0
                }
            except Exception as e:
                return {
                    'chunk_name': chunk_name,
                    'chunk_hash': chunk_hash,
                    'url': urljoin(chunk_base_url, f"{chunk_name}.js"),
                    'status': 'ERROR',
                    'accessible': False,
                    'error': str(e)
                }

        # 并发验证
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(check_chunk, mapping): mapping for mapping in chunk_mappings}
            results = []
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                results.append(result)
                if i % 20 == 0:
                    print(f"    进度: {i}/{len(chunk_mappings)}")

        # 保存结果
        with open(output_file, 'w') as f:
            f.write("# Chunk 文件验证结果\n\n")
            f.write(f"**基础 URL**: {chunk_base_url}\n")
            f.write(f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## ✅ 可访问的 Chunk 文件\n\n")
            for r in results:
                if r['accessible']:
                    f.write(f"- [{r['status']}] {r['url']}\n")
                    f.write(f"  Chunk: {r['chunk_name']}, Hash: {r['chunk_hash']}, Size: {r['size']} bytes\n")
                    accessible_chunks.append(r['url'])

            f.write("\n## ⚠️ 不可访问的 Chunk 文件\n\n")
            for r in results:
                if not r['accessible'] and r['status'] != 'ERROR':
                    f.write(f"- [{r['status']}] {r['url']}\n")

            f.write("\n## ❌ 错误\n\n")
            for r in results:
                if r['status'] == 'ERROR':
                    f.write(f"- [ERROR] {r['url']}: {r.get('error', 'Unknown')}\n")

        print(f"[+] Chunk 验证完成，结果已保存到: {output_file}")
        print(f"[+] 发现 {len(accessible_chunks)} 个可访问的 chunk 文件")

        return accessible_chunks

    def analyze_site(self, url):
        """
        分析单个站点的 JavaScript 文件

        Args:
            url: 网站 URL

        Returns:
            dict: 分析结果
        """
        print(f"[*] 正在分析: {url}")

        # 发现 JS 文件
        js_files = self.find_js_files(url)
        print(f"    发现 {len(js_files)} 个 JS 文件")

        chunk_mappings_all = set()

        # 分析每个 JS 文件
        for js_url in js_files:
            print(f"    分析: {js_url}")
            self.results['js_files'].add(js_url)

            js_content = self.fetch_js(js_url)
            if js_content:
                extracted = self.extract_from_js(js_content, js_url)

                self.results['api_endpoints'].update(extracted['api_endpoints'])
                self.results['paths'].update(extracted['paths'])
                self.results['secrets'].update(extracted['secrets'])
                chunk_mappings_all.update(extracted.get('chunk_mappings', set()))

                print(f"      API 端点: {len(extracted['api_endpoints'])}")
                print(f"      路径: {len(extracted['paths'])}")
                print(f"      敏感信息: {len(extracted['secrets'])}")

                if extracted.get('chunk_mappings'):
                    print(f"      Chunk 映射: {len(extracted['chunk_mappings'])}")

        # 验证 chunk 文件
        if chunk_mappings_all:
            print(f"\n[*] 发现 chunk 映射，开始验证 chunk 文件...")
            chunk_base_url = self.extract_chunk_base_path(js_files[0] if js_files else url)
            accessible_chunks = self.verify_chunk_files(
                chunk_base_url,
                chunk_mappings_all,
                'chunk_verification.txt'
            )
            self.results['chunk_files'].update(accessible_chunks)

        return {
            'url': url,
            'js_files': list(js_files),
            'api_endpoints': len(self.results['api_endpoints']),
            'paths': len(self.results['paths']),
            'secrets': len(self.results['secrets']),
            'chunk_files': len(self.results['chunk_files'])
        }

    def analyze_sites(self, urls):
        """
        批量分析多个站点

        Args:
            urls: URL 列表

        Returns:
            dict: 所有分析结果
        """
        print(f"[*] 开始分析 {len(urls)} 个站点...")

        for url in urls:
            try:
                self.analyze_site(url.rstrip('/'))
                time.sleep(1)  # 避免请求过快
            except Exception as e:
                print(f"[-] 分析 {url} 时出错: {e}")

        return self.results

    def verify_endpoints(self, base_url, endpoints, output_file):
        """
        验证发现的端点是否可访问

        Args:
            base_url: 基础 URL
            endpoints: 端点列表
            output_file: 输出文件

        Returns:
            list: 可访问的端点
        """
        print(f"\n[*] 验证 {len(endpoints)} 个端点...")

        accessible = []

        def check_endpoint(endpoint):
            try:
                full_url = urljoin(base_url, endpoint)
                response = requests.get(
                    full_url,
                    timeout=5,
                    verify=False,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                return {
                    'endpoint': endpoint,
                    'url': full_url,
                    'status': response.status_code,
                    'accessible': response.status_code == 200
                }
            except Exception as e:
                return {
                    'endpoint': endpoint,
                    'url': urljoin(base_url, endpoint),
                    'status': 'ERROR',
                    'accessible': False,
                    'error': str(e)
                }

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(check_endpoint, endpoint): endpoint for endpoint in endpoints}
            results = []
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                results.append(result)
                if i % 10 == 0:
                    print(f"    进度: {i}/{len(endpoints)}")

        # 保存结果
        with open(output_file, 'w') as f:
            f.write("# API 端点验证结果\n\n")
            f.write(f"**基础 URL**: {base_url}\n")
            f.write(f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## ✅ 可访问端点 (200 OK)\n\n")
            for r in results:
                if r['accessible']:
                    f.write(f"- [{r['status']}] {r['url']}\n")
                    accessible.append(r['url'])

            f.write("\n## ⚠️ 其他响应\n\n")
            for r in results:
                if not r['accessible'] and r['status'] != 'ERROR':
                    f.write(f"- [{r['status']}] {r['url']}\n")

            f.write("\n## ❌ 错误\n\n")
            for r in results:
                if r['status'] == 'ERROR':
                    f.write(f"- [ERROR] {r['url']}: {r.get('error', 'Unknown')}\n")

        print(f"[+] 验证完成，结果已保存到: {output_file}")
        print(f"[+] 发现 {len(accessible)} 个可访问端点")

        return accessible

    def save_results(self, output_dir='jsfind_results'):
        """保存分析结果"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # 保存 API 端点
        with open(f'{output_dir}/api_endpoints.txt', 'w') as f:
            for endpoint in sorted(self.results['api_endpoints']):
                f.write(f"{endpoint}\n")

        # 保存路径
        with open(f'{output_dir}/paths.txt', 'w') as f:
            for path in sorted(self.results['paths']):
                f.write(f"{path}\n")

        # 保存敏感信息
        with open(f'{output_dir}/secrets.txt', 'w') as f:
            for secret in sorted(self.results['secrets']):
                f.write(f"{secret}\n")

        # 保存 JS 文件列表
        with open(f'{output_dir}/js_files.txt', 'w') as f:
            for js_file in sorted(self.results['js_files']):
                f.write(f"{js_file}\n")

        # 保存可访问的 chunk 文件（新增）
        with open(f'{output_dir}/accessible_chunks.txt', 'w') as f:
            for chunk_url in sorted(self.results['chunk_files']):
                f.write(f"{chunk_url}\n")

        print(f"\n[+] 结果已保存到: {output_dir}/")
        print(f"    - api_endpoints.txt: {len(self.results['api_endpoints'])} 个 API 端点")
        print(f"    - paths.txt: {len(self.results['paths'])} 个路径")
        print(f"    - secrets.txt: {len(self.results['secrets'])} 个敏感信息")
        print(f"    - js_files.txt: {len(self.results['js_files'])} 个 JS 文件")
        print(f"    - accessible_chunks.txt: {len(self.results['chunk_files'])} 个可访问 chunk 文件")
        if os.path.exists('chunk_verification.txt'):
            print(f"    - chunk_verification.txt: 详细 chunk 验证结果")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 jsfind.py <url_list.txt> [output_dir]")
        print("")
        print("示例:")
        print("  # 分析站点列表")
        print("  python3 jsfind.py sites.txt")
        print("")
        print("  # 指定输出目录")
        print("  python3 jsfind.py sites.txt my_results")
        print("")
        print("url_list.txt 格式:")
        print("  https://example.com")
        print("  https://api.example.com")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'jsfind_results'

    # 读取 URL 列表
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    # 创建分析器
    finder = JSFinder(timeout=10, max_workers=30)

    # 分析站点
    results = finder.analyze_sites(urls)

    # 保存结果
    finder.save_results(output_dir)

    # 验证发现的端点（针对第一个站点）
    if urls and results['api_endpoints']:
        print(f"\n[*] 验证发现的端点...")
        finder.verify_endpoints(
            urls[0],
            list(results['api_endpoints']),
            f'{output_dir}/verified_endpoints.txt'
        )

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
