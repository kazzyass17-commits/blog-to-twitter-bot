# GitHub Actionsから接続テストを実行する方法

## 現在のワークフロー

`.github/workflows/test_connection.yml` が既に存在し、手動実行（workflow_dispatch）が可能です。

## 実行方法

### 方法1: GitHubのWeb UIから実行

1. GitHubリポジトリにアクセス
2. 「Actions」タブをクリック
3. 左側のメニューから「Test Twitter Connection」を選択
4. 「Run workflow」ボタンをクリック
5. ブランチを選択して「Run workflow」をクリック

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

1. IPアドレスとAPIアクセスの確認
2. 両アカウント（365botGary、pursahsgospel）の接続テスト

## 注意事項

- GitHub Actionsの実行には、リポジトリへのプッシュが必要です
- 実行結果はGitHub Actionsのログで確認できます
- 認証情報が正しく設定されているか確認してください







