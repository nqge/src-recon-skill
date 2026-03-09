#!/usr/bin/env python3
"""
FOFA 子域名收集工具
用于 SRC 信息收集阶段
"""

import base64
import os
import sys
import re
import json
import requests
from urllib.parse import quote

def search_fofa_subdomains(target, fofa_email=None, fofa_key=None):
    """
    使用 FOFA API 搜索子域名

    Args:
        target: 目标域名
        fofa_email: FOFA 账户邮箱（可选，默认从环境变量读取）
        fofa_key: FOFA API Key（可选，默认从环境变量读取）

    Returns:
        list: 子域名列表
    """

    # 从环境变量获取 API 凭证
    if not fofa_email:
        fofa_email = os.getenv('FOFA_EMAIL')
    if not fofa_key:
        fofa_key = os.getenv('FOFA_KEY')

    if not fofa_email or not fofa_key:
        print("[-] FOFA API 未配置")
        print("[!] 请设置环境变量：")
        print("    export FOFA_EMAIL=\"your_email@example.com\"")
        print("    export FOFA_KEY=\"your_fofa_api_key\"")
        print("[!] 或在命令行传递参数")
        return []

    # 构建 FOFA 查询语法
    query = f'domain="{target}"'
    query_base64 = base64.b64encode(query.encode()).decode()

    # FOFA API 端点
    url = f"https://fofa.info/api/v1/search/all?email={fofa_email}&key={fofa_key}&qbase64={query_base64}&size=1000"

    try:
        print(f"[*] 正在使用 FOFA 搜索: {query}")
        resp = requests.get(url, timeout=30)
        data = resp.json()

        # 检查 API 错误
        if data.get('error'):
            print(f"[-] FOFA API 错误: {data.get('errmsg', 'Unknown error')}")
            return []

        # 检查结果
        if not data.get('results'):
            print(f"[-] FOFA 未找到 {target} 的子域名")
            return []

        # 提取子域名
        subdomains = set()
        for result in data['results']:
            if isinstance(result, list) and len(result) > 0:
                host = result[0]  # host 字段
                # 提取所有域名
                domains = re.findall(r'[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', host)
                subdomains.update(domains)

        print(f"[+] FOFA 发现 {len(subdomains)} 个子域名")
        return sorted(subdomains)

    except requests.exceptions.Timeout:
        print("[-] FOFA API 请求超时")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[-] FOFA API 请求失败: {e}")
        return []
    except Exception as e:
        print(f"[-] 错误: {e}")
        return []

def save_subdomains(subdomains, output_file='fofa_subs.txt'):
    """
    保存子域名到文件

    Args:
        subdomains: 子域名列表
        output_file: 输出文件路径
    """
    try:
        with open(output_file, 'w') as f:
            for sub in subdomains:
                f.write(sub + '\n')
        print(f"[+] 结果已保存到: {output_file}")
    except Exception as e:
        print(f"[-] 保存文件失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 fofa_subs.py <目标域名> [FOFA_EMAIL] [FOFA_KEY]")
        print("")
        print("示例:")
        print("  # 使用环境变量")
        print("  export FOFA_EMAIL=\"your_email@example.com\"")
        print("  export FOFA_KEY=\"your_api_key\"")
        print("  python3 fofa_subs.py example.com")
        print("")
        print("  # 命令行传递参数")
        print("  python3 fofa_subs.py example.com your_email@example.com your_api_key")
        sys.exit(1)

    target = sys.argv[1]
    fofa_email = sys.argv[2] if len(sys.argv) > 2 else None
    fofa_key = sys.argv[3] if len(sys.argv) > 3 else None

    # 搜索子域名
    subdomains = search_fofa_subdomains(target, fofa_email, fofa_key)

    if subdomains:
        # 保存结果
        save_subdomains(subdomains)

        # 显示前 10 个结果
        print("\n[*] 前 10 个子域名:")
        for sub in subdomains[:10]:
            print(f"  - {sub}")

        if len(subdomains) > 10:
            print(f"\n... 还有 {len(subdomains) - 10} 个")
    else:
        print("[-] 未找到子域名")
        sys.exit(1)

if __name__ == '__main__':
    main()
