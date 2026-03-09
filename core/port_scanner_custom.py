#!/usr/bin/env python3
"""
魔改版端口扫描器 - 参考 fscan 原理
特征去除：随机 User-Agent、随机延迟、自定义指纹
"""

import socket
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Set
import json
from pathlib import Path
from datetime import datetime

# 随机 User-Agent 池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

# 随机延迟范围（毫秒）
MIN_DELAY = 50
MAX_DELAY = 200

class PortScanner:
    """魔改版端口扫描器"""
    
    def __init__(self, max_threads=100, timeout=3):
        self.max_threads = max_threads
        self.timeout = timeout
        self.results = {}
        self.lock = threading.Lock()
        
    def scan_port(self, ip: str, port: int, delay: bool = True) -> Tuple[str, int, str]:
        """
        扫描单个端口
        
        Args:
            ip: 目标 IP
            port: 目标端口
            delay: 是否添加随机延迟
            
        Returns:
            (ip, port, status) - status: 'open' | 'closed' | 'filtered'
        """
        # 随机延迟（避免特征识别）
        if delay:
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY) / 1000.0)
        
        try:
            # 创建 socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # 尝试连接
            result = sock.connect_ex((ip, port))
            
            if result == 0:
                status = 'open'
                
                # 尝试获取服务指纹（魔改版）
                try:
                    # 发送随机 HTTP 请求（避免特征）
                    if port in [80, 443, 8080, 8443, 3000, 5000, 8888, 9000, 9443]:
                        request = self._generate_random_http_request()
                        sock.send(request.encode())
                        
                        # 接收响应
                        response = sock.recv(1024).decode('utf-8', errors='ignore')
                        
                        # 提取 Server 头（如果存在）
                        server = self._extract_server_header(response)
                    else:
                        server = 'unknown'
                except:
                    server = 'unknown'
                
                sock.close()
                return (ip, port, 'open', server)
            else:
                sock.close()
                return (ip, port, 'closed', '')
                
        except socket.timeout:
            return (ip, port, 'filtered', '')
        except Exception as e:
            return (ip, port, 'error', '')
    
    def _generate_random_http_request(self) -> str:
        """
        生成随机 HTTP 请求（避免特征识别）
        """
        # 随机选择 HTTP 方法
        methods = ['GET', 'HEAD', 'OPTIONS']
        method = random.choice(methods)
        
        # 随机 User-Agent
        user_agent = random.choice(USER_AGENTS)
        
        # 随机其他头
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 构建请求
        request = f"{method} / HTTP/1.1\r\n"
        request += f"Host: {{host}}\r\n"
        request += f"User-Agent: {user_agent}\r\n"
        
        # 随机添加其他头
        for key, value in headers.items():
            if random.random() > 0.3:  # 70% 概率添加
                request += f"{key}: {value}\r\n"
        
        request += "\r\n"
        
        return request
    
    def _extract_server_header(self, response: str) -> str:
        """
        提取 Server 头（服务指纹）
        """
        lines = response.split('\r\n')
        for line in lines:
            if line.lower().startswith('server:'):
                return line.split(':', 1)[1].strip()
        return 'unknown'
    
    def scan_ip(self, ip: str, ports: List[int]) -> Dict[int, str]:
        """
        扫描单个 IP 的多个端口
        
        Args:
            ip: 目标 IP
            ports: 端口列表
            
        Returns:
            {port: status} 字典
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # 提交扫描任务
            futures = {
                executor.submit(self.scan_port, ip, port): port 
                for port in ports
            }
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    result_ip, port, status, server = future.result()
                    
                    if status == 'open':
                        results[port] = server
                        
                        # 线程安全地记录
                        with self.lock:
                            if ip not in self.results:
                                self.results[ip] = {}
                            self.results[ip][port] = server
                            
                except Exception as e:
                    pass
        
        return results
    
    def scan_ips(self, ips: List[str], ports: List[int]) -> Dict[str, Dict[int, str]]:
        """
        扫描多个 IP 的多个端口
        
        Args:
            ips: IP 列表
            ports: 端口列表
            
        Returns:
            {ip: {port: server}} 字典
        """
        print(f"[*] 开始扫描 {len(ips)} 个 IP 的 {len(ports)} 个端口")
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # 提交扫描任务
            futures = {
                executor.submit(self.scan_ip, ip, ports): ip 
                for ip in ips
            }
            
            # 收集结果
            completed = 0
            for future in as_completed(futures):
                try:
                    ip = futures[future]
                    results = future.result()
                    
                    completed += 1
                    print(f"[*] 进度: {completed}/{len(ips)} - {ip} ({len(results)} 个开放端口)")
                    
                except Exception as e:
                    pass
        
        return self.results
    
    def save_results(self, output_file: str, format: str = 'gnmap'):
        """
        保存扫描结果
        
        Args:
            output_file: 输出文件路径
            format: 输出格式 ('gnmap' | 'json' | 'txt')
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'gnmap':
            self._save_gnmap(output_path)
        elif format == 'json':
            self._save_json(output_path)
        elif format == 'txt':
            self._save_txt(output_path)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _save_gnmap(self, output_path: Path):
        """保存为 GNMAP 格式（兼容 nmap）"""
        with open(output_path, 'w') as f:
            for ip, ports in self.results.items():
                open_ports = []
                for port, server in ports.items():
                    open_ports.append(f"{port}/open/tcp//{server}//")
                
                if open_ports:
                    line = f"Host: {ip} ()\tPorts: {','.join(open_ports)}"
                    f.write(line + '\n')
    
    def _save_json(self, output_path: Path):
        """保存为 JSON 格式"""
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def _save_txt(self, output_path: Path):
        """保存为 TXT 格式"""
        with open(output_path, 'w') as f:
            for ip, ports in self.results.items():
                for port, server in ports.items():
                    f.write(f"{ip}:{port} - {server}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='魔改版端口扫描器')
    parser.add_argument('targets', help='目标 IP 文件（每行一个 IP）')
    parser.add_argument('-p', '--ports', default='1-1000', help='端口范围（默认: 1-1000）')
    parser.add_argument('-o', '--output', default='port_scan.txt', help='输出文件')
    parser.add_argument('-f', '--format', default='gnmap', choices=['gnmap', 'json', 'txt'], help='输出格式')
    parser.add_argument('-t', '--threads', type=int, default=100, help='线程数（默认: 100）')
    parser.add_argument('--timeout', type=int, default=3, help='超时时间（默认: 3秒）')
    parser.add_argument('--no-delay', action='store_true', help='禁用随机延迟')
    
    args = parser.parse_args()
    
    # 读取目标 IP
    with open(args.targets, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
    
    # 解析端口范围
    ports = []
    if '-' in args.ports:
        start, end = map(int, args.ports.split('-'))
        ports = list(range(start, end + 1))
    elif ',' in args.ports:
        ports = [int(p) for p in args.ports.split(',')]
    else:
        ports = [int(args.ports)]
    
    print(f"[*] 目标数量: {len(ips)}")
    print(f"[*] 端口数量: {len(ports)}")
    print(f"[*] 线程数: {args.threads}")
    print(f"[*] 超时时间: {args.timeout}秒")
    print(f"[*] 输出格式: {args.format}")
    print(f"[*] 随机延迟: {'否' if args.no_delay else '是'}")
    print()
    
    # 创建扫描器
    scanner = PortScanner(max_threads=args.threads, timeout=args.timeout)
    
    # 开始扫描
    start_time = time.time()
    results = scanner.scan_ips(ips, ports)
    elapsed_time = time.time() - start_time
    
    # 统计结果
    total_open = sum(len(ports) for ports in results.values())
    
    print()
    print(f"[*] 扫描完成！")
    print(f"[*] 总耗时: {elapsed_time:.2f}秒")
    print(f"[*] 发现开放端口: {total_open} 个")
    
    # 保存结果
    scanner.save_results(args.output, format=args.format)
    print(f"[*] 结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
