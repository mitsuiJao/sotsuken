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
 
- **ファイルパス引数の場合**: 元のPDF名を基にして `_sumarry.md` をつける
  - 例：`Investor sentiment and optimizing traditional quantitative investments.pdf` → `Investor_sentiment_and_optimizing_traditional_quantitative_investments_sumarry.md`
---
 
## 出力手順
 
1. 要約Markdownを生成
2. ファイルパス引数で呼ばれた場合のみ、以下を実行：
   - 要約を `doc/sumarry/` ディレクトリに保存（ファイル名形式：`{PDF名前}_sumarry.md`）
   - `doc/list.md` に自動追記（後述の「doc/list.md への追記」参照）
3. 会話中に要約の概要を1〜2文だけ添える（長い説明は不要）

## doc/list.md への追記
 
現在の形式に従い、以下の順で追記：
```markdown
### [PDF名][ref番号.1]
[sumarry][ref番号.2]
{生成した要約ファイルの冒頭に記述された説明をコピー}

---

[ref番号.1]: ./PDF%20filename.pdf
[ref番号.2]: ./sumarry/PDF_name_sumarry.md
```

- 既存の最後の参照定義の番号を確認して、適切な ref 番号を割り当てる
- 日本語説明は生成した `*_sumarry.md` ファイルの冒頭から抽出してコピー
---
 
## 注意事項
 
- 要約は**情報密度を高く**保つ。自明な接続詞や繰り返しは省く
- 数式は LaTeX 記法（`$...$` / `$$...$$`）で保持する
- 図・表の内容は文章で補完する（画像は埋め込まない）
- 著者の主張と実験結果を混同しないよう区別して書く
- 論文が長大な場合（50ページ超）は主要セクションに絞り、付録は省略してよい

