#!/usr/bin/env python3
"""
VueCrack - Vue.js 应用未授权访问检测工具
用于检测 Vue.js 应用的敏感路由和端点是否可直接访问
"""

import requests
import re
import sys
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class VueCrack:
    """Vue.js 应用安全检测器"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = {
            'vue_detected': False,
            'accessible_routes': [],
            'forbidden_routes': [],
            'error_routes': []
        }

    # Vue.js 指纹模式
    VUE_PATTERNS = [
        r'vue-router',
        r'<div\s+id=["\']app["\']>',
        r'__vue__',
        r'Vue\.(createApp|component)',
        r'v-cloak',
        r'\.vue["\']',
        r'@vue/',
    ]

    # 常见 Vue 路由
    COMMON_ROUTES = [
        '/admin',
        '/dashboard',
        '/settings',
        '/profile',
        '/users',
        '/api',
        '/login',
        '/register',
        '/forgot-password',
        '/reset-password',
        '/config',
        '/debug',
        '/test',
        '/internal',
        '/management',
        '/console',
        '/panel',
        '/control',
        '/monitor',
        '/logs',
        '/export',
        '/import',
        '/upload',
        '/download',
        '/backup',
        '/database',
        '/sql',
        '/graphql',
        '/swagger',
        '/api-docs',
        '/v1/api',
        '/v2/api',
        '/webhook',
        '/webhooks',
        '/tokens',
        '/keys',
        '/secrets',
        '/auth',
        '/oauth',
        '/sso',
        '/jwt',
        '/session',
        '/cookies',
        '/cache',
        '/queue',
        '/jobs',
        '/tasks',
        '/scheduler',
        '/cron',
        '/websockets',
        '/ws',
        '/notifications',
        '/alerts',
        '/reports',
        '/analytics',
        '/statistics',
        '/metrics',
        '/health',
        '/status',
        '/info',
        '/version',
        '/environment',
        '/env',
        '/config.json',
        '/swagger.json',
        '/openapi.json',
        '/graphql',
    ]

    def detect_vue(self, url):
        """
        检测站点是否使用 Vue.js

        Args:
            url: 站点 URL

        Returns:
            bool: 是否检测到 Vue.js
        """
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=False,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            if response.status_code != 200:
                return False

            content = response.text

            # 检查 Vue.js 指纹
            for pattern in self.VUE_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    return True

            # 检查 HTTP 头
            server = response.headers.get('Server', '').lower()
            x_powered_by = response.headers.get('X-Powered-By', '').lower()

            if 'vue' in server or 'vue' in x_powered_by:
                return True

            # 检查 HTML 结构
            if '<div id="app">' in content or '<div id="app"' in content:
                return True

            return False

        except Exception as e:
            return False

    def extract_routes_from_js(self, base_url):
        """
        从 JS 文件中提取 Vue Router 配置的路由

        Args:
            base_url: 基础 URL

        Returns:
            list: 发现的路由列表
        """
        routes = set()

        # 常见 JS 文件
        js_files = [
            '/app.js',
            '/main.js',
            '/index.js',
            '/chunk-vendors.js',
            '/chunk-common.js',
            '/assets/index.js',
            '/static/js/app.js',
            '/js/app.js',
        ]

        for js_path in js_files:
            js_url = urljoin(base_url, js_path)
            try:
                response = requests.get(
                    js_url,
                    timeout=5,
                    verify=False,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )

                if response.status_code == 200:
                    content = response.text

                    # 提取路由配置
                    # Vue Router 3
                    pattern1 = r'path:\s*["\']([^"\']+)["\']'
                    matches = re.findall(pattern1, content)
                    routes.update(matches)

                    # Vue Router 4
                    pattern2 = r'["\']path["\']:\s*["\']([^"\']+)["\']'
                    matches = re.findall(pattern2, content)
                    routes.update(matches)

                    # 路由数组
                    pattern3 = r'routes:\s*\[([^\]]+)\]'
                    matches = re.findall(pattern3, content)
                    for match in matches:
                        routes.update(re.findall(r'["\']([^"\']+)["\']', match))

            except:
                pass

        return list(routes)

    def check_route(self, base_url, route):
        """
        检查单个路由的可访问性

        Args:
            base_url: 基础 URL
            route: 路由路径

        Returns:
            dict: 检查结果
        """
        url = urljoin(base_url, route)

        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=False,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
            )

            return {
                'route': route,
                'url': url,
                'status': response.status_code,
                'accessible': response.status_code == 200,
                'size': len(response.content),
                'content_type': response.headers.get('Content-Type', ''),
                'location': response.headers.get('Location', '') if response.status_code in [301, 302, 303, 307, 308] else ''
            }

        except requests.exceptions.Timeout:
            return {
                'route': route,
                'url': urljoin(base_url, route),
                'status': 'TIMEOUT',
                'accessible': False,
                'error': 'Timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'route': route,
                'url': urljoin(base_url, route),
                'status': 'ERROR',
                'accessible': False,
                'error': 'Connection Error'
            }
        except Exception as e:
            return {
                'route': route,
                'url': urljoin(base_url, route),
                'status': 'ERROR',
                'accessible': False,
                'error': str(e)
            }

    def scan_site(self, url):
        """
        扫描 Vue.js 站点的可访问路由

        Args:
            url: 站点 URL

        Returns:
            dict: 扫描结果
        """
        url = url.rstrip('/')
        print(f"[*] 正在扫描: {url}")

        # 检测 Vue.js
        print("    [*] 检测 Vue.js 框架...")
        is_vue = self.detect_vue(url)

        if not is_vue:
            print(f"    [-] 未检测到 Vue.js 框架")
            return {
                'url': url,
                'vue_detected': False,
                'message': '未检测到 Vue.js 框架'
            }

        print(f"    [+] 检测到 Vue.js 框架")
        self.results['vue_detected'] = True

        # 收集路由
        routes_to_check = set()

        # 从 JS 文件中提取路由
        print("    [*] 从 JS 文件中提取路由...")
        extracted_routes = self.extract_routes_from_js(url)
        print(f"    [+] 发现 {len(extracted_routes)} 个路由")
        routes_to_check.update(extracted_routes)

        # 添加常见路由
        print("    [*] 添加常见路由...")
        routes_to_check.update(self.COMMON_ROUTES)

        # 确保路由以 / 开头
        routes_to_check = {route if route.startswith('/') else f'/{route}' for route in routes_to_check}

        print(f"    [*] 总共检查 {len(routes_to_check)} 个路由...")

        # 检查路由
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.check_route, url, route): route for route in routes_to_check}

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()

                if result['accessible']:
                    self.results['accessible_routes'].append(result)
                elif result['status'] in [401, 403]:
                    self.results['forbidden_routes'].append(result)
                else:
                    self.results['error_routes'].append(result)

                # 进度显示
                if i % 20 == 0 or i == len(routes_to_check):
                    print(f"        进度: {i}/{len(routes_to_check)}")

        # 统计结果
        print(f"    [+] 可访问路由: {len(self.results['accessible_routes'])}")
        print(f"    [+] 需要认证: {len(self.results['forbidden_routes'])}")
        print(f"    [+] 其他: {len(self.results['error_routes'])}")

        return {
            'url': url,
            'vue_detected': True,
            'accessible_routes': len(self.results['accessible_routes']),
            'forbidden_routes': len(self.results['forbidden_routes']),
            'error_routes': len(self.results['error_routes']),
            'total_routes': len(routes_to_check)
        }

    def save_report(self, output_file='vuecrack_report.txt'):
        """保存扫描报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# VueCrack 扫描报告\n\n")
            f.write(f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Vue.js 检测**: {'是' if self.results['vue_detected'] else '否'}\n\n")

            if self.results['vue_detected']:
                f.write(f"**统计信息**:\n")
                f.write(f"- 可访问路由: {len(self.results['accessible_routes'])}\n")
                f.write(f"- 需要认证: {len(self.results['forbidden_routes'])}\n")
                f.write(f"- 其他状态: {len(self.results['error_routes'])}\n\n")

                f.write("## ✅ 可访问路由 (200 OK)\n\n")
                for r in sorted(self.results['accessible_routes'], key=lambda x: x['size'], reverse=True):
                    f.write(f"- [{r['status']}] {r['url']}\n")
                    f.write(f"  路由: {r['route']}\n")
                    f.write(f"  大小: {r['size']} bytes\n")
                    f.write(f"  Content-Type: {r['content_type']}\n")
                    if r.get('location'):
                        f.write(f"  重定向: {r['location']}\n")
                    f.write("\n")

                f.write("## ⚠️  需要认证 (401/403)\n\n")
                for r in self.results['forbidden_routes']:
                    f.write(f"- [{r['status']}] {r['url']}\n")
                    f.write(f"  路由: {r['route']}\n\n")

                f.write("## ❌ 其他状态\n\n")
                for r in self.results['error_routes']:
                    f.write(f"- [{r['status']}] {r['url']}\n")
                    if r.get('error'):
                        f.write(f"  错误: {r['error']}\n")
                    f.write("\n")

        print(f"[+] 报告已保存到: {output_file}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 vuecrack.py <url_list.txt> [output_file]")
        print("")
        print("示例:")
        print("  python3 vuecrack.py sites.txt")
        print("  python3 vuecrack.py sites.txt vue_report.txt")
        print("")
        print("url_list.txt 格式:")
        print("  https://example.com")
        print("  https://admin.example.com")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'vuecrack_report.txt'

    # 读取 URL 列表
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    # 创建扫描器
    cracker = VueCrack(timeout=10, max_workers=30)

    # 扫描所有站点
    print(f"[*] 开始扫描 {len(urls)} 个站点...\n")

    for url in urls:
        try:
            result = cracker.scan_site(url)
            time.sleep(2)  # 避免请求过快
        except Exception as e:
            print(f"[-] 扫描 {url} 时出错: {e}")

    # 保存报告
    print(f"\n[*] 生成报告...")
    cracker.save_report(output_file)

    # 打印统计
    print(f"\n{'='*80}")
    print("VueCrack 扫描完成")
    print(f"{'='*80}")
    print(f"Vue.js 站点: {len([r for r in cracker.results['accessible_routes'] if r])}")
    print(f"可访问路由: {len(cracker.results['accessible_routes'])}")
    print(f"需要认证: {len(cracker.results['forbidden_routes'])}")
    print(f"其他: {len(cracker.results['error_routes'])}")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
