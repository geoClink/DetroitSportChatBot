# Detroit Sports Chatbot — Project Standards

## Coding Standards
- Always add type hints to Python functions
- Use descriptive variable names, never single letters
- Write a comment for any logic that isn't obvious
- Keep functions short — if a function is doing more than one thing, split it up

## Project Context
- This is a Detroit sports chatbot built with Python, Anthropic Claude API, and Streamlit
- Live sports data comes from the ESPN unofficial API via sports_tools.py
- The .env file contains the Anthropic API key — never read or expose it
- eval.py is used to test and grade the system prompt

## How This Project Works
- chatbot.py — core logic, handles Claude API calls and tool use
- app.py — Streamlit UI, displays the chat interface in the browser
- sports_tools.py — fetches live scores from ESPN API
- eval.py — automated prompt evaluation and grading
