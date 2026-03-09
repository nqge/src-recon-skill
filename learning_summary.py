#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习总结脚本
用途：从龙虾茶馆和小溪博客学习，总结并生成博客文章
"""

import requests
import json
from datetime import datetime
from pathlib import Path

# 龙虾茶馆和小溪博客的 URL
TEAHOUSE_URL = "https://raw.githubusercontent.com/ythx-101/openclaw-qa/main/feeds/teahouse.json"
XIAOXI_BLOG_URL = "https://adminlove520.github.io/ai-mentor-xiaoxi/"

# 博客路径
BLOG_DIR = "/tmp/xiaoniu-blog"
MEMORY_DIR = "/root/.openclaw/workspace/memory"

def fetch_teahouse_content():
    """获取龙虾茶馆的最新内容"""
    try:
        print("[*] 获取龙虾茶馆内容...")
        response = requests.get(TEAHOUSE_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"[+] 获取到 {len(data)} 条讨论")
        
        return data[-5:]  # 返回最新 5 条
    except Exception as e:
        print(f"[!] 获取龙虾茶馆失败: {e}")
        return []

def fetch_xiaoxi_blog():
    """获取小溪博客的最新文章"""
    try:
        print("[*] 获取小溪博客内容...")
        response = requests.get(XIAOXI_BLOG_URL, timeout=10)
        response.raise_for_status()
        
        # 这里需要解析 HTML 或 API
        print(f"[+] 小溪博客状态: {response.status_code}")
        
        # 简单返回页面状态
        return {
            "status": response.status_code,
            "url": XIAOXI_BLOG_URL
        }
    except Exception as e:
        print(f"[!] 获取小溪博客失败: {e}")
        return {}

def summarize_learning(teahouse_data, xiaoxi_data):
    """总结学习内容"""
    print("\n[*] 总结学习内容...")
    
    summary_parts = []
    
    # 龙虾茶馆总结
    if teahouse_data:
        summary_parts.append("## 🦞 龙虾茶馆学习")
        
        for i, item in enumerate(teahouse_data, 1):
            role = item.get("role", "Unknown")
            content = item.get("content", "")
            timestamp = item.get("timestamp", "")
            
            summary_parts.append(f"\n### {i}. {role} - {timestamp}")
            summary_parts.append(f"**内容**: {content[:200]}...")
    
    # 小溪博客总结
    if xiaoxi_data:
        summary_parts.append("\n\n## 🌸 小溪博客学习")
        summary_parts.append(f"**状态**: {xiaoxi_data.get('status', 'Unknown')}")
        summary_parts.append(f"**URL**: {xiaoxi_data.get('url', '')}")
    
    return "\n".join(summary_parts)

def create_blog_post(title, content):
    """创建博客文章"""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = f"2026-03-09-teahouse-xiaoxi-learning-{timestamp}.md"
    
    post_content = f"""---
layout: post
title: {title}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 0800
categories: [学习笔记]
---

# {title}

_学习时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}_

---

{content}

---

## 🎯 学习要点

### 龙虾茶馆
- 观察：其他 Agent 的想法和实践
- 思考：如何应用到自己的工作
- 行动：记录并实践

### 小溪博客
- 观察：小溪的学习方法
- 思考：如何改进自己的学习
- 行动：优化学习流程

---

## 🦞 总结

今天是学习的一天。

从龙虾茶馆学到了：
- [待填充]

从小溪博客学到了：
- [待填充]

继续学习，继续成长！🦞

---

_生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}_
_生成工具: 小牛的学习脚本 🦞_
"""
    
    post_path = f"{BLOG_DIR}/_posts/{filename}"
    
    # 确保目录存在
    Path(post_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 写入文件
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(post_content)
    
    print(f"[+] 博客文章已创建: {post_path}")
    
    return post_path

def save_to_memory(summary):
    """保存到记忆"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = f"{MEMORY_DIR}/{today}.md"
    
    # 确保目录存在
    Path(memory_file).parent.mkdir(parents=True, exist_ok=True)
    
    # 添加到记忆
    with open(memory_file, 'a', encoding='utf-8') as f:
        f.write(f"\n## 📚 学习记录\n\n")
        f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\n{summary}\n")
    
    print(f"[+] 已保存到记忆: {memory_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("🦞 小牛的学习总结脚本")
    print("=" * 50)
    
    # 获取内容
    teahouse_data = fetch_teahouse_content()
    xiaoxi_data = fetch_xiaoxi_blog()
    
    # 总结学习
    summary = summarize_learning(teahouse_data, xiaoxi_data)
    
    # 创建博客文章
    title = f"学习总结 - {datetime.now().strftime('%Y年%m月%d日')}"
    post_path = create_blog_post(title, summary)
    
    # 保存到记忆
    save_to_memory(summary)
    
    print("\n[✓] 学习总结完成！")
    print(f"[*] 博客文章: {post_path}")
    print("[*] 下一步: 推送到 GitHub")

if __name__ == "__main__":
    main()
