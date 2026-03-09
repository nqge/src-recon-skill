#!/usr/bin/env python3
"""
OneForAll 子域名收集工具 - 基于 OneForAll 的增强版子域名枚举

支持：
1. 常规子域名收集（无 API Key）
2. 搜索引擎发现（需要 API Key）
3. 证书透明度查询
4. 威胁情报平台
"""

import subprocess
import sys
import os
import re
from pathlib import Path

class OneForAllCollector:
    """OneForAll 子域名收集器"""

    def __init__(self):
        self.results = {
            'subdomains': set(),
            'sources': {}
        }

    def check_installation(self):
        """检查 OneForAll 是否安装"""
        try:
            result = subprocess.run(
                ['python3', 'oneforall.py', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return True
        except:
            return False

    def collect_without_api(self, target):
        """
        无 API Key 的常规收集

        Args:
            target: 目标域名

        Returns:
            list: 收集的子域名列表
        """
        print(f"[*] 使用 OneForAll 进行常规子域名收集（无需 API）")
        print(f"    目标: {target}")

        # 使用 OneForAll 的基础模块
        cmd = [
            'python3',
            'oneforall.py',
            '--target', target,
            '--run',
            '--disable_modules', ['search_engine', 'threat_intelligence']
        ]

        try:
            print("    [*] 正在运行 OneForAll...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 分钟超时
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            if result.returncode == 0:
                print("    [+] OneForAll 运行成功")

                # 读取结果文件
                output_file = Path(f"results/{target}_subdomains.txt")
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        subdomains = [line.strip() for line in f if line.strip()]
                    
                    self.results['subdomains'].update(subdomains)
                    self.results['sources']['oneforall'] = len(subdomains)
                    
                    print(f"    [+] OneForAll 发现 {len(subdomains)} 个子域名")
                    return subdomains
                else:
                    print(f"    [-] 未找到结果文件: {output_file}")
                    return []
            else:
                print(f"    [-] OneForAll 运行失败")
                print(f"    错误: {result.stderr}")
                return []

        except subprocess.TimeoutExpired:
            print(f"    [-] OneForAll 运行超时")
            return []
        except Exception as e:
            print(f"    [-] 错误: {e}")
            return []

    def collect_with_api(self, target, api_config=None):
        """
        使用搜索引擎 API 收集（需要 API Key）

        Args:
            target: 目标域名
            api_config: API 配置字典

        Returns:
            list: 收集的子域名列表
        """
        print(f"[*] 使用搜索引擎 API 收集子域名")
        print(f"    目标: {target}")

        if not api_config:
            print("    [-] 未提供 API 配置")
            return []

        # 检查可用的 API
        available_apis = []
        if api_config.get('shodan_api_key'):
            available_apis.append('shodan')
        if api_config.get('censat_api_key'):
            available_apis.append('censat')
        if api_config.get('fofa_email') and api_config.get('fofa_key'):
            available_apis.append('fofa')
        if api_config.get('quake_api_key'):
            available_apis.append('quake')

        if not available_apis:
            print("    [-] 没有可用的搜索引擎 API")
            return []

        print(f"    [*] 可用的搜索引擎: {', '.join(available_apis)}")

        # 使用 OneForAll 的搜索引擎模块
        cmd = [
            'python3',
            'oneforall.py',
            '--target', target,
            '--run',
            '--enable_modules', ['search_engine']
        ]

        # 设置环境变量传递 API 配置
        env = os.environ.copy()
        if api_config.get('shodan_api_key'):
            env['SHODAN_API_KEY'] = api_config['shodan_api_key']
        if api_config.get('censat_api_key'):
            env['CENSAT_API_KEY'] = api_config['censat_api_key']
        if api_config.get('fofa_email'):
            env['FOFA_EMAIL'] = api_config['fofa_email']
        if api_config.get('fofa_key'):
            env['FOFA_KEY'] = api_config['fofa_key']
        if api_config.get('quake_api_key'):
            env['QUAKE_API_KEY'] = api_config['quake_api_key']

        try:
            print("    [*] 正在运行 OneForAll 搜索引擎模块...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                env=env,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            if result.returncode == 0:
                # 读取结果
                output_file = Path(f"results/{target}_subdomains.txt")
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        subdomains = [line.strip() for line in f if line.strip()]
                    
                    self.results['subdomains'].update(subdomains)
                    self.results['sources']['search_engines'] = len(subdomains)
                    
                    print(f"    [+] 搜索引擎发现 {len(subdomains)} 个子域名")
                    return subdomains
                else:
                    return []
            else:
                print(f"    [-] 搜索引擎模块运行失败")
                return []

        except Exception as e:
            print(f"    [-] 错误: {e}")
            return []

    def collect_certificates(self, target):
        """
        证书透明度查询

        Args:
            target: 目标域名

        Returns:
            list: 收集的子域名列表
        """
        print(f"[*] 证书透明度查询")
        print(f"    目标: {target}")

        # OneForAll 的证书透明度模块
        cmd = [
            'python3',
            'oneforall.py',
            '--target', target,
            '--run',
            '--enable_modules', ['certificate']
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            if result.returncode == 0:
                output_file = Path(f"results/{target}_subdomains.txt")
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        subdomains = [line.strip() for line in f if line.strip()]
                    
                    self.results['subdomains'].update(subdomains)
                    self.results['sources']['certificates'] = len(subdomains)
                    
                    print(f"    [+] 证书透明度发现 {len(subdomains)} 个子域名")
                    return subdomains
            return []

        except Exception as e:
            print(f"    [-] 证书透明度查询失败: {e}")
            return []

    def save_results(self, output_file='oneforall_subs.txt'):
        """保存结果"""
        with open(output_file, 'w') as f:
            for sub in sorted(self.results['subdomains']):
                f.write(sub + '\n')
        
        print(f"[+] 结果已保存到: {output_file}")
        print(f"[+] 总共发现 {len(self.results['subdomains'])} 个子域名")
        
        # 统计来源
        if self.results['sources']:
            print("\n[*] 来源统计:")
            for source, count in self.results['sources'].items():
                print(f"    - {source}: {count} 个")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 oneforall_subs.py <target> [output_file] [--api]")
        print("")
        print("示例:")
        print("  # 常规收集（无需 API）")
        print("  python3 oneforall_subs.py example.com")
        print("")
        print("  # 使用搜索引擎 API")
        print("  python3 oneforall_subs.py example.com --api")
        print("")
        print("环境变量（API 配置）:")
        print("  SHODAN_API_KEY=xxx")
        print("  CENSAT_API_KEY=xxx")
        print("  FOFA_EMAIL=xxx")
        print("  FOFA_KEY=xxx")
        print("  QUAKE_API_KEY=xxx")
        sys.exit(1)

    target = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'oneforall_subs.txt'
    use_api = '--api' in sys.argv

    # 检查 OneForAll 安装
    collector = OneForAllCollector()
    if not collector.check_installation():
        print("[-] OneForAll 未安装")
        print("")
        print("安装方法:")
        print("  git clone https://github.com/shmilylty/OneForAll.git")
        print("  cd OneForAll")
        print("  pip3 install -r requirements.txt")
        sys.exit(1)

    print(f"[*] OneForAll 子域名收集")
    print(f"[*] 目标: {target}")
    print(f"[*] 使用 API: {'是' if use_api else '否'}")
    print(f"[*] 输出文件: {output_file}")
    print("")

    # 收集子域名
    if use_api:
        # 使用搜索引擎 API
        api_config = {
            'shodan_api_key': os.getenv('SHODAN_API_KEY'),
            'censat_api_key': os.getenv('CENSAT_API_KEY'),
            'fofa_email': os.getenv('FOFA_EMAIL'),
            'fofa_key': os.getenv('FOFA_KEY'),
            'quake_api_key': os.getenv('QUAKE_API_KEY')
        }
        collector.collect_with_api(target, api_config)
    else:
        # 常规收集
        collector.collect_without_api(target)

    # 证书透明度查询（始终执行）
    collector.collect_certificates(target)

    # 保存结果
    collector.save_results(output_file)

    print(f"\n{'='*80}")
    print("OneForAll 子域名收集完成")
    print(f"{'='*80}")
    print(f"总计: {len(collector.results['subdomains'])} 个子域名")

if __name__ == '__main__':
    main()
