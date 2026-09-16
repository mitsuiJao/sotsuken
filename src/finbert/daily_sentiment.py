import sentiment
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

PARQUIET_DIR = Path(os.getenv("FNSPID_PATH")) / "data"

df = pd.read_parquet(filepath=PARQUIET_DIR / "AAPL_articles.parquet")

rows = []
for row in df.itertuples():
    daily_sentiment = sentiment.get_sentiment(row.Article)
    daily = {
        "Date": row.Date,
        **daily_sentiment
    }
    rows.append(daily)

df_daily = pd.DataFrame(rows)
df_daily.to_parquet(PARQUIET_DIR / "daily_sentiment.parquet", index=False)