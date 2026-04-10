# Detroit Sports Chatbot

An AI-powered chatbot that answers questions about Detroit sports — the Lions, Tigers, Red Wings, and Pistons — with live data fetched in real time from the ESPN API.

Built with Python, Streamlit, and support for both Anthropic Claude and Groq (free).

Response quality was measured and improved using an automated eval pipeline — from **3.2 → 4.1 out of 5 (28% improvement)** through iterative prompt engineering.

🚀 **[Live Demo](https://detroitsportchatbot.onrender.com)** — powered by Groq's free API, no setup needed.

---

## Features

- Conversational AI powered by Claude Sonnet or Llama 3.3 via Groq
- Supports both Anthropic and Groq — switch providers in the sidebar
- 13 live data tools powered by the ESPN unofficial API
- Tool use — the model decides when to fetch live data based on the question
- Live tool indicator shows which ESPN endpoint is being called
- Streaming responses displayed word by word
- Suggested questions on first load so new users know what to ask
- Prompt-engineered system prompt scored and improved through automated eval (3.2 → 4.1 out of 5)
- ESPN responses cached for 30 seconds to reduce redundant API calls
- Rate limiting to protect against API quota exhaustion
- Friendly error message when the shared API key hits its daily limit
- API key never exposed to the browser — stored server-side only

---

## Live Data Tools

The chatbot has access to 13 ESPN API tools covering all four Detroit teams:

| Tool | What it returns |
|---|---|
| Scores | Live scores and game status for NFL, NBA, MLB, NHL |
| Standings | Conference standings |
| Schedule | Next 5 upcoming games |
| Injuries | Current injury report |
| Roster | Full roster by position group |
| News | Latest headlines for the sport |
| Team Stats | Season statistics |
| Transactions | Recent signings, trades, and cuts |
| Depth Chart | Starters and backups by position |
| Leaders | Top performers from the current or most recent game |
| Play-by-Play | Live play-by-play during active games |
| Box Score | Full box score from the current or most recent game |

---

## How to Run

**1. Clone the repo**
```bash
git clone https://github.com/geoClink/DetroitSportChatBot.git
cd DetroitSportChatBot
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create a `.env` file in the project root. You can use either provider:

```
# Option 1 — Anthropic (get a key at console.anthropic.com)
ANTHROPIC_API_KEY=your-key-here

# Option 2 — Groq (free, get a key at console.groq.com)
GROQ_API_KEY=your-key-here
```

You can also paste your key directly in the sidebar when the app is running.

**5. Run the app**
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## Project Structure

```
DetroitSportChatBot/
├── app.py              # Streamlit UI with provider selector
├── chatbot.py          # API logic for Anthropic and Groq, tool use, streaming
├── sports_tools.py     # ESPN API functions and tool schemas for both providers
├── eval.py             # Automated prompt evaluation and grading
├── requirements.txt    # Dependencies
├── .env                # API keys (not committed)
└── .gitignore
```

---

## How It Works

1. User asks a question in the chat UI
2. The selected model receives the question along with a Detroit sports system prompt
3. If the question requires live data, the model calls the appropriate ESPN API tool
4. The live data is returned to the model and included in the response
5. The response streams back word by word to the UI

---

## Prompt Engineering

The system prompt was iteratively improved using an automated eval pipeline:

| Version | Score | Change |
|---|---|---|
| v1 | 3.2/5 | Basic system prompt |
| v2 | 3.6/5 | Added examples and bad examples with XML tags |
| v3 | 3.9/5 | Fixed grader context, improved edge case handling |
| v4 | 4.1/5 | Added output format rules for live score responses |

---

## Tech Stack

- Python
- Anthropic Claude API
- Groq API (free tier)
- Streamlit
- ESPN unofficial API
- python-dotenv
- flake8 + black
