# -*- coding: utf-8 -*-
# ============================================================
# 第 5 天下午：五风格改写台 · 网页版
# 组装说明：网页壳来自 5.py（零件），AI 改写循环来自 4.py（发动机）
#
# 运行方式（老规矩）：
#   PyCharm 底部「终端」→ 输入 streamlit run 6.py
#
# 新增加的两个小零件：
#   st.progress  进度条（改写要等，让用户知道没卡死）
#   st.expander  可折叠卡片（5 个结果排开不占地方）
# ============================================================

import time
import os
import requests
import streamlit as st

MODEL = "deepseek-chat"
URL = "https://api.deepseek.com/chat/completions"
API_KEY = "os.environ.get("DEEPSEEK_API_KEY", "在这里填你的Key")"

# ========== 风格列表（从你的 4.py 原样搬来，一字未改）==========
STYLES = [
    {"名字": "骈文风",   "指令": "把下面这句话改写成骈文写法，用'落霞与孤鹜齐飞，秋水共长天一色’这类表达，对仗工整，字句优美"},
    {"名字": "张爱玲风", "指令": "把下面这句话改写成张爱玲小说的风格，比喻恰当，文辞细腻"},
    {"名字": "老学究气",  "指令": "把下面这句话改写成老学究语言，用词严谨、咬文嚼字"},
    {"名字": "李白风", "指令": "把下面这句话改写成李白的风格,气势要大到夸张，善用夸张比喻和呼告。例：原句“今天天气很好”改写“今日之天光，可照彻九万里河山！”"},
    {"名字": "鲁迅腔", "指令": "把下面这句话改写成鲁迅杂文语气，先平淡陈述，再补一句冷冷的转折。示例：原句“今天天气很好” 改写“天气自然是好的，好得叫人无可挑剔，然而也便仅此而已。”"},
]
# ===========================================================

HEADERS = {
    "Authorization": "Bearer " + API_KEY,   # 使用ds的身份证
    "Content-Type": "application/json",
}


# ---------- 网页壳（来自 5.py 学的零件）----------
st.title("句子改写大测评")
st.write("输入一句话，看它变成五种文风。")
# 滑块画出来后，要用变量"接住"它拨到哪（像旋钮 + 音量条）
temp = st.slider("改写活泼程度（temperature）", 0.1, 1.5, 0.7)
st.caption("0.1 = 每次都差不多；0.7 = 常规；1.5 = 天马行空易跑偏")
text = st.text_area("要改写的句子：")

if st.button("开始改写"):
    if text.strip() == "":
        st.warning("先写点什么再点啊")
    else:
        results = []
        progress = st.progress(0, text="准备开始……")

        # ---------- AI 改写循环（来自 4.py 的发动机）----------
        for i, style in enumerate(STYLES):
            progress.progress((i) / len(STYLES), text=f"正在改写为【{style['名字']}】……")


            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "你是一位精通古今文体的中文写作高手。只输出改写结果本身。"},
                    {"role": "user",
                "content": f"{style['指令']}。\n\n要求：只输出改写后的句子，不要解释，不要加引号。\n\n原句：{text}"},
            ],
                "temperature": temp,
            }
            response = requests.post(URL, headers=HEADERS,json=payload,timeout=120)
            answer = response.json()["choices"][0]["message"]["content"].strip()
            results.append({"风格": style["名字"], "改写": answer})

        progress.progress(1.0, text="全部完成！")
        st.balloons()


        # ---------- 展示结果 ----------
        st.subheader("改写结果")
        for r in results:
            with st.expander(f"【{r['风格']}】"):
                st.write(r["改写"])

        # ---------- 存档（老传统不能丢）----------
        name = "改写_" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + ".txt"
        with open(name, "w", encoding="utf-8") as f:
            f.write("原句：" + text + "\n")
            f.write("=" * 40 + "\n\n")
            for r in results:
                f.write(f"【{r['风格']}】\n{r['改写']}\n\n")
        st.success("已保存到 " + name)
