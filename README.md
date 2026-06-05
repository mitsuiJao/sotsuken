## ファンダメンタル要因を考慮したテクニカル分析の精度向上に関する研究

## 概要
企業に関するニュースと株価変動との関係を調べる

ニュースの性質を判定するためにFinBERTを使用する、取得したニュースと株価データを日単位で紐づけ、センチメントが実際の価格変動をどの程度説明できるかを検証

## データ
- 米国個別株を対象（S&P500構成銘柄が基本）
- 株価, yfinance
- ニュース: FNSPID - CC BY-NC 4.0, 要引用
  - Dong et al. (2024). FNSPID. arXiv:2402.06698
  - FNSPIDのnasdaqサブセット（sabareesh88/FNSPID_nasdaq）を使用

## その他
- XGBoostによる予測およびTreeSHAPによる特徴寮寄与の検証を検討
- dockerでも検証可能なようにする予定
- あとgpu使うならcondaも検討


claude: https://claude.ai/project/019d708f-e083-7161-bc6c-e9f2f2f8a929

---
### API
postman: https://www.postman.com/aaa666-9722/sotsuken/request/egyc86x/news-api?action=share&creator=25020975&active-environment=25020975-01aea5d4-b7e2-47ee-b913-0336cc86d4f0

---
### ニュースデータ
sabareesh88/FNSPID_nasdaq

huggingface: https://huggingface.co/datasets/sabareesh88/FNSPID_nasdaq


Zihan Dong, Xinyu Fan, Zhiyuan Peng
FNSPID: A Comprehensive Financial News Dataset in Time Series

arXiv: https://arxiv.org/abs/2402.06698