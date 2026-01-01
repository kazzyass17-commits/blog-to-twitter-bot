# ブログ→X（Twitter）自動投稿ボット

完了したブログの既存投稿を自動的にX（Twitter）に投稿するアプリケーションです。

## 機能

1. **ブログ投稿の管理**
   - ブログから全投稿を取得してデータベースに保存
   - 投稿履歴を管理（1巡するまで再投稿しない）

2. **X（Twitter）への自動投稿**
   - `notesofacim.blog.fc2.com` → `@365botGary` に投稿
   - `pursahs-gospel` (Ameba) → `@pursahsgospel` に投稿
   - 未投稿の投稿をランダムに選択して投稿

3. **スケジュール実行**
   - 1日3回（8時、14時、20時）自動実行
   - GitHub Actionsで常時稼働可能

4. **PDF生成**（NotebookLM用、オプション）
   - 取得したコンテンツをPDF化

## セットアップ

### 1. 依存パッケージのインストール

```powershell
pip install -r requirements.txt
```

### 2. X（Twitter）API認証情報の取得

1. [Twitter Developer Portal](https://developer.twitter.com/) にアクセス
2. アプリケーションを作成
3. API Key、API Secret、Access Token、Access Token Secretを取得
4. Bearer Tokenも取得（オプション）

### 3. 環境変数の設定

`env.example.txt` を `.env` にコピーして、認証情報を入力してください：

```powershell
copy env.example.txt .env
```

`.env` ファイルを編集して、Twitter API認証情報を設定します。

詳細なセットアップ手順は `SETUP_GUIDE.md` を参照してください。

### 4. 投稿データベースの初期化（初回のみ）

```powershell
python init_posts.py
```

このスクリプトはブログから全投稿を取得してデータベースに保存します。
初回セットアップ時に1回だけ実行してください。

### 5. 実行

#### 手動実行

```powershell
python main.py
```

#### スケジュール実行（ローカル）

```powershell
python schedule.py
```

#### GitHub Actionsで常時稼働

詳細は `DEPLOYMENT.md` を参照してください。

## 設定

`.env` ファイルで以下を設定できます：

- `POST_INTERVAL_HOURS`: 投稿間隔（時間単位、デフォルト: 24時間）
- `MAX_POST_LENGTH`: 投稿の最大文字数（デフォルト: 280文字）

## 使用方法

### 手動実行

```powershell
python main.py
```

### スケジュール実行

`schedule.py` を使用して、定期的に実行できます：

```powershell
python schedule.py
```

## プロジェクト構造

```
blog-to-twitter-bot/
├── main.py                    # メインアプリケーション
├── init_posts.py              # 投稿データベース初期化スクリプト
├── database.py                # データベース管理モジュール
├── blog_fetcher.py            # ブログ取得モジュール
├── twitter_poster.py          # Twitter投稿モジュール
├── pdf_generator.py           # PDF生成モジュール
├── schedule.py                # スケジューラー（ローカル実行用）
├── config.py                  # 設定管理
├── requirements.txt           # 依存パッケージ
├── env.example.txt            # 環境変数テンプレート
├── posts.db                   # 投稿データベース（自動生成）
├── .github/
│   └── workflows/
│       └── scheduled_posts.yml  # GitHub Actionsワークフロー
├── SETUP_GUIDE.md             # 詳細セットアップガイド
├── DEPLOYMENT.md              # デプロイメントガイド
└── README.md                  # このファイル
```

## 動作の仕組み

1. **初回セットアップ時**
   - `init_posts.py`を実行してブログから全投稿を取得
   - 投稿をデータベース（`posts.db`）に保存

2. **通常実行時（`main.py`）**
   - データベースから未投稿の投稿をランダムに1件選択
   - X（Twitter）に投稿
   - 投稿履歴をデータベースに記録

3. **サイクル管理**
   - 全ての投稿が1回ずつ投稿されるまで、同じ投稿は再投稿されない
   - 1巡（全投稿が投稿済み）が完了すると、新しいサイクルが開始される

4. **スケジュール実行**
   - 1日3回（8時、14時、20時 JST）自動実行
   - GitHub Actionsを使用して常時稼働可能

## 注意事項

- Twitter APIの利用規約を遵守してください
- レート制限に注意してください（1日3回の投稿なので問題ありません）
- ブログの利用規約を確認してください
- 投稿データベース（`posts.db`）は定期的にバックアップすることを推奨します

