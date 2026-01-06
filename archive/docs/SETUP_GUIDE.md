# セットアップガイド

このガイドでは、ブログ→X（Twitter）自動投稿ボットのセットアップ手順を説明します。

## 1. Pythonの確認

Python 3.8以上がインストールされているか確認：

```powershell
python --version
```

Pythonがインストールされていない場合は、[Python公式サイト](https://www.python.org/downloads/)からインストールしてください。

## 2. 依存パッケージのインストール

```powershell
cd blog-to-twitter-bot
pip install -r requirements.txt
```

## 3. X（Twitter）API認証情報の取得

### 3.1 Twitter Developer Portalにアクセス

1. [Twitter Developer Portal](https://developer.twitter.com/) にアクセス
2. ログイン（Xアカウントでログイン）

### 3.2 アプリケーションの作成

1. 「Create Project」をクリック
2. プロジェクト名を入力（例: "Blog to Twitter Bot"）
3. 使用目的を選択
4. プロジェクトの説明を入力

### 3.3 アプリの作成

1. 「Create App」をクリック
2. アプリ名を入力（例: "blog-to-twitter-bot"）
3. 「Keys and tokens」タブを開く

### 3.4 認証情報の取得

以下の情報をコピーして保存：

- **API Key** → `TWITTER_API_KEY`
- **API Key Secret** → `TWITTER_API_SECRET`
- **Access Token** → `TWITTER_ACCESS_TOKEN`
- **Access Token Secret** → `TWITTER_ACCESS_TOKEN_SECRET`
- **Bearer Token** → `TWITTER_BEARER_TOKEN`

⚠️ **重要**: これらの情報は機密情報です。絶対に他人に共有しないでください。

### 3.5 複数アカウントを使用する場合

異なるTwitterアカウントに投稿する場合：

1. 各アカウントでDeveloper Portalにログイン
2. それぞれのアカウントでアプリを作成
3. 各アカウントの認証情報を取得
4. `.env`ファイルに各アカウント用の認証情報を設定

## 4. 環境変数の設定

### 4.1 .envファイルの作成

```powershell
copy .env.example .env
```

### 4.2 .envファイルの編集

`.env`ファイルを開いて、取得した認証情報を入力：

```env
TWITTER_API_KEY=あなたのAPI_Keyをここに入力
TWITTER_API_SECRET=あなたのAPI_Key_Secretをここに入力
TWITTER_ACCESS_TOKEN=あなたのAccess_Tokenをここに入力
TWITTER_ACCESS_TOKEN_SECRET=あなたのAccess_Token_Secretをここに入力
TWITTER_BEARER_TOKEN=あなたのBearer_Tokenをここに入力
```

### 4.3 複数アカウントの場合

`.env`ファイルに各アカウント用の認証情報を追加：

```env
# 365botGary用
TWITTER_365BOT_API_KEY=...
TWITTER_365BOT_API_SECRET=...
TWITTER_365BOT_ACCESS_TOKEN=...
TWITTER_365BOT_ACCESS_TOKEN_SECRET=...

# pursahsgospel用
TWITTER_PURSAHS_API_KEY=...
TWITTER_PURSAHS_API_SECRET=...
TWITTER_PURSAHS_ACCESS_TOKEN=...
TWITTER_PURSAHS_ACCESS_TOKEN_SECRET=...
```

## 5. 動作確認

### 5.1 テスト実行

```powershell
python main.py
```

正常に動作すると、以下のようなログが表示されます：

```
2024-01-01 10:00:00 - __main__ - INFO - ブログ→Twitter自動投稿ボット開始
2024-01-01 10:00:01 - __main__ - INFO - [1/2] 365botGary の処理を開始
2024-01-01 10:00:02 - blog_fetcher - INFO - ブログコンテンツを取得中...
...
2024-01-01 10:00:05 - __main__ - INFO - 投稿成功: @365botGary
```

### 5.2 エラーが発生した場合

- **認証エラー**: `.env`ファイルの認証情報を確認
- **ブログ取得エラー**: ブログURLが正しいか確認、ネットワーク接続を確認
- **投稿エラー**: Twitter APIのレート制限や利用規約を確認

## 6. 定期実行の設定

### 6.1 手動でスケジューラーを実行

```powershell
python schedule.py
```

### 6.2 Windowsタスクスケジューラーで自動実行

1. 「タスクスケジューラー」を開く
2. 「基本タスクの作成」を選択
3. 名前: "Blog to Twitter Bot"
4. トリガー: 「毎日」を選択、時間を設定
5. 操作: 「プログラムの開始」を選択
6. プログラム/スクリプト: `python`のフルパス（例: `C:\Python39\python.exe`）
7. 引数の追加: `main.py`のフルパス（例: `C:\Users\kazz17\.cursor\blog-to-twitter-bot\main.py`）
8. 開始: プロジェクトディレクトリのフルパス（例: `C:\Users\kazz17\.cursor\blog-to-twitter-bot`）

## 7. PDF生成について

取得したブログコンテンツは自動的に`pdfs/`ディレクトリにPDFとして保存されます。
これらのPDFファイルはNotebookLMに投入できます。

## トラブルシューティング

### よくあるエラー

#### 1. `ModuleNotFoundError: No module named 'XXX'`
→ 依存パッケージがインストールされていません
```powershell
pip install -r requirements.txt
```

#### 2. `tweepy.errors.Unauthorized: 401 Unauthorized`
→ Twitter API認証情報が正しくありません。`.env`ファイルを確認してください。

#### 3. `tweepy.errors.TooManyRequests: 429 Too Many Requests`
→ レート制限に達しました。しばらく待ってから再試行してください。

#### 4. ブログコンテンツが取得できない
→ ブログURLを確認してください。RSSフィードが利用できない場合は、HTMLパーサーが使用されます。

### ログファイル

実行ログは`bot.log`ファイルに保存されます。エラーが発生した場合は、このファイルを確認してください。

## 注意事項

- Twitter APIの利用規約を遵守してください
- レート制限に注意してください（投稿間隔を適切に設定）
- ブログの利用規約を確認してください
- 認証情報（`.env`ファイル）をGitにコミットしないでください（`.gitignore`に含まれています）


