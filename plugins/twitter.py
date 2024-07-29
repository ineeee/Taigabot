import re
from datetime import datetime, timedelta, UTC

from util import hook
from utilities.request import get_json

TWITTER_SCRAPER_API = "https://tweet-reader.onrender.com"
TWEET_RE = (r"https?://(twitter|x).com/([-_a-zA-Z0-9]+)/status/(\d+)", re.I)
PROFILE_RE = (r"https?://(twitter|x).com/([-_a-zA-Z0-9]+)(?=$|/[^s])", re.I)
CHAR_LIMIT = 340


def get_tweet(id):
    data = get_json(TWITTER_SCRAPER_API + "/get_tweet/" + id)

    if data["status"] != "success":
        return "api error"

    user_handle = data["user"]["screen_name"]
    user_name = data["user"]["name"]
    text = data.get("text", "").replace("\n", "  ")
    date_str = data["created_at"]

    # Parsing the tweet date
    tweet_date = datetime.strptime(date_str, "%a %b %d %H:%M:%S +0000 %Y").replace(
        tzinfo=UTC
    )
    now = datetime.now(UTC)
    print(now)
    delta = now - tweet_date

    if delta > timedelta(weeks=1):
        formatted_date = tweet_date.strftime("%Y-%m-%d")
    else:
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        if days > 0:
            formatted_date = f"{days}d {hours}h ago"
        elif hours > 0:
            formatted_date = f"{hours}h {minutes}m ago"
        else:
            formatted_date = f"{minutes}m ago"

    if data["favorite_count"] == 0 and data["retweet_count"] == 0:
        stats = f"{formatted_date}"
    else:
        stats = f"{formatted_date}, ❤ {data['favorite_count']:,}, ↻ {data['retweet_count']:,}"

    if len(text) > CHAR_LIMIT:
        text = text[:CHAR_LIMIT] + "..."

    return f"@\x02{user_handle}\x02 ({user_name}): {text} ({stats})"


def get_profile(id):
    data = get_json(TWITTER_SCRAPER_API + "/get_user/" + id)

    if data["status"] != "success":
        return "api error"

    user_handle = data["screen_name"]
    user_name = data["name"]
    desc = data.get("description", "").replace("\n", "  ")

    if len(desc) > CHAR_LIMIT:
        desc = desc[:CHAR_LIMIT] + "..."

    return f"@\x02{user_handle}\x02 ({user_name}) {desc}"


@hook.regex(*TWEET_RE)
def tweet_url(match):
    # url_user = match.group(2)
    url_id = match.group(3)

    output = get_tweet(url_id)
    return f"[Twitter] {output}"


@hook.regex(*PROFILE_RE)
def profile_url(match):
    url_user = match.group(2)

    output = get_profile(url_user)
    return f"[Twitter] {output}"


@hook.command("tw")
@hook.command("twatter")
@hook.command("twinfo")
@hook.command("twuser")
@hook.command
def twitter(inp):
    """twitter <user> -- Gets profile name and description on <user>."""
    output = get_profile(inp)
    return f"[Twitter] {output}"
