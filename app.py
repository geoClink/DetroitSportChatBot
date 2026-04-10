import os
import streamlit as st
from chatbot import chat
from dotenv import load_dotenv

load_dotenv()

st.title("Detroit Sports Chatbot")

with st.sidebar:
    st.title("Settings")
    provider = st.selectbox("Provider", ["Groq", "Anthropic"])

    if provider == "Groq":
        st.caption("Get a free key at console.groq.com")
        default_key = os.environ.get("GROQ_API_KEY", "")
    else:
        st.caption("Get a free key at console.anthropic.com")
        default_key = os.environ.get("ANTHROPIC_API_KEY", "")

    api_key = st.text_input(
        "API Key",
        value=default_key,
        type="password",
        placeholder="Paste your API key here",
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask about Detroit sports...")

if user_input:
    if not api_key:
        st.error("Please enter an API key in the sidebar to continue.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            response_text = st.write_stream(
                chat(st.session_state.messages, provider.lower(), api_key)
            )

        st.session_state.messages.append({"role": "assistant", "content": response_text})
