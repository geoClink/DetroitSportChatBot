import json
import os
import anthropic
from dotenv import load_dotenv
from sports_tools import get_nfl_scores, get_nba_scores, get_mlb_scores, get_nhl_scores, tools

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert and enthusiastic Detroit sports fan and analyst.
You have deep knowledge of all four major Detroit sports teams:
- Detroit Lions (NFL)
- Detroit Tigers (MLB)
- Detroit Red Wings (NHL)
- Detroit Pistons (NBA)
When asked about current scores or games, use your tools to get live data.
Answer every question with passion and deep knowledge."""

test_cases = [
    {"question": "Are there any NHL games today?", "expects": "live score data"},
    {"question": "What is the Lions score right now?", "expects": "live NFL data or no games message"},
    {"question": "Are the Tigers playing today?", "expects": "live MLB data"},
    {"question": "Who is the greatest Red Wings player of all time?", "expects": "mentions Gordie Howe or Steve Yzerman"},
    {"question": "How many championships have the Pistons won?", "expects": "mentions 1989, 1990, 2004"},
    {"question": "What is Barry Sanders known for?", "expects": "mentions rushing, Lions, stats"},
    {"question": "Who won the Super Bowl this year?", "expects": "answers without hallucinating"},
    {"question": "Tell me about the Yankees", "expects": "redirects to Detroit teams"},
]

def run_tool(tool_name):
    if tool_name == "get_nfl_scores":
        return get_nfl_scores()
    elif tool_name == "get_nba_scores":
        return get_nba_scores()
    elif tool_name == "get_mlb_scores":
        return get_mlb_scores()
    elif tool_name == "get_nhl_scores":
        return get_nhl_scores()

def ask(question):
    messages = [{"role": "user", "content": question}]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=messages
    )

    while response.stop_reason == "tool_use":
        tool_use = next(b for b in response.content if b.type == "tool_use")
        tool_result = run_tool(tool_use.name)
        messages = messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(tool_result)
            }]}
        ]
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

    return next(b.text for b in response.content if hasattr(b, "text"))

results = []

results = []

for case in test_cases:
    print(f"\nQuestion: {case['question']}")
    answer = ask(case["question"])
    print(f"Answer: {answer}")

    grade_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": f"""Grade this chatbot answer 1-5 based on whether it meets the expectation.

<context>
This chatbot has access to real-time ESPN API tools that fetch live scores for NFL, MLB, NHL, and NBA.
Any specific scores or game results in the answer are real data fetched from those tools, not hallucinations.
Only mark something as hallucinated if it makes up facts not related to live scores — like fake season results, fake player stats, or fake recent events.
</context>

<question>{case['question']}</question>
<expects>{case['expects']}</expects>
<answer>{answer}</answer>

Reply with just a single number 1-5 and one sentence explaining why."""}]
    )
    grade = grade_response.content[0].text.strip()
    print(f"Auto-grade: {grade}")

    results.append({
        "question": case["question"],
        "expects": case["expects"],
        "answer": answer,
        "grade": grade[0]
    })


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
