import yfinance as yf

dat = yf.Ticker("GOOG")
print(dat.fast_info)