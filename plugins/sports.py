from util import hook
from utilities import request

NFL_REALTIME_API = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
NBA_REALTIME_API = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
MLB_REALTIME_API = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
NHL_REALTIME_API = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
CFB_REALTIME_API = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"

headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}


def format_sports_event(api_url, event):
    """Format information about sports event"""

    match_info = []
    competition = event["competitions"][0]

    # Get score
    competitors = competition["competitors"]
    match_result = ""
    id_to_abbr = dict()
    for competitor in competitors:
        abbreviation = competitor["team"]["abbreviation"]
        id = competitor["team"]["id"]
        id_to_abbr[id] = abbreviation
        match_result += abbreviation + " " + competitor["score"] + " "

    # Remove white space end of string
    match_result = match_result[:-1]
    match_info.append(match_result)
    time_detail = competition["status"]["type"]["shortDetail"]
    match_info.append(time_detail)

    # Sport-specific logic
    if api_url == NFL_REALTIME_API:
        try:
            pos_team_id = competition["situation"]["lastPlay"]["team"]["id"]
            pos_team = id_to_abbr[pos_team_id]
            down_distance = pos_team + ": " + competition["situation"]["downDistanceText"]
            match_info.append(down_distance)
        except:
            pass

    elif api_url == MLB_REALTIME_API:
        try:
            situation = competition["situation"]

            pitching_team_id = situation["pitcher"]["athlete"]["team"]["id"]
            pitching_team = id_to_abbr[pitching_team_id]

            batting_team_id = situation["batter"]["athlete"]["team"]["id"]
            batting_team = id_to_abbr[batting_team_id]

            pitcher = situation["pitcher"]["athlete"]["shortName"]
            pitcher_summary = situation["pitcher"]["summary"]

            batter = situation["batter"]["athlete"]["shortName"]
            batter_summary = situation["batter"]["summary"]

            now_at_bat = (
                f"[{pitching_team}] {pitcher} ({pitcher_summary}) vs. [{batting_team}] {batter} ({batter_summary})"
            )
            match_info.append(now_at_bat)
        except:
            pass

        try:
            situation = competition["situation"]
            on_base = f"1B: {situation['onFirst']}, 2B: {situation['onSecond']}, 3B: {situation['onThird']}"
            match_info.append(on_base)
        except:
            pass

        try:
            situation = competition["situation"]
            balls_strikes_outs = (
                f"Balls: {situation['balls']}, Strikes: {situation['strikes']}, Outs: {situation['outs']}"
            )
            match_info.append(balls_strikes_outs)
        except:
            pass

    try:
        last_play_info = ""
        last_play_info = competition["situation"]["lastPlay"]["text"]
        match_info.append(last_play_info)
    except:
        pass

    return " | ".join(match_info)


def fetcher(api_url, inp):
    """Fetches data for either specific team or the entire sportsd league"""

    data = request.get_json(api_url, headers=headers)
    events = data["events"]

    schedule = []

    # Specific match
    if inp:
        team = inp.upper()
        for event in events:
            competitors = event["competitions"][0]["competitors"]
            for competitor in competitors:
                if competitor["team"]["abbreviation"] == team:
                    return format_sports_event(api_url, event)

    # League summary
    for event in events:
        match_result = ""
        competitors = event["competitions"][0]["competitors"]

        for competitor in competitors:
            match_result += competitor["team"]["abbreviation"] + " " + competitor["score"] + " "

        # Remove white space end of string
        match_result = match_result[:-1]
        schedule.append(match_result)

    # Build entire schedule
    return " | ".join(schedule)


@hook.command(autohelp=False)
def nfl(inp):
    """nfl [team abbreviation] -- Returns all matchups for current week, or only for a specified team's matchup"""
    return fetcher(NFL_REALTIME_API, inp)


@hook.command(autohelp=False)
def nba(inp):
    """nba [team abbreviation] -- Returns all matchups for current week, or only for a specified team's matchup"""
    return fetcher(NBA_REALTIME_API, inp)


@hook.command(autohelp=False)
def mlb(inp):
    """mlb [team abbreviation] -- Returns all matchups for current week, or only for a specified team's matchup"""
    return fetcher(MLB_REALTIME_API, inp)


@hook.command(autohelp=False)
def nhl(inp):
    """nhl [team abbreviation] -- Returns all matchups for current week, or only for a specified team's matchup"""
    return fetcher(NHL_REALTIME_API, inp)


@hook.command(autohelp=False)
def cfb(inp):
    """cfb [team abbreviation] -- Returns all matchups for current week, or only for a specified team's matchup"""
    return fetcher(CFB_REALTIME_API, inp)
