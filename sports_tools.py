import time
import requests

# Simple cache: stores {url: (timestamp, data)}
_cache: dict = {}
CACHE_TTL = 30  # seconds


def _fetch_espn(url: str) -> dict:
    """Fetch ESPN API data with caching and error handling."""
    now = time.time()
    if url in _cache:
        cached_at, cached_data = _cache[url]
        if now - cached_at < CACHE_TTL:
            return cached_data

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        return {"error": "ESPN API timed out. Try again in a moment."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"ESPN API returned an error: {e}"}
    except Exception:
        return {"error": "Could not reach ESPN API. Try again in a moment."}

    _cache[url] = (now, data)
    return data


def get_nfl_scores():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    data = _fetch_espn(url)
    if "error" in data:
        return [data]
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
    data = _fetch_espn(url)
    if "error" in data:
        return [data]
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
    data = _fetch_espn(url)
    if "error" in data:
        return [data]
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
    data = _fetch_espn(url)
    if "error" in data:
        return [data]
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
    data = _fetch_espn(url)

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
    data = _fetch_espn(url)

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
    data = _fetch_espn(url)

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
    data = _fetch_espn(url)

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
    data = _fetch_espn(url)

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
    data = _fetch_espn(url)

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


def _get_det_game_id(sport_path: str, league: str) -> str | None:
    """Find the current or most recent Detroit game ID from the scoreboard."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/scoreboard"
    data = _fetch_espn(url)
    for event in data.get("events", []):
        competitors = event["competitions"][0]["competitors"]
        if any(t["team"]["abbreviation"] == "DET" for t in competitors):
            return event["id"]
    return None


def get_transactions(sport: str) -> list:
    """Get recent transactions (signings, trades, cuts) for the Detroit team."""
    sport_map = {
        "nfl": ("football", "nfl", "8"),
        "mlb": ("baseball", "mlb", "6"),
        "nhl": ("hockey", "nhl", "5"),
        "nba": ("basketball", "nba", "8"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league, team_id = sport_map[sport.lower()]
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/transactions?limit=10&team={team_id}"
    data = _fetch_espn(url)

    transactions = []
    for item in data.get("transactions", []):
        transactions.append(
            {
                "description": item.get("description", ""),
                "date": item.get("date", "")[:10],
            }
        )
    return transactions if transactions else [{"message": "No recent transactions"}]


def get_depth_chart(sport: str) -> list:
    """Get the depth chart (starters and backups by position) for the Detroit team."""
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
        f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/teams/det/depthcharts"
    )
    data = _fetch_espn(url)

    depth_chart = []
    for formation in data.get("depthchart", []):
        positions = []
        for pos_key, pos_data in formation.get("positions", {}).items():
            athletes = [a.get("displayName", "") for a in pos_data.get("athletes", [])]
            positions.append(
                {
                    "position": pos_data.get("position", {}).get("abbreviation", pos_key.upper()),
                    "players": athletes,
                }
            )
        depth_chart.append(
            {
                "formation": formation.get("name", ""),
                "positions": positions,
            }
        )
    return depth_chart if depth_chart else [{"message": "No depth chart available"}]


def get_leaders(sport: str) -> list:
    """Get the statistical leaders from the Detroit team's current or most recent game."""
    sport_map = {
        "nfl": ("football", "nfl"),
        "mlb": ("baseball", "mlb"),
        "nhl": ("hockey", "nhl"),
        "nba": ("basketball", "nba"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league = sport_map[sport.lower()]
    game_id = _get_det_game_id(sport_path, league)
    if not game_id:
        return [{"message": "No current game found for Detroit"}]

    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/summary?event={game_id}"
    data = _fetch_espn(url)

    result = []
    for team_leaders in data.get("leaders", []):
        team_name = team_leaders.get("team", {}).get("displayName", "")
        stats = []
        for leader in team_leaders.get("leaders", []):
            top = leader.get("leaders", [{}])[0]
            stats.append(
                {
                    "stat": leader.get("displayName", ""),
                    "player": top.get("athlete", {}).get("displayName", ""),
                    "value": top.get("displayValue", ""),
                }
            )
        result.append({"team": team_name, "leaders": stats})
    return result if result else [{"message": "No leader data available"}]


def get_play_by_play(sport: str) -> list:
    """Get live play-by-play for the Detroit team's current game. Only available during active games."""
    sport_map = {
        "nfl": ("football", "nfl"),
        "mlb": ("baseball", "mlb"),
        "nhl": ("hockey", "nhl"),
        "nba": ("basketball", "nba"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league = sport_map[sport.lower()]
    game_id = _get_det_game_id(sport_path, league)
    if not game_id:
        return [{"message": "No current game found for Detroit"}]

    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/summary?event={game_id}"
    data = _fetch_espn(url)

    plays = data.get("plays", [])
    if not plays:
        return [{"message": "No play-by-play data available (game may not be live yet)"}]

    # Return the last 10 plays
    recent_plays = []
    for play in plays[-10:]:
        recent_plays.append(
            {
                "description": play.get("text", ""),
                "clock": play.get("clock", {}).get("displayValue", ""),
                "period": play.get("period", {}).get("number", ""),
                "score": play.get("homeScore", ""),
            }
        )
    return recent_plays


def get_box_score(sport: str) -> list:
    """Get the box score from the Detroit team's current or most recent game."""
    sport_map = {
        "nfl": ("football", "nfl"),
        "mlb": ("baseball", "mlb"),
        "nhl": ("hockey", "nhl"),
        "nba": ("basketball", "nba"),
    }
    if sport.lower() not in sport_map:
        return [{"error": f"Unknown sport: {sport}"}]

    sport_path, league = sport_map[sport.lower()]
    game_id = _get_det_game_id(sport_path, league)
    if not game_id:
        return [{"message": "No current game found for Detroit"}]

    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/{league}/summary?event={game_id}"
    data = _fetch_espn(url)

    result = []
    for team_data in data.get("boxscore", {}).get("players", []):
        team_name = team_data.get("team", {}).get("displayName", "")
        team_stats = []
        for stat_group in team_data.get("statistics", []):
            stat_names = stat_group.get("names", [])
            for athlete in stat_group.get("athletes", []):
                player_name = athlete.get("athlete", {}).get("displayName", "")
                stats = dict(zip(stat_names, athlete.get("stats", [])))
                team_stats.append({"player": player_name, "stats": stats})
        result.append({"team": team_name, "players": team_stats})
    return result if result else [{"message": "No box score available"}]


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
    {
        "name": "get_transactions",
        "description": "Get recent signings, trades, and cuts for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_depth_chart",
        "description": "Get the depth chart showing starters and backups by position for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_leaders",
        "description": "Get the statistical leaders from the Detroit team's current or most recent game. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_play_by_play",
        "description": "Get live play-by-play for the Detroit team's current game. Only returns data during active games. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "One of: nfl, mlb, nhl, nba"}
            },
            "required": ["sport"],
        },
    },
    {
        "name": "get_box_score",
        "description": "Get the box score from the Detroit team's current or most recent game. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
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
    {
        "type": "function",
        "function": {
            "name": "get_transactions",
            "description": "Get recent signings, trades, and cuts for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
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
            "name": "get_depth_chart",
            "description": "Get the depth chart showing starters and backups by position for a Detroit team. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
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
            "name": "get_leaders",
            "description": "Get the statistical leaders from the Detroit team's current or most recent game. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
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
            "name": "get_play_by_play",
            "description": "Get live play-by-play for the Detroit team's current game. Only returns data during active games. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
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
            "name": "get_box_score",
            "description": "Get the box score from the Detroit team's current or most recent game. Use sport='nfl' for Lions, 'mlb' for Tigers, 'nhl' for Red Wings, 'nba' for Pistons.",
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
