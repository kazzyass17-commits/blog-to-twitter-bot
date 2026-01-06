# GitHubへのプッシュ手順

## 現在の状況

✅ Gitリポジトリは初期化済み
✅ すべてのファイルはコミット済み
✅ .env、posts.db、ログファイルは除外済み

## 次のステップ

### 1. GitHubリポジトリを作成

1. [GitHub](https://github.com)にログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名を入力（例: `blog-to-twitter-bot`）
4. **重要**: README、.gitignore、ライセンスは追加しない（既に存在するため）
5. 「Create repository」をクリック

### 2. リモートリポジトリを追加してプッシュ

```powershell
cd c:\Users\kazz17\.cursor\blog-to-twitter-bot

# リモートリポジトリを追加（URLは実際のリポジトリURLに置き換えてください）
git remote add origin https://github.com/ユーザー名/リポジトリ名.git

# メインブランチをプッシュ
git push -u origin main
```

### 3. GitHub Secretsの設定

リポジトリのSettings → Secrets and variables → Actions で以下のSecretsを設定：

**必須:**
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN`

**オプション（別アカウントを使用する場合）:**
- `TWITTER_365BOT_API_KEY`
- `TWITTER_365BOT_API_SECRET`
- `TWITTER_365BOT_ACCESS_TOKEN`
- `TWITTER_365BOT_ACCESS_TOKEN_SECRET`
- `TWITTER_PURSAHS_API_KEY`
- `TWITTER_PURSAHS_API_SECRET`
- `TWITTER_PURSAHS_ACCESS_TOKEN`
- `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`

### 4. PC上のファイルを削除

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
- または、一時的なワークフローでデータベースを初期化することもできます

## 今後の使用

GitHub Actionsで自動実行されるため、PC上でプログラムを実行する必要はありません。

必要な場合のみ、ローカルにクローンして作業できます：

```powershell
git clone https://github.com/ユーザー名/リポジトリ名.git
cd リポジトリ名
```

