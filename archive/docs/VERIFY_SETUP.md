# GitHub Secrets設定の確認と接続テスト

## ステップ3: 設定の確認

### 確認方法

1. **GitHubリポジトリにアクセス**
   - https://github.com/kazzyass17-commits/blog-to-twitter-bot

2. **Settings → Secrets and variables → Actions を開く**
   - 「Settings」タブをクリック
   - 左サイドバーの「Secrets and variables」→「Actions」をクリック

3. **設定されているSecretsを確認**
   
   以下の10個のSecretsが表示されていることを確認してください：

   **365botGary用（5つ）:**
   - `TWITTER_365BOT_API_KEY`
   - `TWITTER_365BOT_API_SECRET`
   - `TWITTER_365BOT_ACCESS_TOKEN`
   - `TWITTER_365BOT_ACCESS_TOKEN_SECRET`
   - `TWITTER_365BOT_BEARER_TOKEN`（オプション）

   **pursahsgospel用（5つ）:**
   - `TWITTER_PURSAHS_API_KEY`
   - `TWITTER_PURSAHS_API_SECRET`
   - `TWITTER_PURSAHS_ACCESS_TOKEN`
   - `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`
   - `TWITTER_PURSAHS_BEARER_TOKEN`（オプション）

   **注意**: 値は表示されません（セキュリティのため）が、名前と更新日時が表示されます。

## ステップ4: 接続テストの実行

### 手順

1. **GitHubリポジトリの「Actions」タブを開く**
   - リポジトリページの上部タブから「**Actions**」をクリック

2. **「Test Twitter Connection」ワークフローを選択**
   - 左サイドバーから「**Test Twitter Connection**」をクリック

3. **「Run workflow」ボタンをクリック**
   - 右上の「**Run workflow**」ボタンをクリック
   - ドロップダウンメニューが表示されます

4. **ワークフローを実行**
   - 「**Run workflow**」ボタンをクリック
   - ワークフローが実行を開始します

### 実行結果の確認

#### 成功時の表示

接続テストが成功すると、以下のようなログが表示されます：

```
✓ 接続成功！
  ユーザー名: @365botGary
  表示名: 365botGary
  ユーザーID: 1234567890
```

```
✓ 接続成功！
  ユーザー名: @pursahsgospel
  表示名: pursahsgospel
  ユーザーID: 1234567890
```

#### 失敗時の確認

接続テストが失敗した場合、エラーメッセージが表示されます。よくあるエラー：

**認証エラー**
```
✗ 認証エラー: API認証情報が無効です。
```
**対処法**: GitHub Secretsの認証情報を確認してください。

**認証情報が不足**
```
✗ 認証情報が不足しています。
```
**対処法**: 必要なSecretsがすべて設定されているか確認してください。

## 次のステップ

接続テストが成功したら：

1. **投稿データベースの初期化**
   - GitHub Actionsで「Scheduled Blog Posts to Twitter」ワークフローを手動実行
   - 初回実行時にデータベースが自動的に初期化されます

2. **自動投稿の開始**
   - スケジュール実行（8時、14時、20時 JST）が自動的に開始されます




