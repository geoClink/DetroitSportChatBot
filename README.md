# Detroit Sports Chatbot

An AI-powered chatbot that answers questions about Detroit sports — the Lions, Tigers, Red Wings, and Pistons — with live scores fetched in real time from the ESPN API.

Built with Python, the Anthropic Claude API, and Streamlit.

---

## Features

- Conversational AI powered by Claude claude-sonnet-4-6
- Live scores and game data from the ESPN unofficial API
- Tool use — Claude decides when to fetch live data based on the question
- Streaming responses displayed word by word
- Prompt-engineered system prompt scored and improved through automated eval (3.2 → 4.1 out of 5)
- Secure API key handling with python-dotenv

---

## How to Run

**1. Clone the repo**
```bash
git clone https://github.com/your-username/DetroitSportChatBot.git
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

**4. Add your Anthropic API key**

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your-key-here
```

**5. Run the app**
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## Project Structure

```
DetroitSportChatBot/
├── app.py              # Streamlit UI
├── chatbot.py          # Claude API logic and tool use
├── sports_tools.py     # ESPN API functions and tool schemas
├── eval.py             # Automated prompt evaluation
├── requirements.txt    # Dependencies
├── .env                # API key (not committed)
└── .gitignore
```

---

## How It Works

1. User asks a question in the chat UI
2. Claude receives the question along with a Detroit sports system prompt
3. If the question is about live scores, Claude calls the ESPN API tool
4. The live data is returned to Claude and included in the response
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
- Streamlit
- ESPN unofficial API
- python-dotenv
- flake8 + black
