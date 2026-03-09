#!/usr/bin/env python3
"""
Spring Boot Actuator 漏洞检测工具
用于检测 Spring Boot Actuator 框架的未授权访问和敏感端点
"""

import requests
import re
import sys
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json

class ActuatorScanner:
    """Spring Boot Actuator 扫描器"""

    def __init__(self, timeout=10, max_workers=15):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = {
            'actuator_detected': False,
            'accessible_endpoints': [],
            'forbidden_endpoints': [],
            'error_endpoints': []
        }

    # Spring Boot Actuator 指纹模式
    ACTUATOR_PATTERNS = [
        r'spring-boot-actuator',
        r'actuator',
        r'application/json',
        r'"_links"',
        r'"self"',
        r'"health"',
        r'"info"',
        r'"metrics"',
        r'{"href":"http',
        r'spring-boot',
        r'x-application-context',
    ]

    # Spring Boot Actuator 端点列表
    ACTUATOR_ENDPOINTS = {
        # 常见端点
        '/actuator': None,
        '/actuator/health': None,
        '/actuator/info': None,
        '/actuator/metrics': None,
        '/actuator/env': None,
        '/actuator/configprops': None,
        '/actuator/threaddump': None,
        '/actuator/heapdump': None,
        '/actuator/logfile': None,
        '/actuator/auditevents': None,
        '/actuator/mappings': None,
        '/actuator/trace': None,
        '/actuator/caches': None,
        '/actuator/scheduledtasks': None,
        '/actuator/httptrace': None,
        '/actuator/beans': None,
        '/actuator/conditions': None,
        '/actuator/startup': None,
        '/actuator/shutdown': None,
        '/actuator/dump': None,
        '/actuator/flyway': None,
        '/actuator/languages': None,
        '/actuator/liquibase': None,
        '/actuator/loggers': None,
        '/actuator/quartz': None,
        '/actuator/sessions': None,
        '/actuator/statistics': None,
        '/actuator/gateway': None,
        '/actuator/hystrix.stream': None,
        '/actuator/refresh': None,
        '/actuator/features': None,
        '/actuator/function': None,
        '/actuator/custom': None,
        
        # 旧版端点（无 /actuator 前缀）
        '/health': None,
        '/info': None,
        '/metrics': None,
        '/env': None,
        '/configprops': None,
        '/threaddump': None,
        '/heapdump': None,
        '/logfile': None,
        '/auditevents': None,
        '/mappings': None,
        '/trace': None,
        '/caches': None,
        '/scheduledtasks': None,
        '/httptrace': None,
        '/beans': None,
        '/conditions': None,
        '/startup': None,
        '/shutdown': None,
        '/dump': None,
        '/flyway': None,
        '/languages': None,
        '/liquibase': None,
        '/loggers': None,
        '/quartz': None,
        '/sessions': None,
        '/statistics': None,
        '/gateway': None,
        '/hystrix.stream': None,
        '/refresh': None,
        
        # 其他可能的路径
        '/admin/actuator': None,
        '/management/actuator': None,
        '/api/actuator': None,
        '/monitor/actuator': None,
        '/cloudfoundryapplication': None,
        '/eureka': None,
        '/hystrix': None,
        '/turbine.stream': None,
        '/api/docs': None,
        '/swagger-ui.html': None,
        '/swagger-ui': None,
        '/swagger': None,
        '/v3/api-docs': None,
        '/v2/api-docs': None,
        '/api-docs': None,
        '/spring-cloud-consul': None,
        '/service-registry': None,
        '/archaius': None,
    }

    def detect_actuator(self, url):
        """
        检测站点是否使用 Spring Boot Actuator

        Args:
            url: 站点 URL

        Returns:
            bool: 是否检测到 Actuator
        """
        # 优先检查 /actuator 端点
        test_urls = [
            urljoin(url, '/actuator'),
            urljoin(url, '/actuator/health'),
            urljoin(url, '/health'),
        ]

        for test_url in test_urls:
            try:
                response = requests.get(
                    test_url,
                    timeout=self.timeout,
                    verify=False,
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Accept': 'application/json'
                    }
                )

                if response.status_code == 200:
                    content = response.text

                    # 检查 Actuator 特征
                    for pattern in self.ACTUATOR_PATTERNS:
                        if re.search(pattern, content, re.IGNORECASE):
                            return True

                    # 检查 JSON 响应结构
                    try:
                        json_data = json.loads(content)
                        if isinstance(json_data, dict):
                            # Actuator 响应通常包含这些字段
                            if any(key in json_data for key in ['_links', 'status', 'health', 'groups']):
                                return True
                    except:
                        pass

            except:
                pass

        return False

    def extract_endpoints_from_actuator(self, url):
        """
        从 /actuator 端点提取所有可用的端点列表

        Args:
            url: 基础 URL

        Returns:
            list: 端点列表
        """
        endpoints = []

        try:
            # 访问 /actuator 端点
            actuator_url = urljoin(url, '/actuator')
            response = requests.get(
                actuator_url,
                timeout=self.timeout,
                verify=False,
                headers={'Accept': 'application/json'}
            )

            if response.status_code == 200:
                try:
                    data = json.loads(response.text)

                    # 提取 _links 中的端点
                    if '_links' in data:
                        for key, value in data['_links'].items():
                            if isinstance(value, dict) and 'href' in value:
                                href = value['href']
                                # 提取相对路径
                                parsed = urlparse(href)
                                if parsed.path:
                                    endpoints.append(parsed.path)

                    # 揰录发现的所有端点
                    if isinstance(data, dict):
                        for key in data.keys():
                            if key not in ['_links']:
                                endpoints.append(f'/actuator/{key}')

                except:
                    pass

        except:
            pass

        return endpoints

    def check_endpoint(self, base_url, endpoint):
        """
        检查单个 Actuator 端点的可访问性

        Args:
            base_url: 基础 URL
            endpoint: 端点路径

        Returns:
            dict: 检查结果
        """
        url = urljoin(base_url, endpoint)

        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=False,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json'
                }
            )

            result = {
                'endpoint': endpoint,
                'url': url,
                'status': response.status_code,
                'accessible': response.status_code == 200,
                'size': len(response.content),
                'content_type': response.headers.get('Content-Type', ''),
            }

            # 尝试解析 JSON 响应
            try:
                json_data = json.loads(response.text)
                result['is_json'] = True

                # 检查敏感信息
                if endpoint in ['/actuator/env', '/env']:
                    result['sensitive_data'] = 'env'

                    # 检查是否包含敏感信息
                    content = json.dumps(json_data)
                    if 'password' in content.lower() or 'secret' in content.lower():
                        result['has_secrets'] = True

                elif endpoint in ['/actuator/configprops', '/configprops']:
                    result['sensitive_data'] = 'configprops'

                elif endpoint in ['/actuator/heapdump', '/heapdump']:
                    result['sensitive_data'] = 'heapdump'

                elif endpoint in ['/actuator/threaddump', '/threaddump']:
                    result['sensitive_data'] = 'threaddump'

            except:
                result['is_json'] = False

            return result

        except requests.exceptions.Timeout:
            return {
                'endpoint': endpoint,
                'url': urljoin(base_url, endpoint),
                'status': 'TIMEOUT',
                'accessible': False,
                'error': 'Timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'endpoint': endpoint,
                'url': urljoin(base_url, endpoint),
                'status': 'ERROR',
                'accessible': False,
                'error': 'Connection Error'
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'url': urljoin(base_url, endpoint),
                'status': 'ERROR',
                'accessible': False,
                'error': str(e)
            }

    def scan_site(self, url):
        """
        扫描 Spring Boot Actuator 端点

        Args:
            url: 站点 URL

        Returns:
            dict: 扫描结果
        """
        url = url.rstrip('/')
        print(f"[*] 正在扫描: {url}")

        # 检测 Actuator
        print("    [*] 检测 Spring Boot Actuator 框架...")
        is_actuator = self.detect_actuator(url)

        if not is_actuator:
            print(f"    [-] 未检测到 Spring Boot Actuator")
            return {
                'url': url,
                'actuator_detected': False,
                'message': '未检测到 Spring Boot Actuator'
            }

        print(f"    [+] 检测到 Spring Boot Actuator")
        self.results['actuator_detected'] = True

        # 收集端点
        endpoints_to_check = set()

        # 从 /actuator 提取端点
        print("    [*] 从 /actuator 提取端点列表...")
        extracted_endpoints = self.extract_endpoints_from_actuator(url)
        if extracted_endpoints:
            print(f"    [+] 提取到 {len(extracted_endpoints)} 个端点")
            endpoints_to_check.update(extracted_endpoints)

        # 添加常见端点
        print("    [*] 添加常见 Actuator 端点...")
        endpoints_to_check.update(self.ACTUATOR_ENDPOINTS.keys())

        print(f"    [*] 总共检查 {len(endpoints_to_check)} 个端点...")

        # 检查端点
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.check_endpoint, url, endpoint): endpoint for endpoint in endpoints_to_check}

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()

                if result['accessible']:
                    self.results['accessible_endpoints'].append(result)
                elif result['status'] in [401, 403]:
                    self.results['forbidden_endpoints'].append(result)
                else:
                    self.results['error_endpoints'].append(result)

                # 进度显示
                if i % 20 == 0 or i == len(endpoints_to_check):
                    print(f"        进度: {i}/{len(endpoints_to_check)}")

        # 统计结果
        accessible_sensitive = [r for r in self.results['accessible_endpoints'] if r.get('sensitive_data')]

        print(f"    [+] 可访问端点: {len(self.results['accessible_endpoints'])}")
        if accessible_sensitive:
            print(f"    [!] 可访问敏感端点: {len(accessible_sensitive)}")
        print(f"    [+] 需要认证: {len(self.results['forbidden_endpoints'])}")
        print(f"    [+] 其他: {len(self.results['error_endpoints'])}")

        return {
            'url': url,
            'actuator_detected': True,
            'accessible_endpoints': len(self.results['accessible_endpoints']),
            'accessible_sensitive_endpoints': len(accessible_sensitive),
            'forbidden_endpoints': len(self.results['forbidden_endpoints']),
            'error_endpoints': len(self.results['error_endpoints']),
            'total_endpoints': len(endpoints_to_check)
        }

    def check_vulnerabilities(self):
        """
        检查发现的漏洞

        Returns:
            list: 漏洞列表
        """
        vulnerabilities = []

        for endpoint in self.results['accessible_endpoints']:
            # 未授权访问 /env 端点
            if endpoint.get('sensitive_data') == 'env':
                vulnerabilities.append({
                    'type': '未授权访问 - 环境变量',
                    'severity': 'HIGH',
                    'endpoint': endpoint['endpoint'],
                    'url': endpoint['url'],
                    'description': '可以直接访问 /env 端点，可能泄露敏感配置信息'
                })

                if endpoint.get('has_secrets'):
                    vulnerabilities.append({
                        'type': '敏感信息泄露',
                        'severity': 'CRITICAL',
                        'endpoint': endpoint['endpoint'],
                        'url': endpoint['url'],
                        'description': '/env 端点响应中包含密码或密钥'
                    })

            # 未授权访问 /configprops 端点
            elif endpoint.get('sensitive_data') == 'configprops':
                vulnerabilities.append({
                    'type': '未授权访问 - 配置属性',
                    'severity': 'HIGH',
                    'endpoint': endpoint['endpoint'],
                    'url': endpoint['url'],
                    'description': '可以直接访问 /configprops 端点，可能泄露配置信息'
                })

            # 未授权访问 /heapdump 端点
            elif endpoint.get('sensitive_data') == 'heapdump':
                vulnerabilities.append({
                    'type': '未授权访问 - 堆转储',
                    'severity': 'CRITICAL',
                    'endpoint': endpoint['endpoint'],
                    'url': endpoint['url'],
                    'description': '可以直接访问 /heapdump 端点，可能泄露内存敏感信息'
                })

            # 未授权访问 /threaddump 端点
            elif endpoint.get('sensitive_data') == 'threaddump':
                vulnerabilities.append({
                    'type': '未授权访问 - 线程转储',
                    'severity': 'MEDIUM',
                    'endpoint': endpoint['endpoint'],
                    'url': endpoint['url'],
                    'description': '可以直接访问 /threaddump 端点，可能泄露线程信息'
                })

        return vulnerabilities

    def save_report(self, output_file='actuator_report.txt'):
        """保存扫描报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Spring Boot Actuator 扫描报告\n\n")
            f.write(f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Actuator 检测**: {'是' if self.results['actuator_detected'] else '否'}\n\n")

            if self.results['actuator_detected']:
                # 检查漏洞
                vulnerabilities = self.check_vulnerabilities()

                f.write(f"**统计信息**:\n")
                f.write(f"- 可访问端点: {len(self.results['accessible_endpoints'])}\n")
                f.write(f"- 需要认证: {len(self.results['forbidden_endpoints'])}\n")
                f.write(f"- 其他状态: {len(self.results['error_endpoints'])}\n")
                f.write(f"- 发现漏洞: {len(vulnerabilities)}\n\n")

                # 漏洞列表
                if vulnerabilities:
                    f.write("## 🔴 漏洞列表\n\n")
                    for vuln in vulnerabilities:
                        f.write(f"### {vuln['type']} [{vuln['severity']}]\n\n")
                        f.write(f"- **端点**: {vuln['endpoint']}\n")
                        f.write(f"- **URL**: {vuln['url']}\n")
                        f.write(f"- **描述**: {vuln['description']}\n\n")
                else:
                    f.write("## ✅ 未发现明显漏洞\n\n")

                f.write("## ✅ 可访问端点 (200 OK)\n\n")
                for r in sorted(self.results['accessible_endpoints'], key=lambda x: x['size'], reverse=True):
                    f.write(f"- [{r['status']}] {r['url']}\n")
                    f.write(f"  端点: {r['endpoint']}\n")
                    f.write(f"  大小: {r['size']} bytes\n")
                    f.write(f"  Content-Type: {r['content_type']}\n")
                    if r.get('sensitive_data'):
                        f.write(f"  ⚠️  敏感数据: {r['sensitive_data']}\n")
                    f.write("\n")

                f.write("## ⚠️  需要认证 (401/403)\n\n")
                for r in self.results['forbidden_endpoints']:
                    f.write(f"- [{r['status']}] {r['url']}\n")
                    f.write(f"  端点: {r['endpoint']}\n\n")

                f.write("## ❌ 其他状态\n\n")
                for r in self.results['error_endpoints']:
                    f.write(f"- [{r['status']}] {r['url']}\n")
                    if r.get('error'):
                        f.write(f"  错误: {r['error']}\n")
                    f.write("\n")

        print(f"[+] 报告已保存到: {output_file}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 actuator_scanner.py <url_list.txt> [output_file]")
        print("")
        print("示例:")
        print("  python3 actuator_scanner.py sites.txt")
        print("  python3 actuator_scanner.py sites.txt actuator_report.txt")
        print("")
        print("url_list.txt 格式:")
        print("  https://example.com")
        print("  https://admin.example.com")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'actuator_report.txt'

    # 读取 URL 列表
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    # 创建扫描器
    scanner = ActuatorScanner(timeout=10, max_workers=30)

    # 扫描所有站点
    print(f"[*] 开始扫描 {len(urls)} 个站点...\n")

    for url in urls:
        try:
            result = scanner.scan_site(url)
            time.sleep(2)  # 避免请求过快
        except Exception as e:
            print(f"[-] 扫描 {url} 时出错: {e}")

    # 保存报告
    print(f"\n[*] 生成报告...")
    scanner.save_report(output_file)

    # 打印统计
    vulnerabilities = scanner.check_vulnerabilities()
    print(f"\n{'='*80}")
    print("Spring Boot Actuator 扫描完成")
    print(f"{'='*80}")
    print(f"Actuator 站点: {'是' if scanner.results['actuator_detected'] else '否'}")
    print(f"可访问端点: {len(scanner.results['accessible_endpoints'])}")
    print(f"需要认证: {len(scanner.results['forbidden_endpoints'])}")
    print(f"其他: {len(scanner.results['error_endpoints'])}")
    print(f"发现漏洞: {len(vulnerabilities)}")

    if vulnerabilities:
        print(f"\n[!] 发现 {len(vulnerabilities)} 个漏洞:")
        for vuln in vulnerabilities:
            print(f"  - {vuln['type']} [{vuln['severity']}]")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
