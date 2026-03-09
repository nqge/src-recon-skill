#!/usr/bin/env python3
"""
简单的子域名收集工具
支持多种子域名收集方法
"""

import requests
import dns.resolver
import sys
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class SubdomainCollector:
    """子域名收集器"""

    def __init__(self):
        self.subdomains = set()

    def collect_from_certspotter(self, domain):
        """从 Certificate Transparency 日志收集"""
        url = f"https://crt.sh/?q=%.25.{domain}&output=json"
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            
            for entry in data:
                name_value = entry.get('name_value', '')
                for subdomain in name_value.split('\n'):
                    if subdomain and domain in subdomain:
                        self.subdomains.add(subdomain)
        except Exception as e:
            print(f"[-] Cert Spotter 收集失败: {e}")

    def collect_from_dnsdumpster(self, domain):
        """从 DNSdumpster 收集"""
        url = f"https://dnsdumpster.com/{domain}"
        try:
            response = requests.get(url, timeout=30)
            
            # 提取子域名
            pattern = rf'([a-zA-Z0-9-]+\.{re.escape(domain)})'
            matches = re.findall(pattern, response.text)
            
            for match in matches:
                if match != domain:
                    self.subdomains.add(match)
        except Exception as e:
            print(f"[-] DNSdumpster 收集失败: {e}")

    def collect_from_virustotal(self, domain):
        """从 VirusTotal 收集（需要 API key）"""
        # 简化版本，不需要 API key
        print("[*] VirusTotal 收集（需要 API key，跳过）")

    def brute_force_subdomains(self, domain, wordlist):
        """字典爆破子域名"""
        print(f"[*] 字典爆破 ({len(wordlist)} 个词)")
        
        def test_subdomain(word):
            subdomain = f"{word}.{domain}"
            try:
                # 测试 DNS 解析
                dns.resolver.resolve(subdomain, 'A')
                return subdomain
            except:
                return None

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(test_subdomain, word): word for word in wordlist}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.subdomains.add(result)
                    print(f"[+] {result}")

    def collect(self, domain, wordlist=None):
        """
        收集子域名

        Args:
            domain: 目标域名
            wordlist: 字典列表（用于爆破）
        """
        print(f"[*] 开始收集子域名: {domain}")
        print(f"[*] 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 方法 1: Certificate Transparency
        print("[*] 方法 1: Certificate Transparency")
        self.collect_from_certspotter(domain)
        print(f"[+] 当前: {len(self.subdomains)} 个子域名")
        print()

        # 方法 2: DNSdumpster
        print("[*] 方法 2: DNSdumpster")
        self.collect_from_dnsdumpster(domain)
        print(f"[+] 当前: {len(self.subdomains)} 个子域名")
        print()

        # 方法 3: 字典爆破
        if wordlist:
            print("[*] 方法 3: 字典爆破")
            self.brute_force_subdomains(domain, wordlist)
            print(f"[+] 最终: {len(self.subdomains)} 个子域名")
            print()

        return list(self.subdomains)

def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 simple_subfinder.py <domain> [wordlist_file]")
        print("")
        print("参数:")
        print("  domain - 目标域名")
        print("  wordlist_file - 字典文件（可选）")
        print("")
        print("示例:")
        print("  python3 simple_subfinder.py example.com")
        print("  python3 simple_subfinder.py example.com subdomains.txt")
        sys.exit(1)

    domain = sys.argv[1]
    wordlist = None

    # 读取字典
    if len(sys.argv) >= 3:
        try:
            with open(sys.argv[2], 'r') as f:
                wordlist = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"[-] 读取字典失败: {e}")
            sys.exit(1)

    # 收集
    collector = SubdomainCollector()
    subdomains = collector.collect(domain, wordlist)

    # 输出
    print()
    print(f"[*] 收集完成")
    print(f"[+] 总数: {len(subdomains)} 个子域名")
    print()

    for subdomain in sorted(subdomains):
        print(subdomain)

if __name__ == "__main__":
    main()
