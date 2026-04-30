---
name: paper-summarizer
description: "論文をアップロード、URL、またはファイルパス引数で渡されたとき、日本語で構造化要約を作成しMarkdownファイルとして出力するスキル。要約後は doc/list.md に自動追記する。ファイルパス引数が doc/ (または @doc/) 以外からの場合は事前確認。「論文を要約して」「この論文をまとめて」「mdでダウンロードしたい」など論文の要約が絡む場合は必ずこのスキルを使うこと。"
---
 
# Paper Summarizer
 
論文を日本語で構造化要約し、Markdownファイルとして出力するスキル。
 
## 入力の受け取り方
 
### ファイルパス引数の渡し方
スラッシュコマンドまたは args パラメータで PDFパスを指定：
```
/paper-summarizer doc/example.pdf
```
または
```
/paper-summarizer "doc/path with spaces.pdf"
```

### ファイルパス引数の処理
ユーザーが `/paper-summarizer doc/example.pdf` のようにファイルパスを引数で指定した場合：
1. **パス確認** - `doc/` または `@doc/` ディレクトリ内かチェック
   - `doc/` または `@doc/` 内なら処理継続
   - それ以外なら「別パスでの処理ですが大丈夫ですか？」と確認してから処理
2. `pdftotext -layout <path> -` でテキスト抽出を試みる
3. テキストが空または文字化けしている場合は `pdftoppm -jpeg -r 150` でページをラスタライズ
4. **処理後** - 自動で `doc/list.md` に要約を追記

```bash
# テキスト抽出確認
pdftotext -f 1 -l 2 /path/to/file.pdf - | head -30
 
# 文字化け・空の場合はラスタライズ
pdftoppm -jpeg -r 150 -f 1 -l 1 /path/to/file.pdf /tmp/page
```
 
---
 
## 要約フォーマット
 
以下の構成でMarkdownを生成すること。各セクションは**日本語**で記述する。原文が英語でも日本語に翻訳・要約する。
 
```markdown
# {日本語タイトル}
 
**原題**: {英語原題}
**著者**: {著者名（全員 or 筆頭+et al.）}
**掲載誌・会議 / 年**: {venue, year}
**arXiv / DOI**: {あれば記載}
 
> {論文を一文で表すキャッチライン。「何をして、何がわかったか」を30字前後で}
 
---
 
## 背景・問題設定
 
{この研究が取り組む課題・動機・先行研究との関係を2〜4段落で}
 
## 提案手法
 
{アーキテクチャ・アルゴリズム・理論的枠組みなど。重要な数式があれば LaTeX 記法で残す}
 
## 実験・評価
 
{データセット、ベースライン、評価指標、実験設定の概要}
 
## 結果
 
{定量的結果・定性的知見。表があれば簡略化してMarkdownテーブルで再現}
 
## 結論・今後の課題
 
{著者らの主張・limitation・将来展望}
 
## 一言コメント
 
{要約者（Claude）から見た、この論文の面白さ・注意点・関連研究へのポインタなど、1〜3文}
```
 
---
 
## ファイル名の生成ルール

PDFから著者名と掲載年を抽出し、以下の形式で生成する：

**形式**: `FirstName_LastName&FirstName_LastName&...&FirstName_LastName_Year.md`

それと同時にPDFファイル名をMDに着けたファイル名と同じ名前に変更する。

### 処理ステップ

1. **著者情報の抽出**
   - PDFの1ページ目から著者名（すべて）と掲載年を抽出
   - 著者名が複数の場合は全員を列挙

2. **著者名のフォーマット**
   - 各著者を `FirstName_LastName` 形式に正規化
   - 複数著者は `&` で区切る
   - 例：`Zheng Chen, Wenlin Li, Jia Huang` → `Zheng_Chen&Wenlin_Li&Jia_Huang_2025`

3. **年の抽出**
   - 掲載年（発表年）をファイル名の末尾に追加
   - 形式：`{著者}&..._{YYYY}.md`

### 例
- 単一著者：`Amos Tversky, Daniel Kahneman, 1974` → `Amos_Tversky&Daniel_Kahneman_1974.md`
- 複数著者：`Shimaa Ouf, Mona El Hawary, Amal Aboutabl, Sherif Adel, 2025` → `Shimaa_Ouf&Mona_El_Hawary&Amal_Aboutabl&Sherif_Adel_2025.md`

---
 
## 出力手順
 
1. 要約Markdownを生成
2. ファイルパス引数で呼ばれた場合のみ、以下を実行：
   - PDFから著者名と掲載年を抽出
   - ファイル名を `FirstName_LastName&FirstName_LastName_Year.md` 形式で生成
   - 要約を `doc/thesis/sumarry/` ディレクトリに保存
   - `doc/thesis/list.md` に自動追記（後述の「doc/list.md への追記」参照）
3. 会話中に要約の概要を1〜2文だけ添える（長い説明は不要）

## doc/list.md への追記
 
現在の形式に従い、以下の順で追記：
```markdown
### [FirstName_LastName&FirstName_LastName_Year.pdf][ref番号.1]
**{日本語タイトル}**

[sumarry][ref番号.2]

{生成した要約ファイルの冒頭に記述された説明をコピー}

---

[ref番号.1]: ./FirstName_LastName&FirstName_LastName_Year.pdf
[ref番号.2]: ./sumarry/FirstName_LastName&FirstName_LastName_Year.md
```

- 既存の最後の参照定義の番号を確認して、適切な ref 番号を割り当てる
- 日本語タイトルは生成した要約ファイルの1行目（`# `で始まる行）から抽出（Markdown見出しの `#` を除く）
- 日本語説明は生成した要約ファイル（FirstName_LastName&..._Year.md）の冒頭から抽出してコピー
- ファイルパスに含まれる `&` は URL エンコード `%26` に変換する必要がある場合がある
---
 
## 注意事項
 
- 要約は**情報密度を高く**保つ。自明な接続詞や繰り返しは省く
- 数式は LaTeX 記法（`$...$` / `$$...$$`）で保持する
- 図・表の内容は文章で補完する（画像は埋め込まない）
- 著者の主張と実験結果を混同しないよう区別して書く
- 論文が長大な場合（50ページ超）は主要セクションに絞り、付録は省略してよい

---

## 探索モード

### トリガー条件

以下のいずれかが入力に含まれるとき探索モードを発動する：

- 「関連論文」＋「探して／見つけて／ダウンロード／取得／まとめて」のいずれか
- 「参考文献」＋「探して／調べて／ダウンロード／取得」のいずれか
- 「論文を集めて」「論文を探して」

**補助引数（オプション）**：
- `--discover <path>` — 起点となる論文PDFを指定
- 引数なしの場合は `doc/thesis/sumarry/` 全体の要約内容をキーワード源とする

### Step 1: 探索起点の決定

1. `--discover <path>` が指定されていればそのPDF
2. 会話中に論文が言及されていれば、その論文
3. どちらもなければ `doc/thesis/sumarry/` 内のすべての要約ファイル（FirstName_LastName&..._.md）から卒論テーマキーワードを抽出

### Step 2: 候補論文の収集

**ルートA: 参考文献の抽出**（起点PDFがある場合）

```bash
pdftotext -layout "<起点PDF>" - | grep -A 2000 -iE "^[[:space:]]*(References|Bibliography|参考文献)"
```

抽出したテキストから著者・タイトル・年を解析してリストを作成する。

**ルートB: WebSearch**（常に実施）

以下のようなクエリでarXiv・Semantic Scholar等を検索し候補を追加する：
```
"<起点論文タイトルの一部> stock prediction sentiment analysis 2023 OR 2024 OR 2025"
```

### Step 3: Claudeによる絞り込み

収集した候補から以下の基準で **3〜5件** を選定する：

- 卒論テーマ（感情分析・株価予測・LLM・SHAP・テクニカル指標）との関連度が高い
- `doc/thesis/` にすでに同名・類似ファイルが存在しない（重複排除）
- 2020年以降の論文を優先

### Step 4: PDF URLの特定とダウンロード

各選定論文について PDF URL を特定する：
1. arXiv: `arxiv.org/abs/XXXX` → `arxiv.org/pdf/XXXX` に変換
2. 直接 PDF URL が判明している場合: そのまま使用
3. 不明な場合: WebSearch で `"<タイトル>" filetype:pdf` または `"<タイトル>" arxiv` を再検索

```bash
# ファイル名はタイトルから生成（スペース保持、既存命名規則に倣う）
curl -L --fail -o "doc/thesis/<タイトル>.pdf" "<pdf_url>"
```

- ダウンロード失敗（ペイウォール・404等）→ スキップして次へ
- 重複ファイルが存在する場合 → スキップ

### Step 5: 要約・保存

ダウンロード成功した各PDFに対して「ファイルパス引数の処理」フローを実行する：
- `pdftotext -layout <path> -` でテキスト抽出（失敗時は `pdftoppm` でリトライ）
- PDFから著者名と掲載年を抽出し、`FirstName_LastName&FirstName_LastName_Year.md` 形式でファイル名を生成
- `doc/thesis/sumarry/` に要約を保存
- `doc/thesis/list.md` に追記

### Step 6: 完了報告

会話内で以下を報告する：
- 取得・要約した論文（件数・タイトル一覧）
- スキップした論文とその理由（ペイウォール・重複・関連度低など）

