import pandas as pd

parquiet_path = [f"train-{i:05d}-of-00048.parquet" for i in range(48)]

dfs = []
for i, path in enumerate(parquiet_path):
    df = pd.read_parquet(path)
    filtered = df.loc[df['Stock_symbol'] == 'AAPL', ['Date', 'Stock_symbol', 'Article']]
    dfs.append(filtered)

new_df = pd.concat(dfs, ignore_index=True)

new_df.sample(10)
new_df.info()

new_df.to_parquet("AAPL_articles.parquet", index=False)
