# GitHub Actionsでの接続テスト実行方法

## 前提条件

GitHub Secretsに以下の認証情報が設定されている必要があります：

### 365botGary用
- `TWITTER_365BOT_API_KEY`
- `TWITTER_365BOT_API_SECRET`
- `TWITTER_365BOT_ACCESS_TOKEN`（新しく再生成したもの）
- `TWITTER_365BOT_ACCESS_TOKEN_SECRET`（新しく再生成したもの）
- `TWITTER_365BOT_BEARER_TOKEN`（新しく再生成したもの）

### pursahsgospel用
- `TWITTER_PURSAHS_API_KEY`
- `TWITTER_PURSAHS_API_SECRET`
- `TWITTER_PURSAHS_ACCESS_TOKEN`（新しく再生成したもの）
- `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`（新しく再生成したもの）
- `TWITTER_PURSAHS_BEARER_TOKEN`（新しく再生成したもの）

## 実行手順

### ステップ1: GitHub Secretsを更新

1. GitHubリポジトリにアクセス
2. 「Settings」→「Secrets and variables」→「Actions」を開く
3. 上記の認証情報を更新（特にAccess Token、Access Token Secret、Bearer Token）

### ステップ2: ワークフローを実行

1. GitHubリポジトリの「Actions」タブを開く
2. 左サイドバーから「Test Twitter Connection」を選択
3. 右上の「Run workflow」ボタンをクリック
4. 「Run workflow」をクリックして実行

### ステップ3: 結果を確認

実行が完了したら、ログを確認してください：

- ✅ **成功**: 両方のアカウントで接続成功
- ❌ **403エラー**: GitHub ActionsのIPブロックの可能性
- ❌ **401エラー**: 認証情報が無効（Secretsを確認）

## 現在の.envファイルの認証情報

以下の認証情報が正しく設定されていることを確認してください：

### 365botGary
- Access Token: `2420551951-DlN8mS3NObj4FYKljf4LdF52HgK3KCMs3nl2DyV`
- Access Token Secret: `QTqpRwxh2O9XWVvzFwFqvColVzDv9GPCV92vxXBHm1q4k`
- Bearer Token: `AAAAAAAAAAAAAAAAAAAAAJGu6gEAAAAAJHuRCtInvD0vK%2FiosxvsOAAYJCg%3DrxwTrNig2h07R2AAbSgXzVlg2HHx67OR8gF4Enb2SrjWGnVcoc`

### pursahsgospel
- Access Token: `2416625168-oaHuPjoGK4PrXE7sOFZOQ0PQEzSHSUkuHfERO3G`
- Access Token Secret: `nWKeaynrv3ZZWzELUNz8P3CQ1kr7hXIqpSpbGY1r3bEm3`
- Bearer Token: `AAAAAAAAAAAAAAAAAAAAAP6u6gEAAAAAF9LMYEb3NR7X%2BGxeCfi1Kfp0Kpk%3DAAs8SFlimPxKrn5KOOud03vbJBFgM1NVrfPsuriuhuYFPq0bUu`

## 注意事項

- GitHub Secretsは一度設定すると値が表示されません
- 更新する場合は、新しい値を入力して「Update secret」をクリック
- すべての認証情報を更新してから、接続テストを実行してください










