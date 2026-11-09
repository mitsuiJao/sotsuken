import pandas as pd
import numpy as np
from pathlib import Path
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt


load_dotenv()

STOCK_PATH = Path(os.getenv("STOCK_PATH"))
SENTIMENT_PATH = Path(os.getenv("SENTIMENT_PATH"))

df_sto = pd.read_parquet(STOCK_PATH / "AAPL.parquet")
df_sent = pd.read_parquet(SENTIMENT_PATH / "AAPL_daily_sentiment.parquet")
df_sent = df_sent.set_index(pd.DatetimeIndex(df_sent["trade_date"]).tz_localize(df_sto.index.tz))


def divergence(df_sto, df_sent, n=5, m=120):
    p = np.log(df_sto["Close"]).diff(n)
    s = df_sent["sent"].rolling(n, min_periods=3).mean()
    z = lambda x: (x - x.rolling(m).mean().shift(1)) / x.rolling(m).std().shift(1)
    # 株価側は全期間で z 化してからセンチメントの日付に合わせる
    df = pd.DataFrame({"z_sent": z(s), "z_price": z(p).reindex(s.index)})
    df["divergence"] = df["z_sent"] - df["z_price"]
    return df


div = divergence(df_sto, df_sent, n=5, m=120)
div.to_parquet(Path(__file__).resolve().parents[2] / "data" / "divergence.parquet")


# グラフ
CHART_PATH = Path(__file__).resolve().parents[2] / "data" / "chart" / "aapl_divergence_chart.png"
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#8a8984"

plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 14})

d = div.dropna()
close = df_sto["Close"].reindex(d.index)

fig, axes = plt.subplots(3, 1, figsize=(16, 10), sharex=True, gridspec_kw={"height_ratios": [2, 2, 2]})

# 株価
axes[0].plot(d.index, close, color=INK, linewidth=1.5)
axes[0].set_ylabel("株価 (USD)")

# センチメントと株価リターンの z スコア
axes[1].plot(d.index, d["z_sent"], color=BLUE, linewidth=2, label="センチメント (z)")
axes[1].plot(d.index, d["z_price"], color=ORANGE, linewidth=2, label="株価5日リターン (z)")
axes[1].axhline(0, color=MUTED, linewidth=0.8)
axes[1].set_ylabel("z スコア")
axes[1].legend(loc="upper left", frameon=False)

# 乖離: 正ならセンチメントが株価より強気
colors = np.where(d["divergence"] >= 0, BLUE, ORANGE)
axes[2].bar(d.index, d["divergence"], width=1.0, color=colors)
axes[2].axhline(0, color=MUTED, linewidth=0.8)
for y in (2, -2):
    axes[2].axhline(y, color=MUTED, linewidth=0.8, linestyle="--")
axes[2].set_ylabel("乖離 (z差)")
axes[2].text(0.01, 0.95, "青: センチメント > 株価　橙: 株価 > センチメント", transform=axes[2].transAxes, va="top", color=INK)

for ax in axes:
    ax.grid(axis="y", color="#e5e4df", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
fig.savefig(CHART_PATH, dpi=100)

