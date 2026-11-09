import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt


load_dotenv()

plt.rcParams["font.family"] = "Noto Sans CJK JP"

STOCK_PATH = Path(os.getenv("STOCK_PATH"))
SENTIMENT_PATH = Path(os.getenv("SENTIMENT_PATH"))
CHART_PATH = Path(os.getenv("CHART_PATH"))

df_sto = pd.read_parquet(STOCK_PATH / "AAPL.parquet")
df_sent = pd.read_parquet(SENTIMENT_PATH / "AAPL_daily_sentiment.parquet")

# corrはインデックスで突き合わせるので、両方をtzなしの日付に揃える
df_sto.index = df_sto.index.tz_localize(None).normalize()
df_sent = df_sent.set_index("trade_date")

def rolling_lag_corr(S, r, w=60, taus=range(-10, 11)):
    out = {}
    for tau in taus:
        # corr(S_t, r_{t+tau}) → rを-tau方向にずらす
        out[tau] = S.rolling(w, min_periods=int(w*0.8)).corr(r.shift(-tau))
    return pd.DataFrame(out)

# rc = rolling_lag_corr(df_sent["sent"], df_sto["logreturn"])

# print(rc)

# 全期間のρ(τ)
full = {tau: df_sent["sent"].corr(df_sto["logreturn"].shift(-tau)) for tau in range(-10, 11)}

full = pd.Series(full)
print(full)
fig, ax = plt.subplots()
full.plot(kind="bar", ax=ax, rot=0)
ax.axhline(0, color="gray", lw=0.5)
ax.set_xlabel("k")
ax.set_ylabel("相関係数")
fig.tight_layout()
# ax.set_title("センチメントと日次リターンのラグ相関（AAPL）")
# plt.savefig(CHART_PATH / "aapl_lag_titled.png")
plt.savefig(CHART_PATH / "aapl_lag.png")
plt.close()


fig, ax = plt.subplots()
for w in [20, 60, 120]:
    rc = rolling_lag_corr(df_sent["sent"], df_sto["logreturn"], w=w)
    rc[0].plot(ax=ax, label=f"w={w}")
ax.axhline(0, color="gray", lw=0.5)
ax.legend()
ax.set_xlabel("日付")
ax.set_ylabel("相関係数")
fig.tight_layout()
# タイトルあり版: 下2行のコメントを外し、その下のsavefigをコメントアウト
# ax.set_title("センチメントと日次リターンの窓相関（k=0, AAPL）")
# plt.savefig(CHART_PATH / "aapl_rolling_tau0_titled.png")
plt.savefig(CHART_PATH / "aapl_rolling_tau0.png")
plt.close()