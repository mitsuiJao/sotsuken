import pandas as pd
import mplfinance as mpf

# trade_date  sent  neu  n_news

N = 60
EMA_SHORT = 5
EMA_LONG = 20

sentiment = pd.read_parquet("./data/sentiment/AAPL_daily_sentiment.parquet")
sentiment = sentiment.dropna(subset=["sent"]).set_index("trade_date")
# ema
sentiment["ema_short"] = sentiment["sent"].ewm(span=EMA_SHORT, adjust=False).mean()
sentiment["ema_long"] = sentiment["sent"].ewm(span=EMA_LONG, adjust=False).mean()

df = pd.read_parquet("./data/stock/AAPL.parquet")
df.index = df.index.tz_localize(None).normalize()

stock = df.loc[sentiment.index.min():sentiment.index.max(), ["Open", "High", "Low", "Close", "Volume"]].tail(N)
sentiment_trimmed = sentiment.reindex(stock.index)
print(stock)
print(sentiment_trimmed)

ap = [
    mpf.make_addplot(sentiment_trimmed["sent"], panel=0, color="blue", width=1, secondary_y=True, ylabel="Sentiment"),
    mpf.make_addplot(sentiment_trimmed["n_news"], panel=1, type="bar", color="gray", ylabel="n_news"),
]
mpf.plot(stock, type="candle", style="yahoo", volume=False, addplot=ap, savefig="./data/chart/aapl_sentiment_chart.png")

# 0の基準線が入る範囲でデータに合わせる
sent_pad = 0.02
sent_ylim = (min(sentiment_trimmed["sent"].min(), 0) - sent_pad, sentiment_trimmed["sent"].max() + sent_pad)
zero = pd.Series(0.0, index=stock.index)

ap_ema = [
    mpf.make_addplot(zero, panel=0, color="black", width=0.8, linestyle="--", secondary_y=True, ylim=sent_ylim),
    mpf.make_addplot(sentiment_trimmed["sent"], panel=0, color="lightblue", width=1.5, ylabel="センチメント", label="sent", secondary_y=True, ylim=sent_ylim),
    mpf.make_addplot(sentiment_trimmed["ema_short"], panel=0, color="blue", width=2, label=f"EMA{EMA_SHORT}", secondary_y=True, ylim=sent_ylim),
    # mpf.make_addplot(sentiment_trimmed["ema_long"], panel=0, color="orange", width=2, label=f"EMA{EMA_LONG}", secondary_y=True, ylim=sent_ylim),
    mpf.make_addplot(sentiment_trimmed["n_news"], panel=1, type="bar", color="gray", ylabel="記事数"),
]
# 日本語用フォントと文字サイズ
style_jp = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"font.family": "Noto Sans CJK JP", "font.size": 16})
# mpf.plot(stock, type="candle", style=style_jp, volume=False, addplot=ap_ema, panel_ratios=(3, 1), figsize=(16, 8), ylabel="株価 (USD)", title="AAPL 株価とセンチメントスコア", savefig="./data/chart/aapl_sentiment_ema_chart_titled.png")
mpf.plot(stock, type="candle", style=style_jp, volume=False, addplot=ap_ema, panel_ratios=(3, 1), figsize=(16, 8), ylabel="株価 (USD)", savefig="./data/chart/aapl_sentiment_ema_chart.png")
