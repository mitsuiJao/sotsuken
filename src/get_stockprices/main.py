import yfinance as yf

yf.config.locale.lang = "ja-JP"
yf.config.locale.region = "JP"

tickers_list = ["AAPL", "MSFT", "NVDA", "V", "^GSPC"]
tickers = yf.Tickers(" ".join(tickers_list))

for symbol in tickers_list:
    ticker = tickers.tickers[symbol]
    df = ticker.history(period="max")
    df.to_parquet(f"{symbol}.parquet")