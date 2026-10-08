
# 作品 1：文本风格雷达图分析器（第 3 周的活，今天提前拿下）
# 运行：streamlit run 8.py
import json
import numpy as np#计算库
import requests
import streamlit as st
import matplotlib.pyplot as plt#画图

# 中文字体设置（Windows 必加，否则图上全是方框）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

MODEL = "modelscope.cn/Qwen/Qwen3-0.6B-GGUF:latest"
URL = "http://localhost:11434/api/generate"

# 打分 Prompt
PROMPT_TEMPLATE = """你是中国古代文学教授，请给下面这段文字按 6 个维度打分，每个维度 1 到 10 分。
维度：辞采华丽度、情感浓度、句式整饬度、意象密度、用典密度、语气直白度。

规则：
1. 先在"理由"里用一句话说明你为什么这么打（必须结合这段文字的具体特点）
2. 只输出 JSON，不要输出任何解释文字和代码块标记
3. 严格按这个格式：
{{"理由": "……", "辞采华丽度": 数字, "情感浓度": 数字, "句式整饬度": 数字, "意象密度": 数字, "用典密度": 数字, "语气直白度": 数字}}

示例一（李白"飞流直下三千尺，疑是银河落九天"）：
{{"理由": "夸张比喻，气势飞扬，意象宏大且口语直白", "辞采华丽度": 9, "情感浓度": 8, "句式整饬度": 3, "意象密度": 5, "用典密度": 1, "语气直白度": 8}}

示例二（《静夜思》）：
{{"理由": "白描浅语，意象极少而情思绵长", "辞采华丽度": 3, "情感浓度": 9, "句式整饬度": 5, "意象密度": 4, "用典密度": 1, "语气直白度": 7}}

待评分文字：
{text}
"""

#定义一个打分函数
def 打分(text, temp=0.3):
    """把文字发给模型，拿回分数字典。解析失败就返回 None。"""
    payload = {
        "model": MODEL,
        "prompt": PROMPT_TEMPLATE.format(text=text),
        "stream": False,#一次性输出
        "format": "json",
        "options": {"temperature": temp},#ollama模型要放在options里面才能生效
    }
    r = requests.post(URL, json=payload)
    raw = r.json()["response"]
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    #异常处理
    try:
        data = json.loads(cleaned)
        return data, raw
    except json.JSONDecodeError:
        return None, raw


def 画雷达图(scores, title="文本风格雷达图"):
    """把分数字典画成雷达图。"""
    dims = [k for k in scores.keys() if k != "理由"]
    values = [float(scores[k]) for k in dims]

    # 雷达图要"首尾相接"，所以把第一个值再补到末尾，画出一圈
    angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()#从 0 到 2π（一整圈）平均取 6 个点，endpoint=False 表示不包含终点（否则首尾会重合）。tolist：numpy 数组转成普通 Python 列表
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles_closed, values_closed, "o-", linewidth=2, color="#D85A30")
    ax.fill(angles_closed, values_closed, alpha=0.25, color="#D85A30")
    ax.set_thetagrids(np.degrees(angles), dims)
    ax.set_ylim(0, 10)
    ax.set_title(title, pad=20)
    return fig


# ---------- 网页部分 ----------
st.title("文本风格雷达图分析器")
st.write("粘贴一段文字，看它的风格长成什么形状。（本地小模型分数仅供参考）")

text = st.text_area("要分析的文字：", height=150)
temp = st.slider("打分稳定性（temperature，越低越稳定）", 0.1, 1.5, 0.3)

if st.button("开始分析"):
    if text.strip() == "":
        st.warning("先粘贴点文字呀")
    else:
        with st.spinner("AI 正在给你的文字打分……"):
            scores, raw = 打分(text, temp)

        if scores is None:
            st.error("模型没返回规范 JSON，解析失败。下面是它原话：")
            st.code(raw)
            st.info("本地 0.6B 小模型经常这样。同一段文字拿到 Coze（豆包）里试，成功率会高很多。")
        else:
            if "理由" in scores:
                st.write("**AI 的判断理由：**", scores["理由"])
            fig = 画雷达图(scores)
            st.pyplot(fig)

            st.subheader("各项分数")
            st.bar_chart({k: v for k, v in scores.items() if k != "理由"})
