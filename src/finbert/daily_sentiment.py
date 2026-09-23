import sentiment
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

DATA_DIR = Path(os.getenv("FNSPID_PATH")) / "data"
ARTICLES_PATH = DATA_DIR / "AAPL_articles.parquet"
OUTPUT_PATH = DATA_DIR / "daily_sentiment.parquet"
print(ARTICLES_PATH)

df = pd.read_parquet(ARTICLES_PATH)

r = sentiment.process_all_articles(df)

df_daily = pd.DataFrame(r)
df_daily.to_parquet(OUTPUT_PATH, index=False)