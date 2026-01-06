# GitHub Actionsで接続テストを実行する方法

## 前提条件

- GitHub Secretsに認証情報が設定されていること
- pursahsgospel用の認証情報も更新されていること

## ステップ1: GitHub Secretsの更新確認

pursahsgospel用の認証情報をGitHub Secretsに更新してください：

1. https://github.com/kazzyass17-commits/blog-to-twitter-bot にアクセス
2. 「Settings」→「Secrets and variables」→「Actions」を開く
3. 以下のSecretsを更新：

### pursahsgospel用のSecrets（5つ）

- `TWITTER_PURSAHS_API_KEY` = `PCotoQSfRLlBPoWgcBA7455y1`
- `TWITTER_PURSAHS_API_SECRET` = `5H4mO4WXSAyadI7yQqlXrOR9DgCm1UOEpZqfPGWlzZTEgCG6Iv`
- `TWITTER_PURSAHS_ACCESS_TOKEN` = `2416625168-HjSU1zutJdPiIkViltErroLVz81VusJBnGlP9BX`
- `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET` = `DyVPAj1Lj7Ebvi6kR2y1xqi1ES49B3XdzuOxLfDkNil7M`
- `TWITTER_PURSAHS_BEARER_TOKEN` = `AAAAAAAAAAAAAAAAAAAAAP6u6gEAAAAANFP7mlTxPI1BeRpCpaJDtja2HB0%3DV443mkbthkCI5NC5ubm0l0AZYHL0YAIC9hJBDC5qoT9Q1pHHYL`

## ステップ2: GitHub Actionsで接続テストを実行

1. **GitHubリポジトリにアクセス**
   - https://github.com/kazzyass17-commits/blog-to-twitter-bot

2. **「Actions」タブを開く**
   - リポジトリページの上部タブから「Actions」をクリック

3. **「Test Twitter Connection」ワークフローを選択**
   - 左サイドバーから「Test Twitter Connection」をクリック

4. **「Run workflow」ボタンをクリック**
   - 右上の「Run workflow」ボタンをクリック
   - ドロップダウンメニューが表示されます

5. **ワークフローを実行**
   - 「Run workflow」ボタンをクリックして実行

## ステップ3: 実行結果の確認

### 成功時の表示

両方のアカウントで接続が成功すると、以下のようなログが表示されます：

```
✓ 接続成功！
  ユーザー名: @365botGary
  表示名: 365botGary
  ユーザーID: 2420551951
```

```
✓ 接続成功！
  ユーザー名: @pursahsgospel
  表示名: pursahsgospel
  ユーザーID: 2416625168
```

### 失敗時の確認

#### 403 Forbiddenエラー

- **症状**: 403 Forbidden + HTMLレスポンス
- **原因**: GitHub ActionsのIPアドレスがブロックされている可能性
- **対処法**: しばらく待ってから再試行

#### 401 Unauthorizedエラー

- **症状**: 401 Unauthorized
- **原因**: 認証情報が無効または期限切れ
- **対処法**: GitHub Secretsの認証情報を確認・更新

## 予想される結果

### ローカル環境では成功、GitHub Actionsでは失敗する可能性

- **ローカル環境**: 両方のアカウントで接続成功 ✅
- **GitHub Actions**: 403 Forbiddenエラーの可能性 ⚠️

これは、GitHub ActionsのIPアドレスがブロックされている可能性が高いです。

## 対処法

### 1. 時間を置いて再試行

1時間〜数時間待ってから、GitHub Actionsで接続テストを再実行してください。

### 2. ローカルPCでの運用を継続

GitHub ActionsのIPブロック問題が解決するまで、ローカルPCでの運用を継続してください。

### 3. プロキシサーバーを使用（利用規約を確認）

プロキシサーバーを使用する方法もありますが、利用規約を確認してください。




