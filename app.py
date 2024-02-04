import streamlit as st
from openai import OpenAI
import config

st.title("旅游咨询机器人")

client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "old_messages" not in st.session_state:
    st.session_state.old_messages = []

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# 显示旧的聊天记录
if st.session_state.old_messages:
    st.markdown("### 旧的聊天记录")
    for message in st.session_state.old_messages:
        st.markdown(f"{message['role']}: {message['content']}")

# 显示当前的聊天记录
if st.session_state.messages:
    st.markdown("### 当前的聊天记录")
    for message in st.session_state.messages:
        st.markdown(f"{message['role']}: {message['content']}")

# 如果用户还没有提交表单，显示表单
if not st.session_state.form_submitted:
    with st.form(key='travel_info_form'):
        st.write("请填写你的旅游信息")
        num_people = st.number_input("出行人数", min_value=1)
        destination = st.text_input("目的地")
        departure = st.text_input("出发地")
        budget = st.number_input("预算", min_value=0)
        days = st.number_input("旅行天数", min_value=1)
        submit_button = st.form_submit_button(label='提交')

    # 如果用户提交了表单，将旅游信息发送给 GPT-3 模型
    if submit_button:
        # 保存旧的聊天记录
        st.session_state.old_messages.extend(st.session_state.messages)
        # 开始新的聊天会话
        st.session_state.messages = []

        travel_info = f"我计划带着{num_people}人从{departure}去{destination}旅行，预算是{budget}，计划{days}天。"
        st.session_state.messages.append({"role": "user", "content": travel_info})

        # 获取 GPT-3 模型的响应
        response = client.chat_completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )
        response_content = response['choices'][0]['message']['content']
        st.markdown(response_content)
        st.session_state.messages.append({"role": "assistant", "content": response_content})

        # 标记表单已提交
        st.session_state.form_submitted = True

# 如果用户输入了聊天信息，获取 GPT-3 模型的响应
if prompt := st.text_input("你有什么问题吗？"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat_completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
    )
    response_content = response['choices'][0]['message']['content']
    st.markdown(response_content)
    st.session_state.messages.append({"role": "assistant", "content": response_content})
