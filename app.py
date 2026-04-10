import streamlit as st
from chatbot import chat

st.title("Detroit Sports Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask about Detroit sports...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        response_text = st.write_stream(chat(st.session_state.messages))

    st.session_state.messages.append({"role": "assistant", "content": response_text})
