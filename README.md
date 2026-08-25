# Detroit Sports Chatbot

An AI agent that answers questions about Detroit sports — the Lions, Tigers, Red Wings, and Pistons — with live data fetched in real time from the ESPN API.

Built with Python, Streamlit, Anthropic Claude, and Groq.

Response quality was measured and improved using an automated eval pipeline — from **3.2 → 4.1 out of 5 (28% improvement)** through iterative prompt engineering.

🚀 **[Live Demo](https://detroitsportchatbot.onrender.com)**

---

## Features

- Tool-calling agent — the model decides when to fetch live data, which of 16 ESPN endpoints to call, and how to synthesize the answer
- Two AI providers: Anthropic Claude Sonnet and Groq — switch in the sidebar
- Server-side API key powers the live demo with no setup required
- Streaming responses word by word
- Live sidebar shows any Detroit game happening today, updated every 5 minutes
- Automated eval pipeline grades responses 1–5 — score displayed live in the sidebar
- ESPN responses cached 30 seconds
- Rate limiting (10 requests/minute) with resend prompt
- Graceful error messages for rate limits, invalid keys, and decommissioned models
- API key stored server-side only — never exposed to the browser
- 11 pytest tests covering ESPN API shape and tool dispatch

---

## Live Data Tools

The agent has access to 16 ESPN API tools covering all four Detroit teams:

| Tool | What it returns |
|---|---|
| NFL / NBA / MLB / NHL Scores | Live scores and game status |
| Recent Results | Last 5 completed game scores and W/L |
| Standings | Conference standings |
| Schedule | Next 5 upcoming games |
| Injuries | Current injury report |
| Roster | Full roster by position group |
| News | Latest Detroit-specific headlines |
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

Create a `.env` file in the project root:

```
# Groq (free, get a key at console.groq.com)
GROQ_API_KEY=your-key-here

# Anthropic (get a key at console.anthropic.com)
ANTHROPIC_API_KEY=your-key-here
```

If no key is found in the environment, the sidebar will prompt you to paste one in.

**5. Run the app**
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## Run the Tests

```bash
python -m pytest test_espn.py -v
```

---

## Run the Eval

```bash
python eval.py
```

Grades 8 test cases 1–5 and writes results to `eval_results.json`. Commit the file to update the score shown in the sidebar.

---

## Project Structure

```
DetroitSportChatBot/
├── app.py              # Streamlit UI, sidebar scores, rate limiting, error handling
├── chatbot.py          # Anthropic and Groq API logic — tool-use loop and streaming
├── sports_tools.py     # 16 ESPN API functions, tool schemas, run_tool dispatch
├── eval.py             # Automated prompt evaluation and grading
├── eval_results.json   # Most recent eval score (commit after running eval.py)
├── test_espn.py        # Pytest tests for ESPN tools and dispatch
├── requirements.txt    # Dependencies
└── .env                # API keys (not committed)
```

---

## How It Works

1. User asks a question in the chat UI
2. The selected model receives the question along with the Detroit sports system prompt
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
- Groq API
- Streamlit
- ESPN unofficial API
- pytest
- python-dotenv
