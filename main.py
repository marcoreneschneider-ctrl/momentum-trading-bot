import os
import requests
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

NUM_STOCKS_TO_TRADE = 3
SHARES_PER_STOCK = 2


def fetch_top_momentum_stocks():
    print("Step 1: Fetching top gainers from Alpha Vantage...")
    url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={ALPHA_VANTAGE_API_KEY}"

    response = requests.get(url)
    data = response.json()

    tradeable_tickers = []

    if "top_gainers" in data:
        for stock in data["top_gainers"]:
            ticker = stock["ticker"]

            if ticker.endswith("W") or "^" in ticker:
                continue

            tradeable_tickers.append(ticker)

            if len(tradeable_tickers) == NUM_STOCKS_TO_TRADE:
                break

        print(f"-> Selected Tradeable Tickers: {tradeable_tickers}\n")
        return tradeable_tickers
    else:
        print("-> Error fetching Alpha Vantage data:", data)
        return []


def execute_alpaca_trades(tickers):
    if not tickers:
        print("No valid tickers found to trade.")
        return

    print("Step 2: Connecting to Alpaca Paper Trading...")
    trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

    account = trading_client.get_account()
    print(f"-> Connected! Available Cash: ${float(account.cash):,.2f}\n")

    print("Step 3: Executing market buy orders...")
    for ticker in tickers:
        try:
            order_data = MarketOrderRequest(
                symbol=ticker,
                qty=SHARES_PER_STOCK,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
            )

            submitted_order = trading_client.submit_order(order_data)
            print(
                f"   [SUCCESS] Bought {SHARES_PER_STOCK} share(s) of {ticker} |"
                f" Order ID: {submitted_order.id}"
            )
        except Exception as e:
            print(f"   [SKIPPED/FAILED] Could not trade {ticker}: {e}")


if __name__ == "__main__":
    if not all([ALPHA_VANTAGE_API_KEY, ALPACA_API_KEY, ALPACA_SECRET_KEY]):
        print("Errore: Chiavi API non trovate. Configura il file .env")
    else:
        tickers_to_buy = fetch_top_momentum_stocks()
        execute_alpaca_trades(tickers_to_buy)