# ブログ→Twitter自動投稿ボット

ブログからランダムに投稿を選び、X（Twitter）に自動投稿するボットです。

## 機能

- 2つのアカウント（365botGary、pursahsgospel）で自動投稿
- 1日3回の自動投稿（9時、12時、15時 JST、各時間帯でランダムな分）
- レート制限の自動管理
- 投稿履歴の管理（サイクル機能）

## 必要な環境

- Python 3.8以上
- Twitter API v2の認証情報（API Key、API Secret、Access Token、Access Token Secret）

## セットアップ

### 1. 依存パッケージのインストール

```powershell
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の認証情報を設定してください：

```env
# 365botGary用の認証情報
TWITTER_API_KEY_365BOT=your_api_key
TWITTER_API_SECRET_365BOT=your_api_secret
TWITTER_ACCESS_TOKEN_365BOT=your_access_token
TWITTER_ACCESS_TOKEN_SECRET_365BOT=your_access_token_secret

# pursahsgospel用の認証情報
TWITTER_API_KEY_PURSAHS=your_api_key
TWITTER_API_SECRET_PURSAHS=your_api_secret
TWITTER_ACCESS_TOKEN_PURSAHS=your_access_token
TWITTER_ACCESS_TOKEN_SECRET_PURSAHS=your_access_token_secret

# ブログURL
BLOG_365BOT_URL=http://notesofacim.blog.fc2.com
BLOG_PURSAHS_URL=https://ameblo.jp/pursahs-gospel
```

参考: `env.example.txt`

### 3. データベースの初期化

初回実行時、または新しいブログURLを追加する場合：

```powershell
python init_posts.py
```

## 使用方法

### 手動実行（テスト投稿）

```powershell
$env:PYTHONIOENCODING='utf-8'
python post_both_accounts.py
```

### 自動実行（スケジューラー）

```powershell
$env:PYTHONIOENCODING='utf-8'
python schedule.py
```

スケジューラーは以下のスケジュールで自動投稿します：
- 9時00分～9時59分（ランダム）
- 12時00分～12時59分（ランダム）
- 15時00分～15時59分（ランダム）

## 主要ファイル

- `post_both_accounts.py`: メインの投稿スクリプト（両アカウント対応）
- `schedule.py`: スケジューラー（1日3回の自動投稿）
- `twitter_poster.py`: Twitter投稿処理
- `blog_fetcher.py`: ブログコンテンツ取得
- `database.py`: データベース管理
- `config.py`: 設定管理
- `rate_limit_checker.py`: レート制限管理
- `init_posts.py`: データベース初期化

## 投稿形式

### 365botGary
- タイトル + 本文 + URL + #ACIM
- 最大188文字（URL含む）

### pursahsgospel
- 本文のみ + URL + #ACIM
- 最大188文字（URL含む）

## レート制限管理

- 投稿前にレート制限状態をチェック
- 429エラー発生時、自動的に待機時間を記録
- 投稿成功時、レート制限状態をクリア
- レート制限状態は`rate_limit_state.json`に保存

## データベース

- SQLiteデータベース（`posts.db`）を使用
- 投稿履歴を記録し、サイクル機能で重複投稿を防止
- 各アカウント・ブログURLごとにサイクルを管理

## ログ

- ログはコンソールに出力されます
- 文字化け対策のため、実行時に`PYTHONIOENCODING='utf-8'`を設定してください

## トラブルシューティング

### 429エラー（Too Many Requests）
- レート制限に達しています
- `rate_limit_state.json`を確認し、待機時間を守ってください

### 403エラー（Forbidden）
- 文字数制限を超えている可能性があります
- 投稿テキストが188文字以内であることを確認してください

### 文字化け
- PowerShellで実行する場合、`$env:PYTHONIOENCODING='utf-8'`を設定してください

## ライセンス

このプロジェクトは個人利用を目的としています。
