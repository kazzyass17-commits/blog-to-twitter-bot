# Git移行ガイド

このプロジェクトをGitリポジトリに移動する手順です。

## 現在の状況

- プロジェクトは `c:\Users\kazz17\.cursor\blog-to-twitter-bot` にあります
- Gitリポジトリとして初期化済み
- 機密情報（.env）やデータファイル（posts.db）は.gitignoreで除外されています

## GitHubへの移動手順

### 1. GitHubリポジトリの作成

1. [GitHub](https://github.com)にログイン
2. 新しいリポジトリを作成
3. リポジトリ名を入力（例: `blog-to-twitter-bot`）
4. **README、.gitignore、ライセンスは追加しない**（既に存在するため）

### 2. リモートリポジトリの追加とプッシュ

```powershell
cd c:\Users\kazz17\.cursor\blog-to-twitter-bot

# リモートリポジトリを追加（URLは実際のリポジトリURLに置き換えてください）
git remote add origin https://github.com/ユーザー名/リポジトリ名.git

# メインブランチをプッシュ
git push -u origin main
```

### 3. GitHub Secretsの設定

リポジトリのSettings → Secrets and variables → Actions で以下のSecretsを設定：

- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN`

（必要に応じて各アカウント用の認証情報も設定）

### 4. PC上のファイルの削除

GitHubへのプッシュが完了したら、PC上のファイルを削除できます：

```powershell
# 親ディレクトリに移動
cd c:\Users\kazz17\.cursor

# プロジェクトディレクトリを削除
Remove-Item -Recurse -Force blog-to-twitter-bot
```

## 注意事項

- `.env`ファイルはGitに含まれていません（機密情報のため）
- `posts.db`ファイルもGitに含まれていません（GitHub Actionsでキャッシュを使用）
- GitHub Actionsを使用する場合は、初回実行時に`init_posts.py`が実行される必要があります

## 今後の使用

GitHub Actionsで自動実行されるため、PC上でプログラムを実行する必要はありません。

必要な場合のみ、ローカルにクローンして作業できます：

```powershell
git clone https://github.com/ユーザー名/リポジトリ名.git
cd リポジトリ名
```

