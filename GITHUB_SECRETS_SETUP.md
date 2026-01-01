# GitHub Secrets設定ガイド（詳細版）

このガイドでは、GitHub SecretsにTwitter API認証情報を設定する手順を詳しく説明します。

## 前提条件

- GitHubアカウントを持っていること
- Twitter Developer PortalでAPI認証情報を取得済みであること

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

## Twitter Developer Portalで認証情報を取得する方法

もしTwitter API認証情報をまだ取得していない場合：

1. https://developer.twitter.com/ にアクセス
2. アカウントを作成またはログイン
3. 「Projects & Apps」→「Create Project」でプロジェクトを作成
4. 「Keys and tokens」タブで認証情報を取得
   - API Key and Secret
   - Access Token and Secret
   - Bearer Token

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

