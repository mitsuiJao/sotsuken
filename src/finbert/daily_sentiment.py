import sentiment
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

PARQUIET_DIR = Path(os.getenv("FNSPID_PATH")) / "data" / "AAPL_articles.parquet"
print(PARQUIET_DIR)

df = pd.read_parquet(PARQUIET_DIR)

rows = []
for row in df.itertuples():
    daily_sentiment = sentiment.get_sentiment(row.Article)
    daily = {
        "Date": row.Date,
        **daily_sentiment
    }
    rows.append(daily)
    print(row.Date, f"{len(rows)/len(df)*100:.2f}%")

df_daily = pd.DataFrame(rows)
df_daily.to_parquet(PARQUIET_DIR / "daily_sentiment.parquet", index=False)