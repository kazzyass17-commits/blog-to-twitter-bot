# デプロイメントガイド

このガイドでは、ブログ→Twitter自動投稿ボットをGitHub上で常時稼働させる方法を説明します。

## GitHub Actionsを使用したデプロイメント

### 1. リポジトリの準備

1. GitHubにリポジトリを作成
2. コードをプッシュ

```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git push -u origin main
```

### 2. GitHub Secretsの設定

リポジトリのSettings → Secrets and variables → Actions で以下のSecretsを設定します：

#### 必須のSecrets（デフォルトアカウント用）
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN`

#### オプション（別アカウントを使用する場合）
- `TWITTER_365BOT_API_KEY`
- `TWITTER_365BOT_API_SECRET`
- `TWITTER_365BOT_ACCESS_TOKEN`
- `TWITTER_365BOT_ACCESS_TOKEN_SECRET`
- `TWITTER_PURSAHS_API_KEY`
- `TWITTER_PURSAHS_API_SECRET`
- `TWITTER_PURSAHS_ACCESS_TOKEN`
- `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`

### 3. 初回セットアップ（投稿データベースの初期化）

初回は、ローカルまたはGitHub Actionsで投稿データベースを初期化する必要があります。

#### 方法1: ローカルで初期化（推奨）

```powershell
# 環境変数を設定
copy env.example.txt .env
# .envファイルを編集して認証情報を入力

# 投稿データベースを初期化
python init_posts.py

# データベースファイルをコミット（オプション）
git add posts.db
git commit -m "Initialize posts database"
git push
```

#### 方法2: GitHub Actionsで初期化

一時的なワークフローファイルを作成して実行：

```yaml
# .github/workflows/init_posts.yml
name: Initialize Posts Database

on:
  workflow_dispatch:

jobs:
  init:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - name: Create .env file
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          # ... 他の環境変数も同様に設定
        run: |
          # .envファイルを作成（上記のワークフローファイルと同様）
      - run: python init_posts.py
      - uses: actions/upload-artifact@v3
        with:
          name: posts-db
          path: posts.db
```

### 4. 実行スケジュール

GitHub Actionsのワークフローは以下のスケジュールで実行されます：

- **8時JST** (23:00 UTC) - 毎日
- **14時JST** (05:00 UTC) - 毎日  
- **20時JST** (11:00 UTC) - 毎日

各時間帯で、データベースから未投稿の投稿をランダムに1件選択して投稿します。

### 5. データベースの永続化

GitHub Actionsでは、`posts.db`ファイルをキャッシュに保存して永続化します。
これにより、投稿履歴が保持され、1巡するまで同じ投稿は再投稿されません。

### 6. ワークフローの確認

GitHubリポジトリの「Actions」タブで、ワークフローの実行状況を確認できます。

## 注意事項

### GitHub Actionsの制限

1. **無料プランの制限**
   - 月間2,000分の実行時間
   - 1日3回の実行で約90分/月（1回あたり約30分として）
   - 十分な余裕があります

2. **データベースの永続化**
   - GitHub Actionsのキャッシュは90日間保持されます
   - 長期間運用する場合は、定期的にデータベースをバックアップすることを推奨します

3. **ランダム時間について**
   - GitHub Actionsのcronは分単位のランダム実行ができません
   - そのため、固定時間（8:00, 14:00, 20:00）で実行されます
   - ランダム性は、投稿選択時に実現されています

### 代替案

より柔軟なスケジューリングが必要な場合：

1. **AWS Lambda + EventBridge**
   - より柔軟なスケジューリング
   - サーバーレスで常時稼働
   - 無料枠あり

2. **Google Cloud Functions + Cloud Scheduler**
   - 同様に柔軟なスケジューリング
   - サーバーレス

3. **Heroku Scheduler**
   - 簡単な設定
   - 有料プランが必要

4. **VPS（Raspberry Pi、Vultr、DigitalOceanなど）**
   - 完全な制御が可能
   - `schedule.py`を直接実行

## トラブルシューティング

### 投稿が実行されない

1. GitHub Actionsのログを確認
2. Secretsが正しく設定されているか確認
3. データベースが正しく初期化されているか確認

### データベースがリセットされる

- GitHub Actionsのキャッシュが期限切れになる可能性があります
- 定期的にデータベースをバックアップすることを推奨します

### 同じ投稿が繰り返される

- データベースの初期化が正しく行われていない可能性があります
- `init_posts.py`を再実行してください


