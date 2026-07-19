import os
import io
import time
import groq
import streamlit as st
from groq import RateLimitError, AuthenticationError
from gtts import gTTS
from chatbot import chat
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from sports_tools import get_nfl_scores, get_nba_scores, get_mlb_scores, get_nhl_scores


RATE_LIMIT = 10  # max requests per minute

DETROIT_TEAMS = {
    "nfl": "Detroit Lions",
    "nba": "Detroit Pistons",
    "mlb": "Detroit Tigers",
    "nhl": "Detroit Red Wings",
}

SPORT_EMOJI = {"nfl": "🏈", "nba": "🏀", "mlb": "⚾", "nhl": "🏒"}

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

# Must be the first Streamlit call
st.set_page_config(
    page_title="Detroit Sports Chatbot",
    page_icon="🦁",
    layout="centered",
)

st.markdown(
    """
    <style>
    /* Detroit Lions blue on the main title */
    h1 { color: #0076B6; }

    /* Lions blue on sidebar headers */
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0076B6;
    }

    /* Score card in sidebar */
    .score-card {
        background: rgba(0, 118, 182, 0.08);
        border-left: 3px solid #0076B6;
        border-radius: 4px;
        padding: 0.4rem 0.6rem;
        margin-bottom: 0.4rem;
    }
    .score-card .teams { font-weight: 600; font-size: 0.85rem; }
    .score-card .score { font-size: 1rem; font-weight: 700; color: #0076B6; }
    .score-card .status { color: #888; font-size: 0.75rem; }

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


@st.cache_data(ttl=300)
def fetch_detroit_scores() -> list[dict]:
    """Check all four scoreboards and return only games that include a Detroit team."""
    score_fns = {
        "nfl": get_nfl_scores,
        "nba": get_nba_scores,
        "mlb": get_mlb_scores,
        "nhl": get_nhl_scores,
    }
    detroit_games = []
    for sport, fn in score_fns.items():
        games = fn()
        detroit_name = DETROIT_TEAMS[sport]
        for game in games:
            if "error" in game:
                continue
            if game["home"] == detroit_name or game["away"] == detroit_name:
                detroit_games.append({**game, "sport": sport})
    return detroit_games


st.title("Detroit Sports Chatbot")

with st.sidebar:
    st.header("Settings")
    provider = st.selectbox("Provider", ["Groq", "Anthropic"])

    if provider == "Groq":
        server_key = os.environ.get("GROQ_API_KEY", "")
        st.caption("Get a free key at console.groq.com")
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

    voice_enabled = st.checkbox("Voice responses", value=False)

    if st.session_state.get("messages"):
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.divider()

    st.subheader("Today's Detroit Games")
    detroit_games = fetch_detroit_scores()
    if detroit_games:
        for game in detroit_games:
            emoji = SPORT_EMOJI[game["sport"]]
            st.markdown(
                f"""<div class="score-card">
                    <div class="teams">{emoji} {game["away"]} @ {game["home"]}</div>
                    <div class="score">{game["away_score"]} – {game["home_score"]}</div>
                    <div class="status">{game["status"]}</div>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No Detroit games on the schedule today.")

    if st.button("Refresh scores", use_container_width=True):
        fetch_detroit_scores.clear()
        st.rerun()

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

if "pending_input" not in st.session_state:
    st.session_state.pending_input = None

for msg in st.session_state.messages:
    avatar = "🦁" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# Show suggested questions only when chat is empty
if not st.session_state.messages:
    st.caption("Try asking:")
    cols = st.columns(2)
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        if cols[i % 2].button(question, key=f"suggested_{i}"):
            st.session_state.suggested_input = question
            st.rerun()

# If a previous message was dropped by the rate limiter, offer to resend it
if st.session_state.pending_input:
    col1, col2 = st.columns([3, 1])
    col1.caption(f"Message not sent: _{st.session_state.pending_input}_")
    if col2.button("Resend"):
        st.session_state.suggested_input = st.session_state.pending_input
        st.session_state.pending_input = None
        st.rerun()

# Use suggested input if a button was clicked
user_input = st.chat_input("Ask about Detroit sports...")
if st.session_state.suggested_input:
    user_input = st.session_state.suggested_input
    st.session_state.suggested_input = None

# Voice input: record audio, transcribe with Groq Whisper, use as user_input
audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹ Stop", key="mic")
if audio and api_key and provider == "Groq":
    try:
        groq_client = groq.Groq(api_key=api_key)
        transcription = groq_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=("audio.wav", audio["bytes"]),
        )
        user_input = transcription.text
    except AuthenticationError:
        st.error("Invalid Groq API key — voice input unavailable. Check your key in the sidebar.")

if user_input:
    if not api_key:
        st.error("Please enter an API key in the sidebar to continue.")
    else:
        # Remove requests older than 60 seconds
        now = time.time()
        st.session_state.request_times = [t for t in st.session_state.request_times if now - t < 60]
        if len(st.session_state.request_times) >= RATE_LIMIT:
            st.session_state.pending_input = user_input
            st.warning("You're sending messages too quickly. Wait a moment and try again.")
            st.stop()

        st.session_state.request_times.append(now)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant", avatar="🦁"):
            thinking_placeholder = st.empty()
            tool_placeholder = st.empty()
            text_placeholder = st.empty()
            full_text = ""
            tools_called = []

            thinking_placeholder.caption("⏳ Thinking...")

            try:
                for chunk in chat(st.session_state.messages, provider.lower(), api_key):
                    if isinstance(chunk, dict) and "tool" in chunk:
                        # Show which ESPN tool is being called
                        thinking_placeholder.empty()
                        label = TOOL_LABELS.get(chunk["tool"], chunk["tool"])
                        tools_called.append(label)
                        tool_placeholder.caption(
                            "📡 Fetching live data: " + ", ".join(tools_called)
                        )
                    else:
                        thinking_placeholder.empty()
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

            # Voice output: only play if the user has enabled it
            if voice_enabled:
                tts = gTTS(text=response_text, lang="en")
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                st.audio(audio_buffer, format="audio/mp3", autoplay=True)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
