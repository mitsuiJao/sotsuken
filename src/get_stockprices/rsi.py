import pandas as pd
import mplfinance as mpf
import numpy as np

# Open  High  Low  Close  Volume  Dividends  Stock Splits

N = 14

df = pd.read_parquet("./data/stock/AAPL.parquet")
df["diff"] = df["Close"].diff(1)
print(df)

stock = df[["Open", "High", "Low", "Close", "Volume"]].tail(60)

df["gain"] = np.where(df["diff"] > 0, df["diff"], 0)
df["loss"] = np.where(df["diff"] < 0, -df["diff"], 0)
# emw
ave_gain = df["gain"].ewm(alpha=1/N, adjust=False).mean()
ave_loss = df["loss"].ewm(alpha=1/N, adjust=False).mean()
rs = ave_gain / ave_loss
rsi = 100 - (100 / (1 + rs))

rsi_trimmed = rsi.loc[stock.index]

ap = mpf.make_addplot(rsi_trimmed, panel=1, color="blue", ylabel="RSI", ylim=(0, 100))
mpf.plot(stock, type="candle", style="yahoo", volume=False, addplot=ap, savefig="./data/chart/aapl_chart.png")