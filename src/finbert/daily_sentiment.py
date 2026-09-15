import sentiment
import pandas as pd

PARQUIET_PATH = ""

df = pd.read_parquet(filepath=PARQUIET_PATH)

r = sentiment.get_sentiment("I love this product! It's amazing.")
print(r)
