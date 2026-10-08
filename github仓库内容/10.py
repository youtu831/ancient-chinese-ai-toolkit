# 8.py

import json
import os
import requests
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

API_KEY = "os.environ.get("DEEPSEEK_API_KEY", "在这里填你的Key")"
URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
SYSTEM_PROMPT = """你是中国古代文学教授，请给文字按 6 个维度打分，每个维度 1 到 10 分。
维度：辞采华丽度、情感浓度、句式整饬度、意象密度、用典密度、语气直白度。

规则：
1. 先在"理由"里用一句话说明为什么这么打（必须结合这段文字的具体特点）
2. 只输出 JSON，不要解释文字和代码块标记
3. 严格按这个格式：
{"理由": "...", "辞采华丽度": 数字, "情感浓度": 数字, "句式整饬度": 数字, "意象密度": 数字, "用典密度": 数字, "语气直白度": 数字}

示例一（李白"飞流直下三千尺，疑是银河落九天"）：
{"理由": "夸张比喻，气势飞扬，意象宏大且口语直白", "辞采华丽度": 9, "情感浓度": 8, "句式整饬度": 3, "意象密度": 5, "用典密度": 1, "语气直白度": 8}

示例二（《静夜思》）：
{"理由": "白描浅语，意象极少而情思绵长", "辞采华丽度": 3, "情感浓度": 9, "句式整饬度": 5, "意象密度": 4, "用典密度": 1, "语气直白度": 7}
"""


def 打分(text, temp=0.3):
    """把文字发给 DeepSeek，拿回分数字典。"""
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "待评分文字：\n" + text},
        ],
        "temperature": temp,
        "response_format": {"type": "json_object"},
    }
    r = requests.post(URL, headers=headers, json=payload, timeout=120)

    if r.status_code != 200:
        return None, f"接口返回错误 {r.status_code}：{r.text[:300]}"

    content = r.json()["choices"][0]["message"]["content"]
    cleaned = content.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned), content
    except json.JSONDecodeError:
        return None, content


def 画雷达图(scores, title="文本风格雷达图"):
    dims = [k for k in scores.keys() if k != "理由"]
    values = [float(scores[k]) for k in dims]
    angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
    v = values + values[:1]
    a = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(a, v, "o-", linewidth=2, color="#D85A30")
    ax.fill(a, v, alpha=0.25, color="#D85A30")
    ax.set_thetagrids(np.degrees(angles), dims)
    ax.set_ylim(0, 10)
    ax.set_title(title, pad=20)
    return fig


# ---------- 网页部分 ----------
st.title("文本风格雷达图分析器（DeepSeek 版）")
st.write("粘贴一段文字，看它的风格长成什么形状。这次的分数来自在线大模型，可信度高得多。")

text = st.text_area("要分析的文字：", height=150)
temp = st.slider("打分稳定性", 0.1, 1.5, 0.3)

if st.button("开始分析"):
    if text.strip() == "":
        st.warning("先粘贴点文字呀")
    elif API_KEY.startswith("sk-在这里"):
        st.error("你还没把 DeepSeek 的 API Key 填进文件第 20 行呢")
    else:
        with st.spinner("DeepSeek 正在给你的文字打分……"):
            scores, raw = 打分(text, temp)

        if scores is None:
            st.error("解析失败，下面是模型原话：")
            st.code(raw)
        else:
            if "理由" in scores:
                st.write("**AI 的判断理由：**", scores["理由"])
            st.pyplot(画雷达图(scores))
            st.subheader("各项分数")
            st.bar_chart({k: v for k, v in scores.items() if k != "理由"})
