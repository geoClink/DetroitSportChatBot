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


def get_standings(sport: str) -> list:
    """Get conference standings for the Detroit team's sport."""
    sport_map = {
        "nfl": ("football", "nfl", "Detroit Lions"),
        "mlb": ("baseball", "mlb", "Detroit Tigers"),
        "nhl": ("hockey", "nhl", "Detroit Red Wings"),
        "nba": ("basketball", "nba", "Detroit Pistons"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league, detroit_team = sport_map[sport.lower()]
    url = f"https://site.api.espn.com/apis/v2/sports/{sport_path}/{league}/standings"
    data = requests.get(url).json()

    standings = []
    for conference in data.get("children", []):
        entries = conference.get("standings", {}).get("entries", [])
        for entry in entries:
            team = entry.get("team", {})
            stats = {s["name"]: s["displayValue"] for s in entry.get("stats", [])}
            standings.append(
                {
                    "team": team.get("displayName", ""),
                    "wins": stats.get("wins", stats.get("wins", "0")),
                    "losses": stats.get("losses", "0"),
                    "conference": conference.get("name", ""),
                    "is_detroit": team.get("displayName", "") == detroit_team,
                }
            )
    return standings


def get_schedule(sport: str) -> list:
    """Get the next 5 upcoming games for the Detroit team in the given sport."""
    sport_map = {
        "nfl": ("football", "nfl"),
        "mlb": ("baseball", "mlb"),
        "nhl": ("hockey", "nhl"),
        "nba": ("basketball", "nba"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league = sport_map[sport.lower()]
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/teams/det/schedule"
    data = requests.get(url).json()

    upcoming = []
    for event in data.get("events", []):
        competition = event["competitions"][0]
        status = competition["status"]["type"]["name"]
        if status == "STATUS_SCHEDULED":
            teams = competition["competitors"]
            home = next(t for t in teams if t["homeAway"] == "home")
            away = next(t for t in teams if t["homeAway"] == "away")
            upcoming.append(
                {
                    "date": event.get("date", ""),
                    "name": event.get("name", ""),
                    "home": home["team"]["displayName"],
                    "away": away["team"]["displayName"],
                    "home_or_away": "home" if home["team"]["abbreviation"] == "DET" else "away",
                }
            )
            if len(upcoming) >= 5:
                break
    return upcoming


def get_injuries(sport: str) -> list:
    """Get injury report for the Detroit team in the given sport."""
    sport_map = {
        "nfl": ("football", "nfl"),
        "mlb": ("baseball", "mlb"),
        "nhl": ("hockey", "nhl"),
        "nba": ("basketball", "nba"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league = sport_map[sport.lower()]
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/teams/det/roster"
    data = requests.get(url).json()

    injured = []
    for group in data.get("athletes", []):
        for player in group.get("items", []):
            status = player.get("status", {})
            if isinstance(status, dict) and status.get("type", "") != "active":
                injuries = player.get("injuries", [])
                injury_desc = (
                    injuries[0].get("description", "Injured")
                    if injuries
                    else status.get("name", "Out")
                )
                injured.append(
                    {
                        "name": player.get("fullName", ""),
                        "position": player.get("position", {}).get("abbreviation", ""),
                        "status": status.get("name", "Out"),
                        "description": injury_desc,
                    }
                )
    return injured if injured else [{"message": "No injuries reported"}]


def get_news(sport: str) -> list:
    """Get the latest news headlines for the Detroit team's sport."""
    sport_map = {
        "nfl": ("football", "nfl"),
        "mlb": ("baseball", "mlb"),
        "nhl": ("hockey", "nhl"),
        "nba": ("basketball", "nba"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league = sport_map[sport.lower()]
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/news?limit=5"
    data = requests.get(url).json()

    articles = []
    for article in data.get("articles", []):
        articles.append(
            {
                "headline": article.get("headline", ""),
                "description": article.get("description", ""),
                "published": article.get("published", ""),
            }
        )
    return articles if articles else [{"message": "No news available"}]


def get_team_stats(sport: str) -> list:
    """Get season statistics for the Detroit team in the given sport."""
    sport_map = {
        "nfl": ("football", "nfl"),
        "mlb": ("baseball", "mlb"),
        "nhl": ("hockey", "nhl"),
        "nba": ("basketball", "nba"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league = sport_map[sport.lower()]
    url = (
        f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/teams/det/statistics"
    )
    data = requests.get(url).json()

    stats = []
    categories = data.get("results", {}).get("stats", {}).get("categories", [])
    for category in categories:
        category_stats = {}
        for stat in category.get("stats", []):
            category_stats[stat.get("displayName", "")] = stat.get("displayValue", "")
        stats.append(
            {
                "category": category.get("displayName", ""),
                "stats": category_stats,
            }
        )
    return stats if stats else [{"message": "No stats available"}]


def get_roster(sport: str) -> dict:
    """Get the current roster for the Detroit team in the given sport."""
    sport_map = {
        "nfl": ("football", "nfl"),
        "mlb": ("baseball", "mlb"),
        "nhl": ("hockey", "nhl"),
        "nba": ("basketball", "nba"),
    }
    if sport.lower() not in sport_map:
        return {"error": f"Unknown sport: {sport}"}

    sport_path, league = sport_map[sport.lower()]
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/teams/det/roster"
    data = requests.get(url).json()

    roster = {}
    for group in data.get("athletes", []):
        position_group = group.get("position", "Players")
        roster[position_group] = [
            {
                "name": p.get("fullName", ""),
                "jersey": p.get("jersey", ""),
                "position": p.get("position", {}).get("abbreviation", ""),
                "age": p.get("age", ""),
            }
            for p in group.get("items", [])
        ]
    return roster


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
    {
        "name": "get_standings",
        "description": "Get current standings for a Detroit team's sport. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_schedule",
        "description": "Get the next 5 upcoming games for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_injuries",
        "description": "Get the injury report for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_roster",
        "description": "Get the current roster for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_news",
        "description": "Get the latest news headlines for a Detroit team's sport. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_team_stats",
        "description": "Get season statistics for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
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
    {
        "type": "function",
        "function": {
            "name": "get_standings",
            "description": "Get current standings for a Detroit team's sport. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
                },
                "required": ["sport"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_schedule",
            "description": "Get the next 5 upcoming games for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
                },
                "required": ["sport"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_injuries",
            "description": "Get the injury report for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
                },
                "required": ["sport"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_roster",
            "description": "Get the current roster for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
                },
                "required": ["sport"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get the latest news headlines for a Detroit team's sport. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
                },
                "required": ["sport"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_stats",
            "description": "Get season statistics for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
                },
                "required": ["sport"],
            },
        },
    },
]
