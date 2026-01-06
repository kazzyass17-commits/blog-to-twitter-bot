# GitHub Actionsから接続テストを実行する手順

## 現在の状況

- **リポジトリ**: https://github.com/kazzyass17-commits/blog-to-twitter-bot.git
- **ワークフロー**: `.github/workflows/test_connection.yml` が存在
- **実行方法**: 手動実行（workflow_dispatch）が可能

## 実行手順

### 方法1: GitHubのWeb UIから実行（推奨）

1. **GitHubリポジトリにアクセス**
   - https://github.com/kazzyass17-commits/blog-to-twitter-bot

2. **Actionsタブを開く**
   - リポジトリページの上部メニューから「Actions」をクリック

3. **ワークフローを選択**
   - 左側のメニューから「Test Twitter Connection」を選択

4. **手動実行**
   - 右側の「Run workflow」ボタンをクリック
   - ブランチを選択（通常は `separate-accounts` または `main`）
   - 「Run workflow」をクリック

5. **実行結果を確認**
   - 実行が開始されると、実行履歴に表示されます
   - 実行をクリックして、ログを確認できます

### 方法2: GitHub CLIから実行

```bash
gh workflow run test_connection.yml
```

## 必要なGitHub Secrets

以下のSecretsが設定されている必要があります：

- `TWITTER_365BOT_API_KEY`
- `TWITTER_365BOT_API_SECRET`
- `TWITTER_365BOT_ACCESS_TOKEN`
- `TWITTER_365BOT_ACCESS_TOKEN_SECRET`
- `TWITTER_365BOT_BEARER_TOKEN`
- `TWITTER_PURSAHS_API_KEY`
- `TWITTER_PURSAHS_API_SECRET`
- `TWITTER_PURSAHS_ACCESS_TOKEN`
- `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`
- `TWITTER_PURSAHS_BEARER_TOKEN`

## 実行内容

1. **IPアドレスとAPIアクセスの確認**
   - `check_ip_blocking.py` を実行

2. **接続テスト**
   - `test_twitter_connection.py --account both` を実行
   - 両アカウント（365botGary、pursahsgospel）の接続をテスト

## 注意事項

- GitHub Actionsの実行には、リポジトリへのプッシュが必要です
- 実行結果はGitHub Actionsのログで確認できます
- 認証情報が正しく設定されているか確認してください







