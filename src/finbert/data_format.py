import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

base_dir = Path(os.getenv("FNSPID_PATH"))

parquet_paths = [base_dir / "data" / f"train-{i:05d}-of-00048.parquet" for i in range(48)]

dfs = []
for i, path in enumerate(parquet_paths):
    print(i)
    df = pd.read_parquet(path)
    filtered = df.loc[df['Stock_symbol'] == 'AAPL', ['Date', 'Stock_symbol', 'Article']]
    dfs.append(filtered)

new_df = pd.concat(dfs, ignore_index=True)

new_df.sample(10)
new_df.info()

new_df.to_parquet(f"{base_dir}/data/AAPL_articles.parquet", index=False)
