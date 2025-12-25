#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具名称：游戏研究 AI 分析辅助工具
作者：ZYW
用途：
    面向「游戏研究与 AI 应用方向」的实践 Demo，
    使用大模型对游戏机制 / 玩法 / 文本进行结构化分析，
    辅助研究讨论与设计优化。
"""

import os #用于读取环境变量
import time #用于生成文件名时间戳
import requests #用于发送HTTP请求调用API


# =========================
# 一、基础配置
# =========================

# 1. 从环境变量中读取 API Key（安全做法），需在系统中预先设置
API_KEY = os.getenv("MOONSHOT_API_KEY")
if not API_KEY:
    print("❌ 未找到环境变量 MOONSHOT_API_KEY")
    print("👉 请先在系统中设置 API Key 后再运行程序")
    exit(1)

# 2. Moonshot API 基础信息
BASE_URL = "https://api.moonshot.cn/v1"
MODEL = "moonshot-v1-8k"


# =========================
# 二、系统 Prompt（核心能力）
# =========================

#系统 Prompt 就是告诉 AI：“你是谁，你要做什么，你要输出什么格式”。定义系统提示，指导模型生成符合要求的内容。
SYSTEM_PROMPT = """
你是一名【游戏研究与 AI 应用分析助手】，服务对象是游戏研发与运营团队。

你的任务是：对用户提供的【游戏机制描述 / 玩法设计 / 剧情文本】进行分析，
并输出可用于【研究讨论、设计决策与优化参考】的结构化内容。

请严格按照以下结构输出：

【一、核心玩法与机制理解】
- 概括该设计的核心循环与关键机制
- 指出玩家主要行为路径

【二、玩家体验分析】
- 新手理解成本
- 中后期可玩性与重复体验
- 可能出现的爽点或挫败点

【三、留存与商业化潜力（定性）】
- 对新手留存的潜在影响
- 对长期留存的潜在影响
- 是否存在自然的商业化切入点（不涉及数值）

【四、风险点与设计隐患】
- 可能导致玩家流失的问题
- 实现或维护成本风险

【五、改进建议（可执行）】
- 提供 1～3 条具体、可落地的优化建议
- 每条建议需说明改进目标

输出要求：
- 使用专业、简洁的游戏研发语言
- 使用要点列出，避免长段落
- 不虚构数据，不做最终结论判断
- 本分析仅作为研究与设计参考
"""


# =========================
# 三、调用大模型的函数
# =========================

def call_moonshot(user_prompt: str) -> str: #定义函数和参数类型
    """
    调用 Moonshot 大模型接口
    参数：
        user_prompt：用户输入的游戏设计或文本
    返回：
        模型生成的分析文本
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"  #告诉服务端发送的是 JSON 格式数据
    }

    payload = {
        "model": MODEL, #使用的模型名称
        "messages": [   #系统角色信息和用户录入
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7, #控制生成文本的创造性
        "max_tokens": 900   #限制生成文本的最大长度
    }

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30  #最多等待30s，如果没有返回就报错
    )

    # 如果 HTTP 状态码不是 200，会直接报错
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


# =========================
# 四、保存分析结果为 Markdown
# =========================

def save_to_markdown(user_input: str, analysis_result: str) -> str:
    """
    将分析结果保存为 Markdown 文件方便后续展示与归档
    """

    filename = time.strftime("%Y-%m-%d_%H-%M-%S") + "_game_analysis.md" #设置时间戳作为文件名

    with open(filename, "w", encoding="utf-8") as f:    #以写入模式打开文件
        f.write("# 游戏研究分析记录\n\n")   ##是一级标题
        f.write("## 研究对象\n")    #两个#是二级标题
        f.write(user_input + "\n\n")
        f.write("## AI 分析结果\n")
        f.write(analysis_result + "\n\n")
        f.write("> 注：本分析由大模型生成，仅作为研究与设计参考。\n")  #>是引用格式

    return filename    #返回文件名，方便调用处打印


# =========================
# 五、程序入口
# =========================

def main():
    print("🎮 游戏研究 AI 分析辅助工具")
    print("-" * 30)

    user_text = input("请输入游戏机制 / 玩法 / 剧情描述：\n").strip() #获取用户输入并去除首尾空白

    if not user_text:
        print("❌ 未输入内容，程序结束")
        return

    print("\n⏳ 正在进行 AI 分析，请稍候...\n")

    try:    #用 try/except 捕获可能的错误（比如 API Key 错误、网络错误）
        result = call_moonshot(user_text)
    except Exception as e:
        print("❌ 调用模型失败：", e)
        return

    print("===== AI 分析结果 =====\n")
    print(result)
    print("\n=======================")

    filename = save_to_markdown(user_text, result)
    print(f"\n✅ 分析结果已保存为文件：{filename}")


if __name__ == "__main__":
    main()
