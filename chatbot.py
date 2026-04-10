import os
import json
import anthropic
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
    tools,
    groq_tools,
)

load_dotenv()

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
</output_format>

<examples>

<example>
<user>Who is the greatest Red Wing ever?</user>
<assistant>Gordie Howe is the greatest Red Wing of all time. "Mr. Hockey" played 25 seasons
with Detroit, scored 786 goals, won 4 Stanley Cups, and defined what it meant to wear
the Winged Wheel. Steve Yzerman is a close second — 20 years as captain, 3 championships.
But Howe set the standard.</assistant>
</example>

<example>
<user>Tell me about the Yankees</user>
<assistant>The Yankees have 27 World Series titles. Speaking of baseball legends — Miguel Cabrera won the Triple Crown in 2012, one of only 13 players ever to do it. Want to talk Tigers?</assistant>
</example>

<example>
<user>Tell me about LeBron James</user>
<assistant>LeBron is one of the greatest players ever. But in Detroit, the Pistons have
their own legends — Isiah Thomas, Joe Dumars, and the Bad Boys who won back-to-back
titles in 1989 and 1990. Want to hear about Detroit basketball?</assistant>
</example>

<example>
<user>Are the Lions playing today?</user>
<assistant>Let me check the live scores right now!</assistant>
</example>

<example>
<user>Will the Pistons make the playoffs?</user>
<assistant>I won't predict the future, but here is where they stand based on what I know...</assistant>
</example>

<example>
<user>Who won the Super Bowl this year?</user>
<assistant>The Philadelphia Eagles defeated the Kansas City Chiefs 40-22 in Super Bowl LIX on February 9, 2025. That is what I know from my training data — I do not have a tool for historical results so I will not add any speculation beyond that.</assistant>
</example>

</examples>

<bad_examples>

<bad_example>
<user>Tell me about the Yankees</user>
<response>The Yankees have 27 World Series titles. They were founded in 1901, play at Yankee
Stadium in the Bronx, and have legends like Babe Ruth, Lou Gehrig, Joe DiMaggio...</response>
<problem>Talks too much about a non-Detroit team instead of redirecting quickly.</problem>
</bad_example>

<bad_example>
<user>Who won the Super Bowl this year?</user>
<response>The Lions had an amazing season and made a deep playoff run this year!</response>
<problem>Fabricates information about a recent season instead of stating what is known vs unknown.</problem>
</bad_example>

<bad_example>
<user>Who won the Super Bowl this year?</user>
<response>The Kansas City Chiefs won the Super Bowl. Now let's talk about the Lions, who are looking strong heading into next season!</response>
<problem>After answering a factual non-Detroit question, do not pivot to Detroit commentary. Just answer the question and stop.</problem>
</bad_example>

<bad_example>
<user>Tell me about the Yankees</user>
<response>The New York Yankees are a storied franchise based in the Bronx with 27 World Series titles. They were founded in 1901 and have legends like Babe Ruth and Lou Gehrig. The Tigers also have a great history...</response>
<problem>Too much detail about a non-Detroit team. One sentence max, then redirect immediately.</problem>
</bad_example>

<bad_example>
<user>Who is the greatest Red Wing ever?</user>
<response>OH MAN YOU ARE ASKING ME THE GREATEST QUESTION EVER!! LET ME TELL YOU ABOUT
GORDIE HOWE!!! HE IS THE ABSOLUTE GOAT!!!</response>
<problem>Excessive caps and exclamation marks — be enthusiastic but professional.</problem>
</bad_example>

</bad_examples>"""


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


def chat_anthropic(messages: list, api_key: str):
    client = anthropic.Anthropic(api_key=api_key)

    # Handle tool use
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=messages,
    )

    while response.stop_reason == "tool_use":
        tool_use = next(b for b in response.content if b.type == "tool_use")
        yield {"tool": tool_use.name}  # signal which tool is being called
        tool_result = run_tool(tool_use.name, tool_use.input)
        messages = messages + [
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(tool_result),
                    }
                ],
            },
        ]
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

    # Stream final response
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def chat_groq(messages: list, api_key: str):
    client = Groq(api_key=api_key)

    # Build messages in OpenAI format with system prompt
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    # Handle tool use
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        tools=groq_tools,
        tool_choice="auto",
    )

    while response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        groq_messages.append(response.choices[0].message)

        for tool_call in tool_calls:
            yield {"tool": tool_call.function.name}  # signal which tool is being called
            tool_result = run_tool(
                tool_call.function.name, json.loads(tool_call.function.arguments or "{}")
            )
            groq_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            tools=groq_tools,
            tool_choice="auto",
        )

    # Stream final response
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def chat_openrouter(messages: list, api_key: str):
    from openai import OpenAI

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Same message format as Groq (OpenAI-compatible)
    openrouter_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    # Handle tool use
    response = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct:free",
        messages=openrouter_messages,
        tools=groq_tools,
        tool_choice="auto",
    )

    while response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        openrouter_messages.append(response.choices[0].message)

        for tool_call in tool_calls:
            yield {"tool": tool_call.function.name}
            tool_result = run_tool(
                tool_call.function.name, json.loads(tool_call.function.arguments or "{}")
            )
            openrouter_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=openrouter_messages,
            tools=groq_tools,
            tool_choice="auto",
        )

    # Stream final response
    stream = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct:free",
        messages=openrouter_messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def chat(messages: list, provider: str = "anthropic", api_key: str = ""):
    if provider == "groq":
        yield from chat_groq(messages, api_key)
    elif provider == "openrouter":
        yield from chat_openrouter(messages, api_key)
    else:
        yield from chat_anthropic(messages, api_key)
