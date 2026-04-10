import os
import time
import streamlit as st
from groq import RateLimitError, AuthenticationError
from chatbot import chat
from dotenv import load_dotenv

RATE_LIMIT = 10  # max requests per minute

TOOL_LABELS = {
    "get_nfl_scores": "NFL scores",
    "get_nba_scores": "NBA scores",
    "get_mlb_scores": "MLB scores",
    "get_nhl_scores": "NHL scores",
    "get_standings": "standings",
    "get_schedule": "schedule",
    "get_injuries": "injury report",
    "get_roster": "roster",
    "get_news": "news",
    "get_team_stats": "team stats",
    "get_transactions": "transactions",
    "get_depth_chart": "depth chart",
    "get_leaders": "game leaders",
    "get_play_by_play": "play-by-play",
    "get_box_score": "box score",
}

SUGGESTED_QUESTIONS = [
    "Are the Lions playing today?",
    "Show me the Pistons standings",
    "Who did the Tigers sign recently?",
    "What are the Red Wings team stats?",
    "Who's starting at QB for the Lions?",
    "Show me the Pistons box score",
]

load_dotenv()

st.markdown(
    """
    <style>
    /* Mobile: reduce side padding */
    @media (max-width: 768px) {
        .block-container { padding-left: 0.75rem; padding-right: 0.75rem; }
    }
    /* Suggested question buttons: left-align text */
    div[data-testid="column"] button {
        text-align: left;
        white-space: normal;
        height: auto;
        padding: 0.4rem 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Detroit Sports Chatbot")

with st.sidebar:
    st.title("Settings")
    provider = st.selectbox("Provider", ["OpenRouter", "Groq", "Anthropic"])

    if provider == "Groq":
        server_key = os.environ.get("GROQ_API_KEY", "")
        st.caption("Get a free key at console.groq.com")
    elif provider == "OpenRouter":
        server_key = os.environ.get("OPENROUTER_API_KEY", "")
        st.caption("Get a free key at openrouter.ai")
    else:
        server_key = os.environ.get("ANTHROPIC_API_KEY", "")
        st.caption("Get a free key at console.anthropic.com")

    if server_key:
        # Key exists on the server — use it silently, never expose it to the browser
        api_key = server_key
        st.caption("✓ Using server API key")
    else:
        # No server key — ask the user for their own
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="Paste your API key here",
        )

    st.divider()
    st.caption("Prompt Engineering")
    st.progress(0.82, text="Eval score: 4.1 / 5")
    st.caption(
        "Improved from 3.2 → 4.1 (28%) through iterative prompt engineering with automated grading."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "request_times" not in st.session_state:
    st.session_state.request_times = []

if "suggested_input" not in st.session_state:
    st.session_state.suggested_input = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Show suggested questions only when chat is empty
if not st.session_state.messages:
    st.caption("Try asking:")
    cols = st.columns(2)
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        if cols[i % 2].button(question, key=f"suggested_{i}"):
            st.session_state.suggested_input = question
            st.rerun()

# Use suggested input if a button was clicked
user_input = st.chat_input("Ask about Detroit sports...")
if st.session_state.suggested_input:
    user_input = st.session_state.suggested_input
    st.session_state.suggested_input = None

if user_input:
    if not api_key:
        st.error("Please enter an API key in the sidebar to continue.")
    else:
        # Remove requests older than 60 seconds
        now = time.time()
        st.session_state.request_times = [t for t in st.session_state.request_times if now - t < 60]
        if len(st.session_state.request_times) >= RATE_LIMIT:
            st.warning("You're sending messages too quickly. Wait a moment and try again.")
            st.stop()

        st.session_state.request_times.append(now)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            tool_placeholder = st.empty()
            text_placeholder = st.empty()
            full_text = ""
            tools_called = []

            try:
                for chunk in chat(st.session_state.messages, provider.lower(), api_key):
                    if isinstance(chunk, dict) and "tool" in chunk:
                        # Show which ESPN tool is being called
                        label = TOOL_LABELS.get(chunk["tool"], chunk["tool"])
                        tools_called.append(label)
                        tool_placeholder.caption(
                            "📡 Fetching live data: " + ", ".join(tools_called)
                        )
                    else:
                        full_text += chunk
                        text_placeholder.markdown(full_text)
            except RateLimitError:
                tool_placeholder.empty()
                text_placeholder.warning(
                    "The shared API key has hit its daily limit. "
                    "Get your own free key at [console.groq.com](https://console.groq.com) "
                    "and paste it in the sidebar — it takes 30 seconds."
                )
                st.stop()
            except AuthenticationError:
                tool_placeholder.empty()
                text_placeholder.error(
                    "Invalid API key. Please check your key and try again. "
                    "Get a free key at [console.groq.com](https://console.groq.com)."
                )
                st.stop()

            # Clear tool indicator once response is complete
            tool_placeholder.empty()
            response_text = full_text

        st.session_state.messages.append({"role": "assistant", "content": response_text})
