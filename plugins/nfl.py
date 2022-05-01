from util import hook
from utilities import request

NFL_REALTIME_API = (
    "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
)

h = {"Cache-Control": "no-cache", "Pragma": "no-cache"}

def helper(event):
    thing = []
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
    thing.append(match_result)
    time_detail = competition["status"]["type"]["shortDetail"]
    thing.append(time_detail)

    # Down distance
    down_distance = ""
    try:
        pos_team_id = competition["situation"]["lastPlay"]["team"]["id"]
        pos_team = id_to_abbr[pos_team_id]
        down_distance = pos_team + ": " + competition["situation"]["downDistanceText"]
        thing.append(down_distance)
    except:
        pass

    # Last play info
    last_play_info = ""
    try:
        last_play_info = competition["situation"]["lastPlay"]["text"]
        thing.append(last_play_info)
    except:
        pass

    return " | ".join(thing)

@hook.command(autohelp=False)
def nfl(inp):
    """nfl | nfl <team abbreviation> -- Returns all matchups for current week, or only for a specified team's matchup
    """
    data = request.get_json(NFL_REALTIME_API, headers=h)
    events = data["events"]

    schedule = []

    # Specific match
    if inp:
        team = inp.upper()
        for event in events:
            competitors = event["competitions"][0]["competitors"]
            for competitor in competitors:
                if competitor["team"]["abbreviation"] == team:
                    return helper(event)

    # League summary
    for event in events:
        match_result = ""
        competitors = event["competitions"][0]["competitors"]

        for competitor in competitors:
            match_result += (
                competitor["team"]["abbreviation"] + " " + competitor["score"] + " "
            )

        # Remove white space end of string
        match_result = match_result[:-1]
        schedule.append(match_result)

    # Build entire schedule
    return(" | ".join(schedule))
