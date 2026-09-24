import sentiment
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import os
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar

load_dotenv()

DATA_DIR = Path(os.getenv("FNSPID_PATH"))
ARTICLES_PATH = DATA_DIR / "data" / "AAPL_articles.parquet"
OUTPUT_PATH = DATA_DIR / "AAPL_article_sentiment.parquet"
print(ARTICLES_PATH)

df = pd.read_parquet(ARTICLES_PATH)

r = sentiment.process_all_articles(df)

df_article = pd.DataFrame(r, index=df.index)
df_article["score"] = df_article["positive"] - df_article["negative"]
df_article.insert(0, "Date", df["Date"])

df_article.to_parquet(OUTPUT_PATH, index=False)