import json
import os
from groq import Groq
from dotenv import load_dotenv
from sports_tools import (
    get_nfl_scores,
    get_nba_scores,
    get_mlb_scores,
    get_nhl_scores,
    get_standings,
    get_schedule,
    get_injuries,
    get_roster,
    get_news,
    get_team_stats,
    get_transactions,
    get_depth_chart,
    get_leaders,
    get_play_by_play,
    get_box_score,
    groq_tools,
)

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert and enthusiastic Detroit sports fan and analyst.
You have deep knowledge of all four major Detroit sports teams:
- Detroit Lions (NFL)
- Detroit Tigers (MLB)
- Detroit Red Wings (NHL)
- Detroit Pistons (NBA)

When asked about current scores or games, use your tools to get live data.
Never speculate or make up information about recent seasons or events. If you are unsure, say so honestly.
When asked about non-Detroit teams, give a brief 1-2 sentence answer then immediately redirect to Detroit.
Keep answers under 200 words unless the question genuinely requires more detail.
Be enthusiastic but professional — avoid excessive caps and exclamation marks.
After showing live score data, do not add fan commentary. Let the scores speak for themselves.

<output_format>
- For live score questions: show a table with away team, home team, score, and status. Highlight the Detroit team if they are playing.
- For knowledge questions: lead with the direct answer in one sentence, then add supporting detail.
- For non-Detroit questions: one sentence answer, then one sentence redirect to Detroit.
- For uncertain questions: clearly state what you know vs what you are unsure about.
</output_format>"""

test_cases = [
    {"question": "Are there any NHL games today?", "expects": "live score data"},
    {
        "question": "What is the Lions score right now?",
        "expects": "live NFL data or no games message",
    },
    {"question": "Are the Tigers playing today?", "expects": "live MLB data"},
    {
        "question": "Who is the greatest Red Wings player of all time?",
        "expects": "mentions Gordie Howe or Steve Yzerman",
    },
    {
        "question": "How many championships have the Pistons won?",
        "expects": "mentions 1989, 1990, 2004",
    },
    {"question": "What is Barry Sanders known for?", "expects": "mentions rushing, Lions, stats"},
    {"question": "Who won the Super Bowl this year?", "expects": "answers without hallucinating"},
    {"question": "Tell me about the Yankees", "expects": "redirects to Detroit teams"},
]


def run_tool(tool_name: str, tool_input: dict = {}) -> list:
    if tool_name == "get_nfl_scores":
        return get_nfl_scores()
    elif tool_name == "get_nba_scores":
        return get_nba_scores()
    elif tool_name == "get_mlb_scores":
        return get_mlb_scores()
    elif tool_name == "get_nhl_scores":
        return get_nhl_scores()
    elif tool_name == "get_standings":
        return get_standings(tool_input.get("sport", "nfl"))
    elif tool_name == "get_schedule":
        return get_schedule(tool_input.get("sport", "nfl"))
    elif tool_name == "get_injuries":
        return get_injuries(tool_input.get("sport", "nfl"))
    elif tool_name == "get_roster":
        return get_roster(tool_input.get("sport", "nfl"))
    elif tool_name == "get_news":
        return get_news(tool_input.get("sport", "nfl"))
    elif tool_name == "get_team_stats":
        return get_team_stats(tool_input.get("sport", "nfl"))
    elif tool_name == "get_transactions":
        return get_transactions(tool_input.get("sport", "nfl"))
    elif tool_name == "get_depth_chart":
        return get_depth_chart(tool_input.get("sport", "nfl"))
    elif tool_name == "get_leaders":
        return get_leaders(tool_input.get("sport", "nfl"))
    elif tool_name == "get_play_by_play":
        return get_play_by_play(tool_input.get("sport", "nfl"))
    elif tool_name == "get_box_score":
        return get_box_score(tool_input.get("sport", "nfl"))
    return []


def ask(question):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=groq_tools,
        tool_choice="auto",
    )

    while response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        messages.append(response.choices[0].message)

        for tool_call in tool_calls:
            tool_result = run_tool(
                tool_call.function.name,
                json.loads(tool_call.function.arguments or "{}"),
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
        )

    return response.choices[0].message.content


results = []

for case in test_cases:
    print(f"\nQuestion: {case['question']}")
    answer = ask(case["question"])
    print(f"Answer: {answer}")

    grade_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"""Grade this chatbot answer 1-5 based on whether it meets the expectation.

<context>
This chatbot has access to real-time ESPN API tools that fetch live scores for NFL, MLB, NHL, and NBA.
Any specific scores or game results in the answer are real data fetched from those tools, not hallucinations.
Only mark something as hallucinated if it makes up facts not related to live scores — like fake season results, fake player stats, or fake recent events.
The Utah Hockey Club (also called Utah Mammoth) is a real NHL team that relocated from Arizona in 2025. Do not mark it as a hallucination.
</context>

<question>{case['question']}</question>
<expects>{case['expects']}</expects>
<answer>{answer}</answer>

Reply with just a single number 1-5 and one sentence explaining why.""",
            }
        ],
    )
    grade = grade_response.choices[0].message.content.strip()
    print(f"Auto-grade: {grade}")

    results.append(
        {
            "question": case["question"],
            "expects": case["expects"],
            "answer": answer,
            "grade": grade[0],
        }
    )


print("\n\n=== EVAL RESULTS ===\n")
for r in results:
    print(f"""
<test_case>
  <question>{r['question']}</question>
  <expects>{r['expects']}</expects>
  <answer>{r['answer']}</answer>
  <grade>{r['grade']}</grade>
</test_case>
""")

total = sum(int(r["grade"]) for r in results)
avg = total / len(results)
print(f"<summary>")
print(f"  <total_cases>{len(results)}</total_cases>")
print(f"  <average_score>{avg:.1f}/5</average_score>")
print(f"</summary>")
