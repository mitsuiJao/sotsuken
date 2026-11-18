"""センチメント−株価 乖離 (divergence.py の方式 A) を複数銘柄・全期間で検証する。

使い方: python divergence_multi.py [TICKER ...]   (省略時は TICKERS 全部)

出力
- data/divergence/{TICKER}.parquet         日次の z_sent / z_price / divergence
- data/chart/{ticker}_divergence_long.png  全期間の 3 段チャート
- data/chart/divergence_quintile.png       乖離 5 分位別の将来リターン (銘柄別)
- 標準出力                                 銘柄別・プールの検証表
"""
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

STOCK_PATH = Path(os.getenv("STOCK_PATH"))
SENTIMENT_PATH = Path(os.getenv("SENTIMENT_PATH"))
ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "divergence"
CHART_DIR = ROOT / "data" / "chart"

TICKERS = sys.argv[1:] or ["AAPL", "MSFT", "NVDA", "V"]
N = 5            # 短期窓 (n日リターン / n日平均センチメント)
M = 120          # 標準化の窓
MIN_FRAC = 0.8   # 窓内の有効日がこの割合以上なら z を計算 (ニュース欠損日の許容)
HORIZONS = (1, 5, 10)
QLABELS = ["Q1(最負)", "Q2", "Q3", "Q4", "Q5(最正)"]

BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#8a8984", "#e5e4df"
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 14})


def z(x, m=M):
    """過去 m 日 (当日を除く) の平均・標準偏差で標準化"""
    r = x.rolling(m, min_periods=int(m * MIN_FRAC))
    return (x - r.mean().shift(1)) / r.std().shift(1)


def load(ticker):
    close = pd.read_parquet(STOCK_PATH / f"{ticker}.parquet")["Close"]
    sent = pd.read_parquet(SENTIMENT_PATH / f"{ticker}_daily_sentiment.parquet")
    sent = sent.set_index(pd.DatetimeIndex(sent["trade_date"]).tz_localize(close.index.tz))
    # ニュースのある期間だけに株価を絞り、センチメントを営業日に揃える (ニュースのない日は NaN)
    sent = sent[sent["n_news"] > 0]
    close = close.loc[sent.index.min() - pd.Timedelta(days=2 * M): sent.index.max()]
    return close, sent["sent"].reindex(close.index), sent["n_news"].reindex(close.index).fillna(0)


def divergence(close, sent):
    p = np.log(close).diff(N)
    s = sent.rolling(N, min_periods=3).mean()
    df = pd.DataFrame({"z_sent": z(s), "z_price": z(p)})
    df["divergence"] = df["z_sent"] - df["z_price"]
    return df


def evaluate(d, close):
    """乖離 D と将来リターンの関係。fwd_h は t 日終値→t+h 日終値の対数リターン"""
    logc = np.log(close)
    fwd = pd.DataFrame({h: (logc.shift(-h) - logc).reindex(d.index) for h in HORIZONS})
    ok = fwd.notna().all(axis=1)
    d, fwd = d[ok], fwd[ok]
    q = pd.qcut(d, 5, labels=QLABELS)
    quint = fwd.groupby(q, observed=True).mean() * 100
    stats = {"日数": len(d), "期間": f"{d.index[0].date()}〜{d.index[-1].date()}"}
    for h in HORIZONS:
        ic = d.rank().corr(fwd[h].rank())
        # 重なりのないサンプル (h 日おき) で t 値: 自己相関による過大評価を避ける
        dn, fn = d.iloc[::h], fwd[h].iloc[::h]
        icn = dn.rank().corr(fn.rank())
        stats[f"IC{h}"] = ic
        stats[f"t{h}(非重複)"] = icn * np.sqrt((len(dn) - 2) / (1 - icn**2))
        stats[f"Q5−Q1 {h}日(%)"] = quint.loc[QLABELS[-1], h] - quint.loc[QLABELS[0], h]
    return quint, stats, pd.DataFrame({"D": d, **{f"fwd{h}": fwd[h] for h in HORIZONS}})


def chart(ticker, d, close, n_news):
    fig, axes = plt.subplots(4, 1, figsize=(18, 13), sharex=True,
                             gridspec_kw={"height_ratios": [2, 2, 2, 1]})
    axes[0].plot(close.index, close, color=INK, linewidth=1.2)
    axes[0].set_ylabel("株価 (USD)")
    axes[0].set_title(f"{ticker}  センチメント−株価 乖離 (n={N}, m={M})", loc="left")

    axes[1].plot(d.index, d["z_sent"], color=BLUE, linewidth=1.2, label="センチメント (z)")
    axes[1].plot(d.index, d["z_price"], color=ORANGE, linewidth=1.2, label=f"株価{N}日リターン (z)")
    axes[1].axhline(0, color=MUTED, linewidth=0.8)
    axes[1].set_ylabel("z スコア")
    axes[1].legend(loc="upper left", frameon=False, ncol=2)

    dv = d["divergence"].dropna()
    axes[2].bar(dv.index, dv, width=1.0, color=np.where(dv >= 0, BLUE, ORANGE))
    axes[2].axhline(0, color=MUTED, linewidth=0.8)
    for y in (2, -2):
        axes[2].axhline(y, color=MUTED, linewidth=0.8, linestyle="--")
    axes[2].set_ylabel("乖離 (z差)")
    axes[2].text(0.01, 0.95, "青: センチメント > 株価　橙: 株価 > センチメント",
                 transform=axes[2].transAxes, va="top", color=INK)

    axes[3].bar(n_news.index, n_news, width=1.0, color=MUTED)
    axes[3].set_ylabel("記事数/日")

    for ax in axes:
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(CHART_DIR / f"{ticker.lower()}_divergence_long.png", dpi=100)
    plt.close(fig)


def quintile_chart(quints):
    fig, axes = plt.subplots(1, len(HORIZONS), figsize=(18, 5.5), sharey=False)
    names = list(quints)
    w = 0.8 / len(names)
    palette = ["#2a78d6", "#eb6834", "#3a9e6b", "#8a5cc2", INK]
    for ax, h in zip(axes, HORIZONS):
        for i, name in enumerate(names):
            ax.bar(np.arange(5) + (i - (len(names) - 1) / 2) * w, quints[name][h], width=w,
                   color=palette[i % len(palette)], label=name)
        ax.set_xticks(range(5), ["Q1\n(株価>セ)", "Q2", "Q3", "Q4", "Q5\n(セ>株価)"])
        ax.axhline(0, color=MUTED, linewidth=0.8)
        ax.set_title(f"{h}日後 平均リターン (%)", loc="left")
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "divergence_quintile.png", dpi=100)
    plt.close(fig)


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows, quints, pooled = [], {}, []
    for t in TICKERS:
        close, sent, n_news = load(t)
        div = divergence(close, sent)
        div.to_parquet(OUT_DIR / f"{t}.parquet")
        d = div.dropna()
        chart(t, d, close.loc[d.index[0]:], n_news.loc[d.index[0]:])

        quint, stats, ev = evaluate(d["divergence"], close)
        quints[t] = quint
        # プール用: 銘柄ごとに D を 5 分位化してから結合 (銘柄間のスケール差を除く)
        ev["q"] = pd.qcut(ev["D"], 5, labels=QLABELS)
        pooled.append(ev.assign(ticker=t))
        rows.append({"銘柄": t, "ニュース日割合": (n_news.loc[d.index] > 0).mean(), **stats})
        print(f"\n[{t}] 乖離 5 分位別 平均将来リターン(%)")
        print(quint.round(2).to_string())

    pool = pd.concat(pooled)
    quints["プール"] = pool.groupby("q", observed=True)[[f"fwd{h}" for h in HORIZONS]].mean().set_axis(HORIZONS, axis=1) * 100
    print("\n[プール] 乖離 5 分位別 平均将来リターン(%)")
    print(quints["プール"].round(2).to_string())

    print("\n=== 銘柄別サマリ (IC: Spearman 順位相関, t: h日おきの非重複サンプルで計算) ===")
    print(pd.DataFrame(rows).set_index("銘柄").round(3).to_string())
    if len(TICKERS) > 1:
        quintile_chart(quints)
