from util import hook
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}


def color(change):
    if change < 0:
        # Orange
        return "05"
    else:
        # Green
        return "03"


# Get list of possible tickers user could be referencing
def ticker_search(query):
    url = "https://query2.finance.yahoo.com/v1/finance/search?q=" + query
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


@hook.command
def stock(inp, bot):
    """stock <symbol> -- gets stock information"""
    inputed_symbol = inp
    base_url = "https://query2.finance.yahoo.com/v6/finance/quoteSummary/"

    # Validate ticker
    query_url = (
        base_url
        + inputed_symbol
        + "?modules=financialData&modules=quoteType&modules=defaultKeyStatistics&modules=assetProfile&modules=summaryDetail&modules=price&ssl=true"
    )
    r = requests.get(query_url, headers=headers)
    data = r.json()

    # Ticker might not exist
    # Or, it might be some inactive ticker in which case we want to search the term instead
    if data["quoteSummary"]["error"] or "summaryDetail" not in data["quoteSummary"]["result"][0]:
        # Call function that searches for ticker
        ticker_search_data = ticker_search(inputed_symbol)

        # If no quotes, return
        if not ticker_search_data["quotes"]:
            return "[Stock] No quotes found for " + inputed_symbol
        else:
            # Create list of possible tickers
            possible_tickers = []
            for quote in ticker_search_data["quotes"]:
                possible_tickers.append(
                    quote["exchDisp"] + ": " + quote["shortname"] + " (\x02" + quote["symbol"] + "\x02)"
                )
            # Return list of possible tickers
            return "[Stock] Possible tickers: " + ", ".join(possible_tickers)

    try:
        shortName = data["quoteSummary"]["result"][0]["quoteType"]["shortName"]
        symbol = data["quoteSummary"]["result"][0]["quoteType"]["symbol"]
        currencySymbol = data["quoteSummary"]["result"][0]["price"]["currencySymbol"]
        price = data["quoteSummary"]["result"][0]["price"]["regularMarketPrice"]["raw"]
        changePercent = data["quoteSummary"]["result"][0]["price"]["regularMarketChangePercent"]["raw"]
        fiftyTwoWeekLow = data["quoteSummary"]["result"][0]["summaryDetail"]["fiftyTwoWeekLow"]["raw"]
        fiftyTwoWeekHigh = data["quoteSummary"]["result"][0]["summaryDetail"]["fiftyTwoWeekHigh"]["raw"]
    except Exception as e:
        print(e)
        return "[Stock] Error parsing data"

    # Round change percent two 2 decimal places
    changePercentRounded = round(changePercent, 2)
    marketCapFormatted = data["quoteSummary"]["result"][0]["price"]["marketCap"].get("fmt")
    if marketCapFormatted:
        marketCapFormatted = f"{currencySymbol}{marketCapFormatted}"
    else:
        marketCapFormatted = "N/A"

    # Redo output in f-string
    stock_info = f"{shortName} (\x02{symbol}\x02), Current: \x0307{currencySymbol}{price}\x03, 24h: \x03{color(changePercentRounded)}{changePercentRounded}%\x03, 52-wk range: {currencySymbol}{fiftyTwoWeekLow} - {currencySymbol}{fiftyTwoWeekHigh}, Cap: {marketCapFormatted}"
    return "[Stock] " + stock_info
