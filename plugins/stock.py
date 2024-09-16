from util import hook
import requests
from datetime import datetime, timedelta

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}


def color(change):
    if change < 0:
        # Orange
        return "05"
    else:
        # Green
        return "03"


def price_change(current_price, historical_price):
    if historical_price is None:
        return False
    return round((current_price - historical_price) / historical_price * 100, 2)


def find_historical_price(market_datetime, days, timestamp, close_prices):
    historical_datetime = market_datetime - timedelta(days=days)
    historical_timestamp = historical_datetime.timestamp()
    closest_timestamp = min(timestamp, key=lambda x: abs(x - historical_timestamp))
    historical_price = close_prices[timestamp.index(closest_timestamp)]
    return historical_price


def get_currency_symbol(currency):
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CHF": "₣",
        "CAD": "C$",
        "AUD": "A$",
        "HKD": "HK$",
        "CNY": "¥",
        "SGD": "S$",
    }
    return currency_symbols.get(currency, currency)


def ticker_search(query):
    url = "https://query2.finance.yahoo.com/v1/finance/search?q=" + query
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


@hook.command
def stock(inp, bot):
    """stock <symbol> -- gets stock information"""
    inputed_symbol = inp
    base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"

    # Validate ticker
    query_url = base_url + inputed_symbol + "?range=1y&interval=1d"
    r = requests.get(query_url, headers=headers)
    data = r.json()

    # Ticker might not exist
    # Or, it might be some inactive ticker in which case we want to search the term instead
    if data["chart"]["error"]:
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
                    quote["exchDisp"]
                    + ": "
                    + quote["shortname"]
                    + " (\x02"
                    + quote["symbol"]
                    + "\x02)"
                )
            # Return list of possible tickers
            return "[Stock] Possible tickers: " + ", ".join(possible_tickers)

    try:
        # Extract the relevant values
        symbol = data["chart"]["result"][0]["meta"]["symbol"]
        currency = data["chart"]["result"][0]["meta"]["currency"]
        regular_market_price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        market_time = data["chart"]["result"][0]["meta"]["regularMarketTime"]
        chart_previous_close = data["chart"]["result"][0]["meta"]["chartPreviousClose"]
        regular_market_volume = data["chart"]["result"][0]["meta"][
            "regularMarketVolume"
        ]
        timestamp = data["chart"]["result"][0]["timestamp"]
        close_prices = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]

        # Fetch the company name
        ticker_search_data = ticker_search(symbol)
        company_name = next(
            (
                quote["shortname"]
                for quote in ticker_search_data["quotes"]
                if quote["symbol"] == symbol
            ),
            symbol,
        )

    except Exception as e:
        print(e)
        return "[Stock] Error parsing data"

    # Convert regularMarketTime to a datetime object
    market_datetime = datetime.fromtimestamp(market_time)

    # Calculate the price changes for different time periods
    price_change_24h = price_change(
        regular_market_price,
        find_historical_price(market_datetime, 1, timestamp, close_prices),
    )
    price_change_7d = price_change(
        regular_market_price,
        find_historical_price(market_datetime, 7, timestamp, close_prices),
    )
    price_change_30d = price_change(
        regular_market_price,
        find_historical_price(market_datetime, 30, timestamp, close_prices),
    )
    price_change_6m = price_change(
        regular_market_price,
        find_historical_price(market_datetime, 180, timestamp, close_prices),
    )
    price_change_1y = price_change(
        regular_market_price,
        find_historical_price(market_datetime, 365, timestamp, close_prices),
    )

    # Format the market cap
    market_cap = "{:,.0f}".format(regular_market_price * regular_market_volume)

    # Get the currency symbol
    currency_symbol = get_currency_symbol(currency)

    # Create the stock info string
    stock_info = f"{company_name} (\x02{symbol}\x02), Current: \x0307{currency_symbol}{regular_market_price}\x03, "
    stock_info += f"24h: \x03{color(price_change_24h)}{'+' if price_change_24h > 0 else ''}{price_change_24h}%\x03, "
    stock_info += f"7d: \x03{color(price_change_7d)}{'+' if price_change_7d > 0 else ''}{price_change_7d}%\x03, "
    stock_info += f"30d: \x03{color(price_change_30d)}{'+' if price_change_30d > 0 else ''}{price_change_30d}%\x03, "
    stock_info += f"6m: \x03{color(price_change_6m)}{'+' if price_change_6m > 0 else ''}{price_change_6m}%\x03, "
    stock_info += f"1y: \x03{color(price_change_1y)}{'+' if price_change_1y > 0 else ''}{price_change_1y}%\x03"

    return "[Stock] " + stock_info
