#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小工具：读取用户输入 → 调 Moonshot 大模型 → 保存回答为 Markdown
作者：你的姓名
用途：面试腾娱互动-游戏研究 AI 方向实习生「快速动手能力」Demo
"""

import json
import os
import time
import requests

# 1. 读环境变量/获取密钥，使用环境变量可以再不更改代码的情况下仅调整外部变量即可在不同环境运行。exit可以更早发现错误及时调整。
API_KEY = os.getenv("MOONSHOT_API_KEY")
if not API_KEY:
    print("❌ 找不到环境变量 MOONSHOT_API_KEY，程序终止！")
    print("👉 PowerShell 请先运行：$Env:MOONSHOT_API_KEY='你的钥匙'")
    exit(1)

# 2. 官方接口
BASE_URL = "https://api.moonshot.cn/v1"
MODEL    = "moonshot-v1-8k"

def call_moonshot(user_prompt: str, system_prompt: str = "你是一名游戏研究助手，回答简洁专业。") -> str:
    """调 Moonshot 大模型，返回 assistant 内容"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800,
        "top_p": 0.9
    }
    resp = requests.post(f"{BASE_URL}/chat/completions",
                         headers=headers,
                         json=payload,
                         timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def save_to_md(user: str, assistant: str, filename: str = None) -> str:
    """保存对话为 Markdown"""
    if filename is None:
        filename = time.strftime("%Y-%m-%d_%H-%M-%S") + "_chat.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 用户输入\n{user}\n\n")
        f.write(f"# 模型回答\n{assistant}\n")
    print(f"✅ 已保存对话 → {filename}")
    return filename

def main():
    print("=== 大模型自动整理小工具 ===", flush=True)
    user_text = input("请输入你的问题（一句话）：").strip()
    if not user_text:
        print("❌ 没输入内容，程序退出。")
        return

    print("正在调用大模型，请稍候...")
    assistant_text = call_moonshot(user_text)
    print("\n----- 模型回答 -----")
    print(assistant_text)
    print("--------------------\n")
    save_to_md(user_text, assistant_text)

if __name__ == "__main__":
    main()