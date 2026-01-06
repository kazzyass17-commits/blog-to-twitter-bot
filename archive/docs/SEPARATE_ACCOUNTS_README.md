# アカウント分離版の使い方

## 概要

365botGaryとpursahsgospelのプログラムを完全に分離しました。
それぞれ独立して実行・管理できます。

## ファイル構成

### 365botGary用
- `main_365bot.py`: 365botGary専用のメインプログラム
- `schedule_365bot.py`: 365botGary専用のスケジューラー
- `bot_365bot.log`: 365botGary専用のログファイル

### pursahsgospel用
- `main_pursahs.py`: pursahsgospel専用のメインプログラム
- `schedule_pursahs.py`: pursahsgospel専用のスケジューラー
- `bot_pursahs.log`: pursahsgospel専用のログファイル

### 共通ファイル
- `main.py`: 旧バージョン（両方のアカウントを処理）
- `schedule.py`: 旧バージョン（両方のアカウントを処理）
- `config.py`: 設定管理（両方のアカウントの認証情報を含む）
- `database.py`: データベース管理（共通）
- `blog_fetcher.py`: ブログ取得（共通）
- `twitter_poster.py`: Twitter投稿（共通）

## 使い方

### 1. 単発実行

#### 365botGaryのみ実行
```bash
python main_365bot.py
```

#### pursahsgospelのみ実行
```bash
python main_pursahs.py
```

### 2. スケジュール実行

#### 365botGaryをスケジュール実行
```bash
python schedule_365bot.py
```

#### pursahsgospelをスケジュール実行
```bash
python schedule_pursahs.py
```

### 3. 両方を同時に実行（別プロセス）

#### Windows PowerShell
```powershell
# 365botGaryをバックグラウンドで実行
Start-Process python -ArgumentList "schedule_365bot.py" -WindowStyle Hidden

# pursahsgospelをバックグラウンドで実行
Start-Process python -ArgumentList "schedule_pursahs.py" -WindowStyle Hidden
```

#### Linux/Mac
```bash
# 365botGaryをバックグラウンドで実行
nohup python schedule_365bot.py > bot_365bot.log 2>&1 &

# pursahsgospelをバックグラウンドで実行
nohup python schedule_pursahs.py > bot_pursahs.log 2>&1 &
```

## 設定

### 環境変数（.envファイル）

両方のアカウントの認証情報を設定する必要があります：

```env
# 365botGary アカウント用の認証情報
TWITTER_365BOT_API_KEY=...
TWITTER_365BOT_API_SECRET=...
TWITTER_365BOT_ACCESS_TOKEN=...
TWITTER_365BOT_ACCESS_TOKEN_SECRET=...
TWITTER_365BOT_BEARER_TOKEN=...

# pursahsgospel アカウント用の認証情報
TWITTER_PURSAHS_API_KEY=...
TWITTER_PURSAHS_API_SECRET=...
TWITTER_PURSAHS_ACCESS_TOKEN=...
TWITTER_PURSAHS_ACCESS_TOKEN_SECRET=...
TWITTER_PURSAHS_BEARER_TOKEN=...

# ブログURL設定
BLOG_365BOT_URL=http://notesofacim.blog.fc2.com/
TWITTER_365BOT_HANDLE=365botGary

BLOG_PURSAHS_URL=https://www.ameba.jp/profile/general/pursahs-gospel/
TWITTER_PURSAHS_HANDLE=pursahsgospel
```

## データベース

両方のアカウントは同じデータベース（`posts.db`）を使用しますが、
`blog_url`と`twitter_handle`で区別されます。

## ログファイル

- `bot_365bot.log`: 365botGary専用のログ
- `bot_pursahs.log`: pursahsgospel専用のログ

## 利点

1. **独立した実行**: それぞれのアカウントを独立して実行・管理できます
2. **個別のログ**: それぞれのログファイルで管理が容易です
3. **個別のスケジュール**: それぞれ異なるスケジュールで実行できます
4. **エラー分離**: 一方のアカウントでエラーが発生しても、もう一方に影響しません

## 注意事項

- 両方のアカウントを同時に実行する場合は、レート制限に注意してください
- データベースは共通なので、両方のアカウントが同じデータベースを使用します
- 旧バージョンの`main.py`と`schedule.py`は残していますが、新しい分離版を使用することを推奨します




