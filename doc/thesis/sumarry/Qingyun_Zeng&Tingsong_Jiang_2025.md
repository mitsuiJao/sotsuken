# FinBERTを用いた金融感情分析と株価変動予測への応用

**原題**: Financial Sentiment Analysis Using FinBERT with Application in Predicting Stock Movement
**著者**: Qingyun Zeng (University of Pennsylvania), Tingsong Jiang (University of Rochester)
**掲載誌・会議 / 年**: 42nd International Conference on Machine Learning (ICML), 2025
**arXiv / DOI**: arXiv:2306.02136

> FinBERT で抽出した金融ニュース感情スコアを LSTM に統合することで、ARIMA・単独 LSTM・base BERT+LSTM を上回る株価予測精度を達成した。

---

## 背景・問題設定

BERTをベースにした事前学習済み言語モデルが NLP 全般で高い性能を示す中、金融テキストに特化したFinBERT（Araci, 2019）はロイターTRC2や Financial PhraseBank で追加学習され、財務コミュニケーションの感情分類において優れた能力を持つ。一方、株式市場の時系列予測には ARIMA が伝統的に使われてきたが、金融データの非線形性を捉えにくい。LSTMなどの深層学習モデルがその代替として有望視されているが、ニュースや SNS の感情情報をどう組み込むかは未解決課題として残っていた。

本研究の基本仮説は効率的市場仮説（EMH）に基づく「ニュース等の感情情報は株価変動と高い相関を持つ」というものである。ただし因果関係の同定は行わず、感情と価格変動の相関を定量化することに絞っている。

## 提案手法

モデルは **感情分析モジュール** と **LSTMベース時系列予測モジュール** の2段構成。

### 感情スコア算出

各ニュースタイトルを FinBERT（`ProsusAI/finbert`）に入力し、3クラス（positive/negative/neutral）のソフトマックス確率を取得。日次の感情スコアを以下で定義：

$$\text{SentimentScore}_t = \frac{1}{N_t} \sum_{n=1}^{N_t} \left[ P_n(\text{positive}) - P_n(\text{negative}) \right]$$

### 数値感情指数（NSI）

市場ベースの感情ラベルとして、日次リターン $r_t = \frac{\text{Close}_t - \text{Open}_t}{\text{Open}_t}$ から：

$$\text{NSI}_t = \begin{cases} 1 & \text{if } r_t > s \\ 0 & \text{if } -s \le r_t \le s \\ -1 & \text{if } r_t < -s \end{cases}$$

閾値 $s = 0.01$。このラベルは FinBERT のファインチューニングや感情-価格相関分析に活用される。

### LSTMアーキテクチャ

- 入力特徴量：感情スコア + 過去 $k=60$ 日分の始値・高値・安値・終値・出来高（MinMax正規化）
  $$X_t = [S_t, C_{t-1}, O_{t-1}, H_{t-1}, L_{t-1}, V_{t-1}, \ldots, C_{t-k}, O_{t-k}, H_{t-k}, L_{t-k}, V_{t-k}]$$
- LSTM層×2（各100ユニット）→ Dense(25, ReLU) → Dense(1, linear)
- 損失関数：MSE、最適化：Adam（lr=0.001）、エポック上限100、バッチサイズ1
- 早期終了：validationロスが20エポック改善しない場合に停止

## 実験・評価

**データセット**
- Historical Financial News Archive（Kaggle、米国800社以上、最大2019年まで12年間）
- Daily Financial News for 6000+ Stocks（Kaggle、補足用）
- yfinance API で取得した日次株価（始値・高値・安値・終値・出来高）
- 結合後の総レコード数：1,056,471件

**前処理**：タイトル重複除去、非取引日の感情スコアを次の営業日に対応付け、Min-Max スケーリング

**学習・評価分割**：時系列順に先頭90%を訓練、残り10%をテストに使用（データリーク防止）

**比較ベースライン**
1. ARIMA（1,1,2）
2. LSTM（数値データのみ）
3. FinBERT + DNN（Dense層2段、256ユニット、Leaky ReLU）
4. Base BERT + LSTM

## 結果

| モデル | Validation Loss（MSE） |
|---|---|
| ARIMA | 0.00975 |
| LSTM（数値のみ） | 1.1937×10⁻³ |
| BERT + LSTM | 3.3132×10⁻⁴ |
| FinBERT + DNN | 3.4177×10⁻⁴ |
| **FinBERT + LSTM（提案）** | **3.1975×10⁻⁴** |

- 提案モデル（FinBERT + LSTM）が全モデル中最低のvalidationロスを達成
- Base BERT + LSTM との差は僅差。オフザシェルフ FinBERT（追加ファインチューニングなし）の場合、金融ドメイン適応の優位性が小さい
- ARIMA は長期トレンドの追随は得意だが短期変動への追随は弱い
- 提案モデルは短期変動の予測精度が高い一方、長期での過少予測傾向あり

## 結論・今後の課題

FinBERT + LSTM の組み合わせが ARIMA や単独 LSTM を上回ることを示し、感情情報の組み込みが株価変動予測を改善することを実証した。主な限界と今後の方向性：

1. **ハイブリッドモデル化**：ARIMAで長期トレンドを前処理してからLSTMへ入力（Shi et al., 2022 の手法を参考）
2. **データ拡充**：個別銘柄のデータが少ない（MSFT で前処理後1440行）。記事本文や Twitter 等SNSデータの活用
3. **FinBERT のファインチューニング**：NSI を教師ラベルとした追加学習で精度向上が見込まれる
4. **高度な時系列アーキテクチャ**：TEANet 等のTransformer時系列モデルとの統合

## 一言コメント

オフザシェルフ FinBERT の感情スコアを素直に LSTM へ結合するシンプルな構成で結果を示しており、再現性が高い。一方で FinBERT と base BERT の差が小さい点は、NSI によるドメイン適応ファインチューニングの余地を示唆しており、追試価値が高い。株価予測のベースライン実装として参考にしやすい論文。
