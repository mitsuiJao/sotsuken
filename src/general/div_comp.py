import os
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

STOCK_PATH = Path(os.getenv("STOCK_PATH"))
SENTIMENT_PATH = Path(os.getenv("SENTIMENT_PATH"))

N = 5          # 短期窓 (n日リターン / n日平均センチメント)
M = 120        # 標準化・順位計算の窓
K = 20         # 「水準」の基準にする移動平均の窓
HORIZONS = (1, 3, 5)  # 将来リターンを見る日数

df_sto = pd.read_parquet(STOCK_PATH / "AAPL.parquet")
df_sent = pd.read_parquet(SENTIMENT_PATH / "AAPL_daily_sentiment.parquet")
df_sent = df_sent.set_index(pd.DatetimeIndex(df_sent["trade_date"]).tz_localize(df_sto.index.tz))

close = df_sto["Close"]
# センチメントを株価の営業日に揃える (ニュースのない日は NaN)
# → 価格側もセンチメント側も「営業日 n 行」で窓が揃う
sent = df_sent["sent"].reindex(close.index)


MIN_FRAC = 0.8  # 窓内の有効日が m の 80% 以上なら計算する (ニュース欠損日の許容)


def z(x, m=M):
    """過去 m 日 (当日を除く) の平均・標準偏差で標準化"""
    mp = int(m * MIN_FRAC)
    r = x.rolling(m, min_periods=mp)
    return (x - r.mean().shift(1)) / r.std().shift(1)


def pct(x, m=M):
    """過去 m 日 (当日を除く) の中での当日値の順位 (0〜1)。NaN は無視"""
    mp = int(m * MIN_FRAC)

    def f(w):
        past, cur = w[:-1], w[-1]
        past = past[~np.isnan(past)]
        if np.isnan(cur) or len(past) < mp:
            return np.nan
        return (past < cur).mean()

    return x.rolling(m + 1, min_periods=1).apply(f, raw=True)


ret_n = np.log(close).diff(N)                       # 価格: n日リターン (変化量)
s_n = sent.rolling(N, min_periods=3).mean()          # センチメント: n日平均 (水準)

# 各方式の (センチメント側, 価格側)。乖離 D = センチメント側 − 価格側
sides = {
    "A 現行(水準z − リターンz)": (z(s_n), z(ret_n)),
    "B 変化量同士": (z(s_n - s_n.shift(N)), z(ret_n)),
    "C 水準同士": (
        z(s_n - s_n.rolling(K, min_periods=K // 2).mean()),
        z(np.log(close) - np.log(close.rolling(K).mean())),
    ),
    "D 順位差(Aの入力を順位化)": (pct(s_n), pct(ret_n)),
}

# 全方式で共通の有効日だけ使って公平に比較
frame = pd.concat(
    {k: pd.DataFrame({"xs": a, "xp": b}) for k, (a, b) in sides.items()}, axis=1
).dropna()

rows, divs = [], {}
for name in sides:
    xs, xp = frame[name]["xs"], frame[name]["xp"]
    d = xs - xp
    divs[name] = d
    rows.append({
        "方式": name,
        "corr(D, センチメント側)": d.corr(xs),
        "corr(D, 価格側)": d.corr(xp),
        "corr(センチメント側, 価格側)": xs.corr(xp),
        "std(D)": d.std(),
        "|D|>2σ_D の日数": int(((d / d.std()).abs() > 2).sum()),
    })

print(f"有効日数: {len(frame)}  期間: {frame.index[0].date()} 〜 {frame.index[-1].date()}")
print(pd.DataFrame(rows).set_index("方式").round(2).to_string())

# D を5分位に分けたときの、その後の平均将来リターン (対数リターン, %)
fwd = {h: np.log(close).shift(-h) - np.log(close) for h in HORIZONS}
for name, d in divs.items():
    q = pd.qcut(d, 5, labels=["Q1(最負)", "Q2", "Q3", "Q4", "Q5(最正)"])
    out = pd.DataFrame({
        f"{h}日後": fwd[h].reindex(d.index).groupby(q, observed=True).mean() for h in HORIZONS
    })
    print(f"\n[{name}] D の5分位別 平均将来リターン(%)")
    print((out * 100).round(2).to_string())