#!/usr/bin/env python3
"""
认证会话管理器 - 支持 Cookie、账号密码、Token 等多种认证方式

用于需要登录才能访问的页面或 API 的信息收集。
"""

import requests
import json
import sys
import os
from urllib.parse import urlparse
from http.cookies import SimpleCookie

class AuthSessionManager:
    """认证会话管理器"""

    def __init__(self):
        self.session = requests.Session()
        self.auth_method = None
        self.auth_info = {}

    def load_from_env(self):
        """从环境变量加载认证信息"""
        auth_info = {}

        # Cookie
        if os.getenv('TARGET_COOKIE'):
            auth_info['cookie'] = os.getenv('TARGET_COOKIE')

        # Token
        if os.getenv('TARGET_TOKEN'):
            auth_info['token'] = os.getenv('TARGET_TOKEN')

        # 账号密码
        if os.getenv('TARGET_USERNAME') and os.getenv('TARGET_PASSWORD'):
            auth_info['username'] = os.getenv('TARGET_USERNAME')
            auth_info['password'] = os.getenv('TARGET_PASSWORD')

        # API Key
        if os.getenv('TARGET_API_KEY'):
            auth_info['api_key'] = os.getenv('TARGET_API_KEY')

        # Bearer Token
        if os.getenv('TARGET_BEARER_TOKEN'):
            auth_info['bearer_token'] = os.getenv('TARGET_BEARER_TOKEN')

        return auth_info

    def load_from_file(self, auth_file):
        """
        从文件加载认证信息

        Args:
            auth_file: 认证信息文件（JSON 格式）

        Returns:
            dict: 认证信息
        """
        try:
            with open(auth_file, 'r') as f:
                auth_info = json.load(f)
            return auth_info
        except Exception as e:
            print(f"[-] 读取认证文件失败: {e}")
            return {}

    def load_from_interactive(self):
        """交互式输入认证信息"""
        auth_info = {}

        print("\n[*] 认证方式选择:")
        print("  1. Cookie")
        print("  2. 账号密码")
        print("  3. Token")
        print("  4. API Key")
        print("  5. Bearer Token")
        print("  6. 跳过（无认证）")

        choice = input("\n请选择认证方式 (1-6): ").strip()

        if choice == '1':
            cookie = input("请输入 Cookie: ").strip()
            if cookie:
                auth_info['cookie'] = cookie
                self.auth_method = 'cookie'

        elif choice == '2':
            username = input("请输入用户名: ").strip()
            password = input("请输入密码: ").strip()
            if username and password:
                auth_info['username'] = username
                auth_info['password'] = password
                self.auth_method = 'password'

        elif choice == '3':
            token = input("请输入 Token: ").strip()
            if token:
                auth_info['token'] = token
                self.auth_method = 'token'

        elif choice == '4':
            api_key = input("请输入 API Key: ").strip()
            if api_key:
                auth_info['api_key'] = api_key
                self.auth_method = 'api_key'

        elif choice == '5':
            bearer_token = input("请输入 Bearer Token: ").strip()
            if bearer_token:
                auth_info['bearer_token'] = bearer_token
                self.auth_method = 'bearer_token'

        else:
            print("[*] 跳过认证")
            self.auth_method = None

        return auth_info

    def apply_auth(self, auth_info):
        """
        应用认证信息到会话

        Args:
            auth_info: 认证信息字典
        """
        self.auth_info = auth_info

        # Cookie
        if 'cookie' in auth_info:
            cookie_str = auth_info['cookie']
            cookie = SimpleCookie()
            cookie.load(cookie_str)

            for key, morsel in cookie.items():
                self.session.cookies.set(key, morsel.value)

            self.auth_method = 'cookie'
            print(f"[+] 使用 Cookie 认证")

        # Token（作为查询参数或请求头）
        elif 'token' in auth_info:
            token = auth_info['token']
            self.session.headers.update({
                'Authorization': f'Token {token}'
            })
            self.auth_method = 'token'
            print(f"[+] 使用 Token 认证")

        # 账号密码（Basic Auth 或登录）
        elif 'username' in auth_info and 'password' in auth_info:
            # 存储用户名和密码，稍后可能需要登录
            self.auth_method = 'password'
            print(f"[+] 使用账号密码认证（用户名: {auth_info['username']}）")

        # API Key
        elif 'api_key' in auth_info:
            api_key = auth_info['api_key']
            self.session.headers.update({
                'X-API-Key': api_key
            })
            self.auth_method = 'api_key'
            print(f"[+] 使用 API Key 认证")

        # Bearer Token
        elif 'bearer_token' in auth_info:
            bearer_token = auth_info['bearer_token']
            self.session.headers.update({
                'Authorization': f'Bearer {bearer_token}'
            })
            self.auth_method = 'bearer_token'
            print(f"[+] 使用 Bearer Token 认证")

    def login(self, login_url):
        """
        使用账号密码登录

        Args:
            login_url: 登录接口 URL

        Returns:
            bool: 登录是否成功
        """
        if self.auth_method != 'password':
            print("[-] 当前认证方式不是账号密码")
            return False

        username = self.auth_info.get('username')
        password = self.auth_info.get('password')

        if not username or not password:
            print("[-] 缺少用户名或密码")
            return False

        print(f"[*] 正在登录到: {login_url}")

        try:
            # 尝试常见的登录格式
            login_data = {
                'username': username,
                'password': password,
                'email': username,  # 有些站点使用 email
            }

            response = self.session.post(
                login_url,
                data=login_data,
                timeout=10,
                verify=False
            )

            if response.status_code == 200:
                print(f"[+] 登录成功")
                return True
            else:
                print(f"[-] 登录失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[-] 登录错误: {e}")
            return False

    def test_auth(self, test_url):
        """
        测试认证是否有效

        Args:
            test_url: 测试 URL

        Returns:
            bool: 认证是否有效
        """
        if not self.auth_method:
            print("[*] 无认证，测试匿名访问")
        else:
            print(f"[*] 测试认证（方式: {self.auth_method}）")

        try:
            response = self.session.get(
                test_url,
                timeout=10,
                verify=False,
                allow_redirects=True
            )

            print(f"[*] 响应状态码: {response.status_code}")

            if response.status_code == 200:
                print(f"[+] 认证有效，可以访问")
                return True
            elif response.status_code in [401, 403]:
                print(f"[-] 认证失败或权限不足")
                return False
            else:
                print(f"[?] 状态码: {response.status_code}")
                return response.status_code == 200

        except Exception as e:
            print(f"[-] 测试错误: {e}")
            return False

    def save_session(self, output_file='auth_session.json'):
        """
        保存会话信息

        Args:
            output_file: 输出文件
        """
        session_info = {
            'auth_method': self.auth_method,
            'cookies': dict(self.session.cookies),
            'headers': dict(self.session.headers)
        }

        with open(output_file, 'w') as f:
            json.dump(session_info, f, indent=2)

        print(f"[+] 会话信息已保存到: {output_file}")

    def get_session(self):
        """
        获取配置好的会话

        Returns:
            requests.Session: 配置好的会话对象
        """
        return self.session

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 auth_session_manager.py <test_url> [auth_file]")
        print("")
        print("认证方式:")
        print("  1. 从文件加载: python3 auth_session_manager.py https://example.com auth.json")
        print("  2. 从环境变量: TARGET_COOKIE=xxx ...")
        print("  3. 交互式输入: python3 auth_session_manager.py https://example.com")
        print("")
        print("环境变量:")
        print("  TARGET_COOKIE - Cookie 字符串")
        print("  TARGET_TOKEN - Token")
        print("  TARGET_USERNAME - 用户名")
        print("  TARGET_PASSWORD - 密码")
        print("  TARGET_API_KEY - API Key")
        print("  TARGET_BEARER_TOKEN - Bearer Token")
        print("")
        print("认证文件格式 (JSON):")
        print("""
{
  "cookie": "sessionid=xxx; csrftoken=yyy",
  "token": "your_token",
  "username": "user",
  "password": "pass",
  "api_key": "your_api_key",
  "bearer_token": "your_bearer_token"
}
        """)
        sys.exit(1)

    test_url = sys.argv[1]
    auth_file = sys.argv[2] if len(sys.argv) > 2 else None

    # 创建会话管理器
    manager = AuthSessionManager()

    # 加载认证信息
    if auth_file:
        print(f"[*] 从文件加载认证信息: {auth_file}")
        auth_info = manager.load_from_file(auth_file)
    elif os.getenv('TARGET_COOKIE') or os.getenv('TARGET_TOKEN'):
        print("[*] 从环境变量加载认证信息")
        auth_info = manager.load_from_env()
    else:
        auth_info = manager.load_from_interactive()

    if not auth_info:
        print("[-] 无认证信息，使用匿名访问")
    else:
        # 应用认证
        manager.apply_auth(auth_info)

    # 如果需要登录
    if manager.auth_method == 'password':
        login_url = input("\n请输入登录接口 URL (例如: https://example.com/api/login): ").strip()
        if login_url:
            manager.login(login_url)

    # 测试认证
    print(f"\n[*] 测试访问: {test_url}")
    success = manager.test_auth(test_url)

    # 保存会话
    if success:
        manager.save_session()
        print("\n[+] 认证会话已保存，可以用于后续扫描")
    else:
        print("\n[-] 认证失败，请检查认证信息")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
