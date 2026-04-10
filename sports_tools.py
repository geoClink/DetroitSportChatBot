import requests


def get_nfl_scores():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    response = requests.get(url)
    data = response.json()
    games = []
    for event in data.get("events", []):
        competition = event["competitions"][0]
        teams = competition["competitors"]
        home = next(t for t in teams if t["homeAway"] == "home")
        away = next(t for t in teams if t["homeAway"] == "away")
        games.append(
            {
                "home": home["team"]["displayName"],
                "away": away["team"]["displayName"],
                "home_score": home.get("score", "0"),
                "away_score": away.get("score", "0"),
                "status": competition["status"]["type"]["description"],
            }
        )
    return games


def get_nba_scores():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    response = requests.get(url)
    data = response.json()
    games = []
    for event in data.get("events", []):
        competition = event["competitions"][0]
        teams = competition["competitors"]
        home = next(t for t in teams if t["homeAway"] == "home")
        away = next(t for t in teams if t["homeAway"] == "away")
        games.append(
            {
                "home": home["team"]["displayName"],
                "away": away["team"]["displayName"],
                "home_score": home.get("score", "0"),
                "away_score": away.get("score", "0"),
                "status": competition["status"]["type"]["description"],
            }
        )
    return games


def get_mlb_scores():
    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    response = requests.get(url)
    data = response.json()
    games = []
    for event in data.get("events", []):
        competition = event["competitions"][0]
        teams = competition["competitors"]
        home = next(t for t in teams if t["homeAway"] == "home")
        away = next(t for t in teams if t["homeAway"] == "away")
        games.append(
            {
                "home": home["team"]["displayName"],
                "away": away["team"]["displayName"],
                "home_score": home.get("score", "0"),
                "away_score": away.get("score", "0"),
                "status": competition["status"]["type"]["description"],
            }
        )
    return games


def get_nhl_scores():
    url = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
    response = requests.get(url)
    data = response.json()
    games = []
    for event in data.get("events", []):
        competition = event["competitions"][0]
        teams = competition["competitors"]
        home = next(t for t in teams if t["homeAway"] == "home")
        away = next(t for t in teams if t["homeAway"] == "away")
        games.append(
            {
                "home": home["team"]["displayName"],
                "away": away["team"]["displayName"],
                "home_score": home.get("score", "0"),
                "away_score": away.get("score", "0"),
                "status": competition["status"]["type"]["description"],
            }
        )
    return games


# Anthropic tool format
tools = [
    {
        "name": "get_nfl_scores",
        "description": "Get current NFL scores and game statuses",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_nba_scores",
        "description": "Get current NBA scores and game statuses",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_mlb_scores",
        "description": "Get current MLB scores and game statuses",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_nhl_scores",
        "description": "Get current NHL scores and game statuses",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

# Groq/OpenAI tool format
groq_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_nfl_scores",
            "description": "Get current NFL scores and game statuses",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_nba_scores",
            "description": "Get current NBA scores and game statuses",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_mlb_scores",
            "description": "Get current MLB scores and game statuses",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_nhl_scores",
            "description": "Get current NHL scores and game statuses",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]
