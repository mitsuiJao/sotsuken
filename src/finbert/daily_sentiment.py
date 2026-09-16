import sentiment
import pandas as pd

PARQUIET_PATH = ""

df = pd.read_parquet(filepath=PARQUIET_PATH)

rows = []
for row in df.itertuples():
    daily_sentiment = sentiment.get_sentiment(row.Article)
    daily = {
        "Date": row.Date,
        **daily_sentiment
    }
    rows.append(daily)

df_daily = pd.DataFrame(rows)

df_daily.to_parquet("daily_sentiment.parquet", index=False)
