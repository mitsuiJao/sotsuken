import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
import os

load_dotenv()

DATA_PATH = Path(os.getenv("STOCK_PATH"))

df = pd.read_parquet(DATA_PATH / "AAPL.ori.parquet")

df["return"] = df["Close"].pct_change()
df["logreturn"] = np.log(df["Close"] / df["Close"].shift(1))

df.to_parquet(DATA_PATH / "AAPL.parquet")