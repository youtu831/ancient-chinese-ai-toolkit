# -*- coding: utf-8 -*-
# 第 4 天升级版：五风格改写台（DeepSeek 在线大模型版）

import time
import os
import requests

API_KEY = "os.environ.get("DEEPSEEK_API_KEY", "在这里填你的Key")"
URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

STYLES = [
    {"名字": "骈文风",   "指令": "把下面这句话改写成骈文写法，用'落霞与孤鹜齐飞，秋水共长天一色'这类表达，对仗工整，字句优美"},
    {"名字": "张爱玲风", "指令": "把下面这句话改写成张爱玲小说的风格，比喻恰当，文辞细腻"},
    {"名字": "老学究气",  "指令": "把下面这句话改写成老学究语言，用词严谨、咬文嚼字"},
    {"名字": "李白风", "指令": "把下面这句话改写成李白的风格，气势要大到夸张，善用夸张比喻和呼告。例：原句“今天天气很好”改写“今日之天光，可照彻九万里河山！”"},
    {"名字": "鲁迅腔",    "指令": "把下面这句话改写成鲁迅杂文语气，先平淡陈述，再补一句冷冷的转折。示例：原句“今天天气很好”改写“天气自然是好的，好得叫人无可挑剔，然而也便仅此而已。”"},
]

HEADERS = {
    "Authorization": "Bearer " + API_KEY,   # ① 身份证
    "Content-Type": "application/json",
}

TEXT = input("请输入一句要改写的话：\n\n")
results = []

for style in STYLES:
    print(f"\n正在改写为【{style['名字']}】……")

    # ② 对话格式：system 是"规矩"，user 是"这次要干什么"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是一位精通古今文体的中文写作高手。只输出改写结果本身。"},
            {"role": "user", "content": f"{style['指令']}。\n\n要求：只输出改写后的句子，不要解释，不要加引号。\n\n原句：{TEXT}"},
        ],
        "temperature": 0.8,
    }

    response = requests.post(URL, headers=HEADERS, json=payload, timeout=120)

    if response.status_code != 200:
        print(f"  ✗ 出错了 {response.status_code}：{response.text[:200]}")
        continue

    # ③ 拆信的方式也不一样：choices → message → content
    answer = response.json()["choices"][0]["message"]["content"].strip()
    print(f"  → {answer}")
    results.append({"风格": style["名字"], "改写": answer})

# 汇总写入一个文件（这部分和以前一模一样）
name = "改写_" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + ".txt"
with open(name, "w", encoding="utf-8") as f:
    f.write("原句：" + TEXT + "\n")
    f.write("=" * 40 + "\n\n")
    for r in results:
        f.write(f"【{r['风格']}】\n{r['改写']}\n\n")

print("\n" + "=" * 40)
print("全部改写完成，已保存到：" + name)
