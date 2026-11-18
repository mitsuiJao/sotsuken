import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

load_dotenv()

base_dir = Path(os.getenv("FNSPID_PATH"))
# 使い方: python data_format.py MSFT NVDA V  (省略時は AAPL)
TICKERS = sys.argv[1:] or ["AAPL"]

parquet_paths = [base_dir / "data" / f"train-{i:05d}-of-00048.parquet" for i in range(48)]

dfs = {t: [] for t in TICKERS}
for i, path in enumerate(parquet_paths):
    print(i)
    df = pd.read_parquet(path, columns=['Date', 'Stock_symbol', 'Article'])
    for t in TICKERS:
        dfs[t].append(df.loc[df['Stock_symbol'] == t])

for t in TICKERS:
    new_df = pd.concat(dfs[t], ignore_index=True)
    new_df.info()
    new_df.to_parquet(f"{base_dir}/data/{t}_articles.parquet", index=False)
