import pandas as pd
from dotenv import load_dotenv
import os
from pathlib import Path
import numpy as np
import datetime
import holidays

load_dotenv()

DATA_DIR = Path(os.getenv("FNSPID_PATH"))
SENTIMENT_PATH = DATA_DIR / "data" / "news_sentiment.parquet"
OUTPUT_PATH = DATA_DIR / "daily_sentiment.parquet"

us_holidays = holidays.NASDAQ()

def dialy_sentiment(data: pd.DataFrame):
    data["score"] = data["positive"] - data["negative"]
    
    

def lag_corr(s: pd.Series, r: pd.Series, taus=range(-10, 11)):
    n = len(s.dropna())
    rows = []
    for tau in taus:
        rho = s.corr(r.shift(-tau))
        rows.append((tau, rho))
    
    out = pd.DataFrame(rows, columns=["tau", "rho"]).set_index("tau")
    out["thr"] = 2 / np.sqrt(n)
    out["sig"] = out["rho"].abs() > out["thr"]
    return out