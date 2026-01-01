# GitHub Configuration設定ガイド

このガイドでは、GitHubリポジトリのSettings（設定）で必要なConfigurationを設定する方法を説明します。

## 設定が必要な項目

1. **Secrets（機密情報）**: Twitter API認証情報
2. **Variables（変数）**: 必要に応じて設定（オプション）

## Secretsの設定手順

### 1. GitHubリポジトリにアクセス

1. GitHubにログイン
2. リポジトリ（`blog-to-twitter-bot`など）を開く

### 2. Settingsを開く

1. リポジトリページの上部タブから「**Settings**」をクリック
2. 左サイドバーの「**Secrets and variables**」をクリック
3. 「**Actions**」をクリック

### 3. Secretsを追加

「**New repository secret**」ボタンをクリックして、以下のSecretsを1つずつ追加します。

#### 必須のSecrets（デフォルトアカウント用）

以下の5つのSecretsを追加してください：

| Secret名 | 説明 | 取得方法 |
|---------|------|---------|
| `TWITTER_API_KEY` | Twitter API Key | Twitter Developer Portal |
| `TWITTER_API_SECRET` | Twitter API Secret | Twitter Developer Portal |
| `TWITTER_ACCESS_TOKEN` | Access Token | Twitter Developer Portal |
| `TWITTER_ACCESS_TOKEN_SECRET` | Access Token Secret | Twitter Developer Portal |
| `TWITTER_BEARER_TOKEN` | Bearer Token | Twitter Developer Portal |

**追加手順（1つのSecretごと）:**
1. 「New repository secret」をクリック
2. 「Name」にSecret名を入力（例: `TWITTER_API_KEY`）
3. 「Secret」に実際の値を貼り付け
4. 「Add secret」をクリック

#### オプション: 別アカウント用のSecrets

365botGaryとpursahsgospelを別々のTwitterアカウントで運用する場合、以下のSecretsも追加します：

**365botGary用:**
- `TWITTER_365BOT_API_KEY`
- `TWITTER_365BOT_API_SECRET`
- `TWITTER_365BOT_ACCESS_TOKEN`
- `TWITTER_365BOT_ACCESS_TOKEN_SECRET`

**pursahsgospel用:**
- `TWITTER_PURSAHS_API_KEY`
- `TWITTER_PURSAHS_API_SECRET`
- `TWITTER_PURSAHS_ACCESS_TOKEN`
- `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`

### 4. Twitter Developer Portalで認証情報を取得

まだ取得していない場合：

1. [Twitter Developer Portal](https://developer.twitter.com/)にアクセス
2. ログイン（Xアカウントでログイン）
3. 「Projects & Apps」→ 既存のプロジェクトを選択、または新規作成
4. 「Keys and tokens」タブを開く
5. 以下の情報をコピー：
   - **API Key** → `TWITTER_API_KEY`
   - **API Key Secret** → `TWITTER_API_SECRET`
   - **Access Token** → `TWITTER_ACCESS_TOKEN`
   - **Access Token Secret** → `TWITTER_ACCESS_TOKEN_SECRET`
   - **Bearer Token** → `TWITTER_BEARER_TOKEN`（「Regenerate」ボタンから取得可能）

## 設定の確認

### Secretsの確認方法

1. Settings → Secrets and variables → Actions
2. 「Repository secrets」セクションに追加したSecretsが表示されます
3. 値は表示されません（セキュリティのため）が、名前と更新日時が表示されます

### 設定が正しいか確認

GitHub Actionsのワークフローを手動実行して確認できます：

1. リポジトリページの「**Actions**」タブを開く
2. 左サイドバーから「**Scheduled Blog Posts to Twitter**」を選択
3. 右上の「**Run workflow**」をクリック
4. 「Run workflow」ボタンをクリック
5. ワークフローが実行され、ログで認証エラーがないか確認

## トラブルシューティング

### 認証エラーが発生する場合

- Secretsの名前が正しいか確認（大文字・小文字を区別）
- 値が正しくコピーされているか確認（前後の空白がないか）
- Twitter Developer Portalでアプリが有効になっているか確認

### Secretsが見つからないエラー

- Secretsが正しい名前で追加されているか確認
- リポジトリレベルで追加されているか確認（Organizationレベルではない）

## セキュリティに関する注意事項

⚠️ **重要**:
- Secretsの値は一度追加すると表示できません（更新・削除のみ可能）
- SecretsはGitHub Actionsのワークフロー内でのみ使用できます
- Secretsの値はログに出力されません（自動的にマスクされます）
- `.env`ファイルはGitに含めないでください（`.gitignore`で除外されています）

## 次のステップ

Secretsの設定が完了したら：

1. GitHub Actionsのワークフローが自動実行されます（8時、14時、20時 JST）
2. 初回実行時に投稿データベースが自動的に初期化されます
3. 以降、1日3回自動的にブログ投稿がTwitterに投稿されます

詳細は `DEPLOYMENT.md` を参照してください。

