from util import hook
from utilities import request
from utilities import services
from bs4 import BeautifulSoup

MAX_NUM_URLS_DISPLAYED = 3
MAX_NUM_URLS_FETCHED = 20


def extract_text_from_html(element):
    soup = BeautifulSoup(element, 'html.parser')

    # Loop through line break tags
    for line_break in soup.find_all('br'):
        # Replace tags with new line delimiter
        line_break.replace_with('\n')

    # Get list of strings
    strings = soup.get_text().split('\n')

    return "\n".join([string for string in strings if string])


@hook.command("4chan")
@hook.command
def catalog(inp):
    """catalog <board> <regex> -- Search all OP posts on the catalog of a board, and return matching results"""

    inp = inp.split(" ")
    board = inp[0]
    user_query = (" ".join(inp[1:])).strip()

    catalog_json_url = f"https://a.4cdn.org/{board}/catalog.json"

    try:
        catalog_json = request.get_json(catalog_json_url)
    except Exception as e:
        return f"[4chan] Error fetching catalog"

    # Store the search specifics in a dictionary
    results = []

    # Iterate through each page in the catalog
    for page in catalog_json:
        # Iterate through each thread on the page
        thread_list = page["threads"]
        for thread in thread_list:
            # List of all relevant fields to search
            # https://github.com/4chan/4chan-API/blob/master/pages/Catalog.md
            sections = ["com", "name", "trip", "email", "sub", "filename"]

            # Get relevant fields from thread
            relevant_fields = {key: thread.get(key, "") for key in sections}

            # Search the relevant fields user query (case insensitive)
            query_in_relevant_fields = any(user_query.lower() in s.lower() for s in relevant_fields.values())

            # If the query is in any of the relevant fields, add the thread to the results
            if query_in_relevant_fields:
                results.append(thread)

            # If we have enough results, return them
            if len(results) >= MAX_NUM_URLS_FETCHED:
                break

    if len(results) == 0:
        return f"No results on /{board}/ for {user_query}"

    # Upload to pastebin if there are too many results
    if len(results) > MAX_NUM_URLS_DISPLAYED:
        # Create HTML formatted results to upload to taiga.link
        html_formatted_results = []

        for thread in results:
            url = f"https://boards.4chan.org/{board}/thread/{thread['no']}"
            subject = thread.get("sub", "(No subject)")
            comment = thread.get("com", "")

            html_formatted_results.append(f"<h2>{subject}</h2><a href={url}>{url}</a>\n{comment}\n")

        return services.paste_taigalink(
            "\n".join(html_formatted_results), title=f"4chan {board} search results for {user_query}", format="html"
        )

    # Otherwise, return the results as a message to IRC
    irc_results = []
    for thread in results:
        max_chars = 100
        url = f"https://boards.4chan.org/{board}/thread/{thread['no']}"
        subject = extract_text_from_html(thread.get("sub", ""))[:max_chars]
        comment = extract_text_from_html(thread.get("com", ""))[:max_chars]

        irc_results.append(f"{url} \x02{subject}\x02 {comment}")

    return " ".join(irc_results)


@hook.command(autohelp=False)
def bs(inp):
    """bs -- Returns current battlestation threads on /g/"""
    return catalog("g battlestation")


@hook.command(autohelp=False)
def desktops(inp):
    """desktop -- Returns current desktop threads on /g/"""
    return catalog("g desktop thread")


@hook.command(autohelp=False)
def britbong(inp):
    """britbong -- find latest britbong thread on /pol/"""
    return catalog("pol britbong")
