# GitHub Secrets設定ガイド（詳細版）

このガイドでは、GitHub SecretsにTwitter API認証情報を設定する手順を詳しく説明します。

## 前提条件

- GitHubアカウントを持っていること
- X（Twitter）アカウントを持っていること
- Twitter Developer PortalでAPI認証情報を取得済みであること（下記手順を参照）

## ステップ1: GitHubリポジトリにアクセス

1. ブラウザでGitHubにログイン
2. リポジトリにアクセス: https://github.com/kazzyass17-commits/blog-to-twitter-bot

## ステップ2: Settingsを開く

1. リポジトリページの上部にあるタブから「**Settings**」をクリック
   - タブは「Code」「Issues」「Pull requests」「Actions」「Projects」「Wiki」「Security」「Insights」「Settings」の順に並んでいます
   - 一番右側の「Settings」をクリック

## ステップ3: Secrets and variables → Actions を開く

1. 左サイドバーを下にスクロール
2. 「**Secrets and variables**」をクリック
3. 「**Actions**」をクリック

## ステップ4: Secretsを追加

「**New repository secret**」ボタンをクリックして、以下のSecretsを1つずつ追加します。

### 必須のSecrets（5つ）

#### 1. TWITTER_API_KEY
1. 「New repository secret」をクリック
2. 「Name」に `TWITTER_API_KEY` と入力
3. 「Secret」にTwitter Developer Portalで取得したAPI Keyを貼り付け
4. 「Add secret」をクリック

#### 2. TWITTER_API_SECRET
1. 「New repository secret」をクリック
2. 「Name」に `TWITTER_API_SECRET` と入力
3. 「Secret」にTwitter Developer Portalで取得したAPI Secretを貼り付け
4. 「Add secret」をクリック

#### 3. TWITTER_ACCESS_TOKEN
1. 「New repository secret」をクリック
2. 「Name」に `TWITTER_ACCESS_TOKEN` と入力
3. 「Secret」にTwitter Developer Portalで取得したAccess Tokenを貼り付け
4. 「Add secret」をクリック

#### 4. TWITTER_ACCESS_TOKEN_SECRET
1. 「New repository secret」をクリック
2. 「Name」に `TWITTER_ACCESS_TOKEN_SECRET` と入力
3. 「Secret」にTwitter Developer Portalで取得したAccess Token Secretを貼り付け
4. 「Add secret」をクリック

#### 5. TWITTER_BEARER_TOKEN
1. 「New repository secret」をクリック
2. 「Name」に `TWITTER_BEARER_TOKEN` と入力
3. 「Secret」にTwitter Developer Portalで取得したBearer Tokenを貼り付け
4. 「Add secret」をクリック

### オプション: 別アカウント用のSecrets

365botGaryとpursahsgospelを別々のTwitterアカウントで運用する場合、以下のSecretsも追加します。

#### 365botGary用（4つ）
- `TWITTER_365BOT_API_KEY`
- `TWITTER_365BOT_API_SECRET`
- `TWITTER_365BOT_ACCESS_TOKEN`
- `TWITTER_365BOT_ACCESS_TOKEN_SECRET`

#### pursahsgospel用（4つ）
- `TWITTER_PURSAHS_API_KEY`
- `TWITTER_PURSAHS_API_SECRET`
- `TWITTER_PURSAHS_ACCESS_TOKEN`
- `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`

**注意**: 同じアカウントを使用する場合は、これらのSecretsは不要です。デフォルトのSecrets（上記5つ）が使用されます。

## ステップ5: 設定の確認

1. 「Secrets and variables」→「Actions」ページに戻る
2. 追加したSecretsが一覧に表示されていることを確認
3. Secret名の横に「●●●●●●●●」のようにマスクされた値が表示されます

## ステップ6: 接続テストの実行

1. リポジトリページの「**Actions**」タブをクリック
2. 左サイドバーから「**Test Twitter Connection**」を選択
3. 「**Run workflow**」ボタンをクリック
4. 実行結果を確認

## Twitter Developer Portalで認証情報を取得する方法（詳細手順）

### ステップ1: Twitter Developer Portalにアクセス

1. ブラウザで https://developer.twitter.com/ にアクセス
2. X（Twitter）アカウントでログイン
   - 右上の「Sign in」をクリック
   - Xアカウントでログイン

### ステップ2: Developerアカウントの申請（初回のみ）

初めてDeveloper Portalにアクセスする場合：

1. 「Apply for a developer account」または「Apply」をクリック
2. 利用目的を選択（例: "Making a bot" または "Exploring the API"）
3. 必要事項を入力して申請
4. 承認を待つ（通常、数分〜数時間）

### ステップ3: プロジェクトとアプリの作成

1. ログイン後、左サイドバーの「**Projects & Apps**」をクリック
2. 「**Create Project**」または「**+ Create Project**」をクリック
3. プロジェクト情報を入力：
   - **Project name**: 任意の名前（例: "Blog to Twitter Bot"）
   - **Use case**: 用途を選択（例: "Making a bot"）
4. 「Next」をクリック
5. アプリ名を入力（例: "blog-to-twitter-bot"）
6. 「Complete」をクリック

### ステップ4: 認証情報の取得

プロジェクト作成後、認証情報を取得します：

1. 作成したプロジェクトをクリック
2. アプリ名をクリック（または「Keys and tokens」タブを開く）
3. 「**Keys and tokens**」タブをクリック

#### 4-1. API Key and Secret を取得

1. 「**API Key and Secret**」セクションを探す
2. 「**Generate**」または「**Regenerate**」をクリック
3. 表示された値をコピー：
   - **API Key** → これを `TWITTER_API_KEY` として保存
   - **API Key Secret** → これを `TWITTER_API_SECRET` として保存
   - ⚠️ **重要**: この画面を閉じると再表示できません。必ずコピーしてください

#### 4-2. Access Token and Secret を取得

1. 「**Access Token and Secret**」セクションを探す
2. 「**Generate**」または「**Regenerate**」をクリック
3. 表示された値をコピー：
   - **Access Token** → これを `TWITTER_ACCESS_TOKEN` として保存
   - **Access Token Secret** → これを `TWITTER_ACCESS_TOKEN_SECRET` として保存
   - ⚠️ **重要**: この画面を閉じると再表示できません。必ずコピーしてください

#### 4-3. Bearer Token を取得

1. 「**Bearer Token**」セクションを探す
2. 「**Generate**」または「**Regenerate**」をクリック
3. 表示された値をコピー：
   - **Bearer Token** → これを `TWITTER_BEARER_TOKEN` として保存
   - ⚠️ **重要**: この画面を閉じると再表示できません。必ずコピーしてください

### ステップ5: アプリの権限設定

1. 「**Settings**」タブをクリック
2. 「**App permissions**」セクションを確認
3. 「**Read and Write**」または「**Read and write and Direct message**」を選択
   - ツイートを投稿するには「Read and Write」権限が必要です
4. 「**Save**」をクリック

### ステップ6: 認証情報の保存

取得した5つの認証情報を安全な場所に保存してください：

- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN`

⚠️ **セキュリティ注意事項**:
- これらの認証情報は他人に共有しないでください
- GitHubのコードや公開リポジトリに直接書かないでください
- GitHub Secretsにのみ保存してください

## トラブルシューティング

### Secretが見つからない
- Secret名のスペルを確認（大文字小文字も正確に）
- 「Secrets and variables」→「Actions」ページで一覧を確認

### 認証エラーが発生する
- Secretの値が正しくコピーされているか確認
- Twitter Developer Portalで認証情報が有効か確認
- アカウントの権限（Read and Write）を確認

### 接続テストが失敗する
- すべての必須Secretsが設定されているか確認
- GitHub Actionsのログを確認してエラーメッセージを確認

