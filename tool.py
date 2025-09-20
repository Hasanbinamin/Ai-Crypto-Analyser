from binance.client import Client
import datetime as dt
import time
import csv
import os

# Initialize client (no API keys needed for public endpoints)
client = Client()


def fetch_trades(symbol, start_time, end_time, whale_threshold=100000):
    """Fetch taker trades from Binance and save them to CSV."""
    taker_buy_volume = 0
    taker_sell_volume = 0
    whale_buy_volume = 0
    whale_sell_volume = 0
    all_trades = []
    last_id = None
    total_count = 0

    print(f"Fetching trades for {symbol} from {start_time} to {end_time} ...")

    start_ts = int(start_time.timestamp() * 1000)
    end_ts = int(end_time.timestamp() * 1000)

    while True:
        params = {"symbol": symbol, "limit": 1000}
        if last_id:
            params["fromId"] = last_id + 1
        else:
            params["startTime"] = start_ts
            params["endTime"] = end_ts

        try:
            trades = client.get_aggregate_trades(**params)
        except Exception as e:
            print(f"Error fetching trades: {e}")
            time.sleep(1)
            continue

        if not trades:
            break

        for trade in trades:
            qty = float(trade['q'])
            price = float(trade['p'])
            timestamp = dt.datetime.fromtimestamp(trade['T'] / 1000, dt.timezone.utc)
            trade_value = qty * price 

            if trade['m']:  # Buyer is taker → SELL
                taker_sell_volume += qty
                side = "SELL" 
                if trade_value >= whale_threshold:
                    whale_sell_volume += qty
            else:  # Seller is taker → BUY
                taker_buy_volume += qty
                side = "BUY"
                if trade_value >= whale_threshold:
                    whale_buy_volume += qty

            all_trades.append([timestamp, price, qty, side])
            total_count += 1

        last_id = trades[-1]['a']
        if trades[-1]['T'] > end_ts:
            break

        print(f"Fetched {total_count} trades...", end="\r")
        time.sleep(0.2)

    print(f"\nFinished fetching {total_count} trades.")

    return taker_buy_volume, taker_sell_volume, whale_buy_volume, whale_sell_volume


def get_taker_data(symbol="BTCUSDT", days=0, hours=0, minutes=0, whale_threshold=100000):
    """
    Get taker trade data for a given symbol and timeframe.
    Example:
        - days=1 → last 24 hours
        - hours=6 → last 6 hours
        - minutes=30 → last 30 minutes
    """
    end_time = dt.datetime.now(dt.timezone.utc)
    start_time = end_time - dt.timedelta(days=days, hours=hours, minutes=minutes)

    
    data = fetch_trades(symbol, start_time, end_time, whale_threshold)

    return data


def analyze_sentiment(buy_vol, sell_vol, whale_buy, whale_sell):
    """Calculate sentiment indices for both retail and whales."""
    total_vol = buy_vol + sell_vol
    sentiment_index = (buy_vol - sell_vol) / total_vol if total_vol > 0 else 0

    whale_total = whale_buy + whale_sell
    whale_index = (whale_buy - whale_sell) / whale_total if whale_total > 0 else 0

    return {
        "buy_volume": buy_vol,
        "sell_volume": sell_vol,
        "sentiment_index": sentiment_index,
        "whale_buy_volume": whale_buy,
        "whale_sell_volume": whale_sell,
        "whale_sentiment_index": whale_index,
    }


if __name__ == "__main__":
    # Example usage
    symbol = "LINKUSDT"
    whale_threshold = 100000

    # Fetch last 6 hours
    buy_vol, sell_vol, whale_buy, whale_sell = get_taker_data(symbol, days=1, whale_threshold=whale_threshold)
    results = analyze_sentiment(buy_vol, sell_vol, whale_buy, whale_sell)

    print("\n--- Market Sentiment Report ---")
    print("Buy Volume:", results["buy_volume"])
    print("Sell Volume:", results["sell_volume"])
    print("Sentiment Index:", round(results["sentiment_index"], 3))
    print("\nWhale Buy Volume:", results["whale_buy_volume"])
    print("Whale Sell Volume:", results["whale_sell_volume"])
    print("Whale Sentiment Index:", round(results["whale_sentiment_index"], 3))
