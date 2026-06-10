import yfinance as yf
import pandas as pd
import pandas_ta as ta

# データ取得
# df = yf.download("AAPL", start="2018-01-01", end="2024-12-31")
df = pd.read_parquet("./data/stock/AAPL.parquet")
print(df.head())
df = df[(df.index >= "2018-01-01") & (df.index <= "2024-12-31")]

# 変化率
df["ret_1d"]    = df["Close"].pct_change()
df["ret_5d"]    = df["Close"].pct_change(5)
df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()

# rsi
df["rsi"] = ta.rsi(df["Close"], length=14)

# macd
macd = ta.macd(df["Close"], fast=12, slow=26, signal=9)
df["macd"]        = macd["MACD_12_26_9"]
df["macd_signal"] = macd["MACDs_12_26_9"]
df["macd_hist"]   = macd["MACDh_12_26_9"]

# 乖離率
df["ma20_dev"] = (df["Close"] - df["Close"].rolling(20).mean()) / df["Close"].rolling(20).mean()
df["ma60_dev"] = (df["Close"] - df["Close"].rolling(60).mean()) / df["Close"].rolling(60).mean()

# target 明日 > 今日: 1
df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

# nan消去、 inplace破壊的置換
df.dropna(inplace=True)

print(df[["Close", "rsi", "macd", "target"]].tail(10))
print(f"\nデータ件数: {len(df)}")
print(f"正例(上昇)の割合: {df['target'].mean():.3f}")