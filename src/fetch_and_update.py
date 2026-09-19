# src/fetch_and_update.py
import os
import sys
from datetime import datetime, timedelta, timezone
import pandas as pd

try:
    from kiteconnect import KiteConnect
except Exception as e:
    print("kiteconnect not installed. Install with: pip install kiteconnect")
    raise

TEMPLATE_PATH = "src/index.template.html"
OUTPUT_PATH = "src/index.html"

def get_prev_month_range(now=None):
    if now is None:
        now = datetime.now()
    first_of_this_month = datetime(now.year, now.month, 1)
    last_of_prev_month = first_of_this_month - timedelta(days=1)
    first_of_prev_month = datetime(last_of_prev_month.year, last_of_prev_month.month, 1)
    # return naive datetimes (local) for comparison
    return first_of_prev_month, datetime(last_of_prev_month.year, last_of_prev_month.month, last_of_prev_month.day, 23, 59, 59)

def fetch_trades(kite):
    # kite.trades() returns a list of trade dicts
    trades = kite.trades()
    return trades

def parse_trade_timestamp(trade):
    # Kite trade dicts may have 'trade_timestamp' or 'order_timestamp'
    for key in ("trade_timestamp", "order_timestamp", "timestamp"):
        if key in trade and trade[key]:
            try:
                # Example format: "2023-09-15 09:15:00"
                return pd.to_datetime(trade[key])
            except Exception:
                pass
    # fallback: try created_at or executed_at
    for key in ("created_at", "executed_at"):
        if key in trade and trade[key]:
            try:
                return pd.to_datetime(trade[key])
            except Exception:
                pass
    return None

def count_trades_last_month(trades):
    start, end = get_prev_month_range()
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    timestamps = []
    for t in trades:
        ts = parse_trade_timestamp(t)
        if ts is not None:
            timestamps.append(ts)
    if not timestamps:
        return 0
    s = pd.Series(timestamps)
    mask = (s >= start) & (s <= end)
    return int(mask.sum())

def render_template(count):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tpl = f.read()
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    out = tpl.replace("<!--TRADES_COUNT-->", str(count)).replace("<!--UPDATED_AT-->", updated_at)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote {OUTPUT_PATH} with count={count}")

def main():
    API_KEY = os.environ.get("KITE_API_KEY")
    ACCESS_TOKEN = os.environ.get("KITE_ACCESS_TOKEN")
    trades = kite.trades()
    if not API_KEY or not ACCESS_TOKEN:
        print("Missing KITE_API_KEY or KITE_ACCESS_TOKEN environment variables.")
        sys.exit(2)

    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(ACCESS_TOKEN)

    trades = fetch_trades(kite)
    count = count_trades_last_month(trades)
    render_template(count)
    # exit 0 so workflow can commit changes
    return 0

if __name__ == "__main__":
    sys.exit(main())
