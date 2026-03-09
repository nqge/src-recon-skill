#!/usr/bin/env python3
"""
浏览器 HTTP/HTTPS 访问测试工具
使用 Selenium + Chrome/Chromium 浏览器进行访问测试
特别适用于：
1. Legacy SSL Renegotiation 问题
2. 需要 JavaScript 渲染的页面
3. 复杂的客户端证书验证
4. 需要模拟浏览器行为的场景
"""

import json
import time
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class BrowserAccessTester:
    """浏览器访问测试器"""

    def __init__(self, headless=True, timeout=30, max_workers=3):
        self.headless = headless
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []

    def create_driver(self):
        """
        创建 Chrome WebDriver

        Returns:
            WebDriver: Chrome WebDriver 实例
        """
        chrome_options = Options()

        # 无头模式
        if self.headless:
            chrome_options.add_argument('--headless=new')

        # SSL 相关选项
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-ssl-fetch')
        
        # 其他选项
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # 禁用日志
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            driver.set_script_timeout(self.timeout)
            return driver
        except Exception as e:
            print(f"[-] 创建 WebDriver 失败: {e}")
            return None

    def test_url(self, url):
        """
        使用浏览器测试单个 URL

        Args:
            url: 目标 URL

        Returns:
            dict: 测试结果
        """
        result = {
            'url': url,
            'accessible': False,
            'status_code': None,
            'title': None,
            'error': None,
            'load_time': None,
            'screenshot': None,
            'cookies': [],
            'forms': [],
            'links': []
        }

        driver = None
        try:
            start_time = time.time()

            # 创建 WebDriver
            driver = self.create_driver()
            if not driver:
                result['error'] = "无法创建 WebDriver"
                return result

            # 访问 URL
            driver.get(url)

            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 获取页面信息
            result['accessible'] = True
            result['title'] = driver.title
            result['load_time'] = round(time.time() - start_time, 2)

            # 尝试获取状态码（从 JavaScript）
            try:
                performance = driver.get_log('performance')
                for entry in performance:
                    message = json.loads(entry['message'])
                    if message['message']['method'] == 'Network.responseReceived':
                        result['status_code'] = message['message']['params']['response'].get('status')
                        break
            except:
                pass

            # 获取 Cookies
            try:
                cookies = driver.get_cookies()
                result['cookies'] = [cookie['name'] for cookie in cookies]
            except:
                pass

            # 获取表单
            try:
                forms = driver.find_elements(By.TAG_NAME, 'form')
                result['forms'] = [
                    form.get_attribute('action') or 'current_url' 
                    for form in forms
                ]
            except:
                pass

            # 获取链接（前 10 个）
            try:
                links = driver.find_elements(By.TAG_NAME, 'a')
                result['links'] = [
                    link.get_attribute('href') 
                    for link in links[:10] 
                    if link.get_attribute('href')
                ]
            except:
                pass

            # 截图
            try:
                screenshot_path = f"/tmp/screenshot_{url.replace('https://', '').replace('http://', '').replace('/', '_')}.png"
                driver.save_screenshot(screenshot_path)
                result['screenshot'] = screenshot_path
            except:
                pass

        except TimeoutException:
            result['error'] = "页面加载超时"
        except WebDriverException as e:
            result['error'] = f"WebDriver 错误: {str(e)}"
        except Exception as e:
            result['error'] = f"未知错误: {str(e)}"
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        return result

    def test_urls(self, urls):
        """
        批量测试 URL

        Args:
            urls: URL 列表

        Returns:
            list: 测试结果列表
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.test_url, url): url 
                for url in urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 实时输出
                    if result['accessible']:
                        print(f"[✅] {url} - 可访问")
                        if result['title']:
                            print(f"    标题: {result['title']}")
                    else:
                        print(f"[-] {url} - 不可访问")
                        if result['error']:
                            print(f"    错误: {result['error']}")
                except Exception as e:
                    print(f"[-] {url} - 测试失败: {e}")
                    results.append({
                        'url': url,
                        'accessible': False,
                        'error': str(e)
                    })

        return results

    def generate_report(self, results, output_file):
        """
        生成测试报告

        Args:
            results: 测试结果列表
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 浏览器访问测试报告\n\n")
            f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试**: {len(results)} 个 URL\n\n")

            # 统计
            accessible = sum(1 for r in results if r.get('accessible', False))
            f.write("## 📊 统计\n\n")
            f.write(f"- 可访问: {accessible} 个\n")
            f.write(f"- 不可访问: {len(results) - accessible} 个\n\n")

            # 可访问的 URL
            f.write("## ✅ 可访问的 URL\n\n")
            for result in results:
                if result.get('accessible', False):
                    f.write(f"### {result['url']}\n\n")
                    
                    if result.get('status_code'):
                        f.write(f"**状态码**: {result['status_code']}\n\n")
                    
                    if result.get('title'):
                        f.write(f"**标题**: {result['title']}\n\n")
                    
                    if result.get('load_time'):
                        f.write(f"**加载时间**: {result['load_time']} 秒\n\n")
                    
                    if result.get('cookies'):
                        f.write(f"**Cookies**: {', '.join(result['cookies'][:5])}\n\n")
                    
                    if result.get('forms'):
                        f.write(f"**表单**: {len(result['forms'])} 个\n\n")
                    
                    if result.get('screenshot'):
                        f.write(f"**截图**: {result['screenshot']}\n\n")
                    
                    f.write("---\n\n")

            # 不可访问的 URL
            f.write("## ❌ 不可访问的 URL\n\n")
            for result in results:
                if not result.get('accessible', False):
                    f.write(f"### {result['url']}\n\n")
                    
                    if result.get('error'):
                        f.write(f"**错误**: {result['error']}\n\n")
                    
                    f.write("---\n\n")

            f.write("\n---\n\n")
            f.write("**生成工具**: 浏览器访问测试工具 🦞\n")

def main():
    if len(sys.argv) < 3:
        print("使用方法: python3 browser_access_tester.py <input_file> <output_file>")
        print("")
        print("参数:")
        print("  input_file  - 包含 URL 列表的文件")
        print("  output_file - 输出报告文件路径")
        print("")
        print("环境变量:")
        print("  HEADLESS=false - 显示浏览器窗口（默认：true）")
        print("  TIMEOUT=30    - 页面加载超时时间（秒）")
        print("")
        print("示例:")
        print("  python3 browser_access_tester.py urls.txt report.md")
        print("  HEADLESS=false python3 browser_access_tester.py urls.txt report.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # 环境变量
    headless = os.getenv('HEADLESS', 'true').lower() == 'true'
    timeout = int(os.getenv('TIMEOUT', '30'))

    # 读取 URL
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        sys.exit(1)

    if not urls:
        print("[-] 没有找到 URL")
        sys.exit(1)

    print(f"[*] 浏览器访问测试工具")
    print(f"[*] 测试 {len(urls)} 个 URL")
    print(f"[*] 无头模式: {headless}")
    print(f"[*] 超时时间: {timeout} 秒")
    print(f"[*] 开始测试...\n")

    # 测试
    tester = BrowserAccessTester(headless=headless, timeout=timeout)
    results = tester.test_urls(urls)

    # 生成报告
    tester.generate_report(results, output_file)

    # 统计
    accessible = sum(1 for r in results if r.get('accessible', False))

    print(f"\n[*] 测试完成")
    print(f"[+] 可访问: {accessible} 个")
    print(f"[+] 不可访问: {len(results) - accessible} 个")
    print(f"[+] 报告已保存到: {output_file}")

if __name__ == "__main__":
    main()
