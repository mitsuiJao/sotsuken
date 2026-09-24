import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import pandas_market_calendars as mcal

load_dotenv()

DATA_DIR = Path(os.getenv("FNSPID_PATH"))
ARTICLES_SENTIMENT_PATH = DATA_DIR / "AAPL_article_sentiment.parquet"
OUTPUT_PATH = DATA_DIR / "AAPL_daily_sentiment.parquet"

df = pd.read_parquet(ARTICLES_SENTIMENT_PATH)


ts = pd.to_datetime(df["Date"], utc=True)

nasdaq = mcal.get_calendar("NASDAQ")
sched = nasdaq.schedule(
    start_date=ts.min().date() - pd.Timedelta(days=7),
    end_date=ts.max().date() + pd.Timedelta(days=7),
)
closes = sched["market_close"]

idx = closes.searchsorted(ts, side="right")
valid = idx < len(closes)
df = df[valid].copy()
df["trade_date"] = sched.index[idx[valid]]

df_daily = (
    df.groupby(["trade_date"])
    .agg(sent=("score", "mean"), neu=("neutral", "mean"), n_news=("score", "count"))
    .reset_index()
)

print(df_daily)

df.to_parquet(OUTPUT_PATH, index=False)


