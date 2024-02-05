import openai
import streamlit as st
import config

st.title("趣味旅行")

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state["messages"] = []
prompt_placeholder = st.empty()
# 问卷封面部分
if "form_selected" not in st.session_state:
    st.session_state["form_selected"] = None
    prompt_placeholder.markdown("请选择你的旅行者身份开启副本")
cover_placeholder = st.empty()  # 创建一个新的占位符用于放置问卷封面按钮
# 创建一个新的占位符用于显示提示信息


if st.session_state["form_selected"] is None:
    cols = cover_placeholder.columns(3)  # 将问卷封面按钮放在新的占位符中
    with cols[0]:
        if st.button("问卷甲"):
            st.session_state["form_selected"] = "form1"

    with cols[1]:
        if st.button("问卷乙"):
            st.session_state["form_selected"] = "form2"

    with cols[2]:
        if st.button("问卷丙"):
            st.session_state["form_selected"] = "form3"

    if st.session_state["form_selected"] is not None:
        cover_placeholder.empty()  # 清空问卷封面按钮
        prompt_placeholder.empty()  # 清空提示信息


# 问卷部分
if st.session_state["form_selected"] is not None:

    form_placeholder = st.empty()
    skip_button_placeholder = st.empty()  # 创建一个新的占位符用于放置跳过按钮
    if "form_submitted" not in st.session_state or not st.session_state["form_submitted"]:
        with form_placeholder.form(key='my_form'):
            option1 = st.radio(
                '您是否想去下面哪个城市旅游？',
                ('A.美国纽约，自由', 'B.日本东京，时尚', 'C.法国巴黎，浪漫', 'D.中国北京，历史')
            )
            option2 = st.radio(
                '您喜欢什么样的风景？',
                ('A.高楼大厦，繁华都市', 'B.山水相映，自然风光', 'C.海天一色，阳光沙滩', 'D.古色古香，人文景观')
            )
            option3 = st.radio(
                '您的旅行目的是什么？',
                ('A.放松身心，享受生活', 'B.拓展视野，学习知识', 'C.寻找刺激，冒险探索', 'D.结交朋友，增进感情')
            )
            option4 = st.radio(
                '您的旅行方式是什么？',
                ('A.跟团游，省心省力', 'B.自由行，随心所欲', 'C.深度游，体验当地', 'D.主题游，专注兴趣')
            )
            option5 = st.radio(
                '您的旅行预算是多少？',
                ('A.不限，只要有趣', 'B.适中，性价比高', 'C.节省，花最少钱', 'D.奢华，享受最好的')
            )
            submit_button = st.form_submit_button(label='提交')

        skip_button = skip_button_placeholder.button('填问卷太麻烦？一键开启盲盒旅行')

        # 如果用户提交了问卷，将问卷结果作为聊天机器人的输入
        if submit_button or skip_button:
            st.session_state["form_submitted"] = True
            form_placeholder.empty()  # 清除问卷
            skip_button_placeholder.empty()  # 清除跳过按钮
            st.markdown("欢迎咨询旅游服务")  # 显示欢迎消息

            if submit_button:
                status_message = st.empty()  # 创建状态消息的占位符
                status_message.write("正在为您生成旅游计划...")  # 显示状态消息
                full_response = ""
                for response in client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[{"role": "user",
                                   "content": f"我选择了：\n问题 1: {option1}\n问题 2: {option2}\n问题 3: {option3}\n问题 4: {option4}\n问题 5: {option5}"}],
                        stream=True,
                ):
                    full_response += (response.choices[0].delta.content or "")
                status_message.empty()  # 清除状态消息
                st.session_state.messages.append({"role": "assistant", "content": full_response})

# 在使用messages之前，检查它是否已经在session_state中初始化
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 聊天部分
if "form_submitted" in st.session_state and st.session_state["form_submitted"]:
    # 添加重置按钮
    if st.button('重置'):
        st.session_state.clear()
        st.experimental_rerun()  # 重定向到一个新的页面

    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
        for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.get("messages", [])],
                stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
