# GitHub Actionsで接続テストを実行する手順

このガイドでは、GitHub ActionsでTwitter APIの接続テストを実行する方法を説明します。

## 前提条件

1. GitHubリポジトリにコードがプッシュされていること
2. GitHub SecretsにTwitter API認証情報が設定されていること

## ステップ1: GitHub Secretsの設定確認

接続テストを実行する前に、GitHub Secretsに認証情報が設定されているか確認してください。

### 確認方法

1. GitHubリポジトリにアクセス: https://github.com/kazzyass17-commits/blog-to-twitter-bot
2. 「**Settings**」タブをクリック
3. 左サイドバーの「**Secrets and variables**」→「**Actions**」をクリック
4. 以下のSecretsが設定されているか確認：

#### 必須のSecrets（5つ）
- [ ] `TWITTER_API_KEY`
- [ ] `TWITTER_API_SECRET`
- [ ] `TWITTER_ACCESS_TOKEN`
- [ ] `TWITTER_ACCESS_TOKEN_SECRET`
- [ ] `TWITTER_BEARER_TOKEN`

#### オプション: 別アカウント用（365botGaryとpursahsgospelを別アカウントで運用する場合）
- [ ] `TWITTER_365BOT_API_KEY`
- [ ] `TWITTER_365BOT_API_SECRET`
- [ ] `TWITTER_365BOT_ACCESS_TOKEN`
- [ ] `TWITTER_365BOT_ACCESS_TOKEN_SECRET`
- [ ] `TWITTER_PURSAHS_API_KEY`
- [ ] `TWITTER_PURSAHS_API_SECRET`
- [ ] `TWITTER_PURSAHS_ACCESS_TOKEN`
- [ ] `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`

**注意**: Secretsが設定されていない場合は、`GITHUB_SECRETS_SETUP.md`を参照して設定してください。

## ステップ2: 接続テストワークフローの実行

### 手順

1. **GitHubリポジトリにアクセス**
   - https://github.com/kazzyass17-commits/blog-to-twitter-bot

2. **「Actions」タブを開く**
   - リポジトリページの上部タブから「**Actions**」をクリック

3. **「Test Twitter Connection」ワークフローを選択**
   - 左サイドバーから「**Test Twitter Connection**」をクリック

4. **「Run workflow」ボタンをクリック**
   - 右上の「**Run workflow**」ボタンをクリック
   - ドロップダウンメニューが表示されます

5. **ワークフローを実行**
   - 「**Run workflow**」ボタンをクリック
   - ワークフローが実行を開始します

## ステップ3: 実行結果の確認

### 実行状況の確認

1. **ワークフローの実行一覧**
   - 「Actions」タブで実行中のワークフローが表示されます
   - 実行中のワークフローをクリックして詳細を確認

2. **各ステップの確認**
   - 「**Test Twitter connection**」ステップをクリック
   - ログが表示されます

### 成功時の表示

接続テストが成功すると、以下のようなログが表示されます：

```
✓ 接続成功！
  ユーザー名: @365botGary
  表示名: 365botGary
  ユーザーID: 1234567890
```

### 失敗時の確認

接続テストが失敗した場合、エラーメッセージが表示されます。よくあるエラー：

#### 認証エラー
```
✗ 認証エラー: API認証情報が無効です。
```
**対処法**: GitHub Secretsの認証情報を確認してください。

#### 認証情報が不足
```
✗ 認証情報が不足しています。
```
**対処法**: 必要なSecretsがすべて設定されているか確認してください。

#### レート制限
```
✗ レート制限: リクエストが多すぎます。
```
**対処法**: しばらく待ってから再試行してください。

## トラブルシューティング

### Secretsが設定されていない

**症状**: 認証情報が不足しているエラー

**対処法**:
1. `GITHUB_SECRETS_SETUP.md`を参照してSecretsを設定
2. すべての必須Secretsが設定されているか確認

### 認証情報が間違っている

**症状**: 認証エラー

**対処法**:
1. Twitter Developer Portalで認証情報を再確認
2. GitHub Secretsの値を再設定
3. 前後の空白がないか確認

### ワークフローが実行されない

**症状**: 「Run workflow」ボタンが表示されない

**対処法**:
1. リポジトリの権限を確認（管理者権限が必要）
2. ワークフローファイル（`.github/workflows/test_connection.yml`）が存在するか確認

## 次のステップ

接続テストが成功したら：

1. **投稿データベースの初期化**
   - GitHub Actionsで「Scheduled Blog Posts to Twitter」ワークフローを手動実行
   - 初回実行時にデータベースが自動的に初期化されます

2. **自動投稿の開始**
   - スケジュール実行（8時、14時、20時 JST）が自動的に開始されます

## 参考ドキュメント

- `GITHUB_SECRETS_SETUP.md`: GitHub Secretsの設定方法
- `CREDENTIALS_CHECKLIST.md`: 必要な認証情報のチェックリスト
- `PREREQUISITES.md`: 開発開始前の前提条件




