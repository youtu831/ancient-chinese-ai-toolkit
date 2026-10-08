#处理文章内容
#运行方式 终端streamlit run 7.py

import requests
import streamlit as st #终端方式打开

MODEL = "modelscope.cn/Qwen/Qwen3-0.6B-GGUF:latest"#调用ollama模型
URL = "http://localhost:11434/api/generate"#本地ollama地址

st.title("文档小助手")
st.write("上传一个 txt 文件，让 AI 帮你读它。")#阐释该网页运行效果

# 上传文件
uploaded = st.file_uploader("选择一个 txt 文件", type=["txt"])#上传类型为txt的文件

# 下拉选择想让ai完成的任务
TASKS = [
    {"名字": "总结大意", "指令": "请用三到五句话概括下面这段文字的主要内容。"},
    {"名字": "提取要点", "指令": "请分条列出下面这段文字的关键信息，每条不超过 20 字。"},
    {"名字": "翻译成现代汉语", "指令": "请把下面这段文字翻译成通顺的现代汉语，保留原意，难词加括号注释。"},
    {"名字": "出三道题", "指令": "请基于下面这段文字出三道思考题（不要给答案），题目要有启发性。"},
    {"名字":"翻译成文言文","指令":"请把下面这段文字改为文言文的形式"}
]
task = st.selectbox("你想让它做什么？", [t["名字"] for t in TASKS])

temp = st.slider("活泼程度", 0.1, 1.5, 0.7)#选择活泼程度 0.1—1.5，0.7为默认值

if st.button("开始处理"):#按下按钮
    if uploaded is None:
        st.warning("先上传一个 txt 文件呀")
    else:
        # 读出文件内容
        content = uploaded.read().decode("utf-8")

        # 找到用户选的是哪一个任务
        指令 = ""
        for t in TASKS:
            if t["名字"] == task:
                指令 = t["指令"]
                break

        prompt = f"""{指令}

要求：只输出结果本身，不要说"好的""以下是"这类开场白。

文字内容：
{content[:2000]}
"""
# 截取输入的前2000个字发给模型
        #开始处理文字
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temp},#ollama的参数要放进options内部
        }
        #把服务器回信解析成 Python 字典
        with st.spinner("AI 正在读你的文件……"):
            response = requests.post(URL, json=payload)
            answer = response.json()["response"].strip()

        # 分栏展示
        col1, col2 = st.columns(2)
        #左边一栏展示原文
        with col1:
            st.subheader("原文预览")
            st.text(content[:500] + ("……" if len(content) > 500 else ""))
        #右边一栏展示结果
        with col2:
            st.subheader(task)
            st.success(answer)
