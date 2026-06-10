from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
from practice_xgb import get_data

df = get_data()

feature_cols = ["ret_1d", "ret_5d", "vol_ratio",
                "rsi", "macd", "macd_signal", "macd_hist",
                "ma20_dev", "ma60_dev"]

X = df[feature_cols]
y = df["target"]

split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

model = XGBClassifier(
    n_estimators=200,           # 決定木の数
    max_depth=4,                # 深さ
    learning_rate=0.05,         # 学習率
    subsample=0.8,              # サンプルの割合
    colsample_bytree=0.8,       # 特徴量のサンプルの割合
    eval_metric="logloss",      # 進捗
    random_state=42             # 乱数シード（定数）
)

model.fit(X_train, y_train,
          eval_set=[(X_test, y_test)],  
          verbose=50)

y_pred = model.predict(X_test)
print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))