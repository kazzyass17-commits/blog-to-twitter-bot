# 開発開始前の前提条件と注意点

このドキュメントでは、プログラム開発を開始する**前に**必要な前提条件と注意点をまとめています。

## ⚠️ 重要: 開発前に必ず確認すること

### 1. 必要なアカウント

#### GitHubアカウント
- **必須**: はい
- **取得方法**: https://github.com/ でアカウント作成
- **用途**: コードの保存、GitHub Actionsでの自動実行
- **コスト**: 無料

#### X（Twitter）アカウント
- **必須**: はい（投稿先のアカウント）
- **取得方法**: https://twitter.com/ または https://x.com/ でアカウント作成
- **用途**: 投稿先のアカウント
- **コスト**: 無料
- **注意**: 投稿するアカウント（365botGary、pursahsgospel）が必要

#### Twitter Developer Portalアカウント
- **必須**: はい
- **取得方法**: https://developer.twitter.com/ で申請
- **申請手順**: `GITHUB_SECRETS_SETUP.md` を参照
- **承認時間**: 数分〜数日（通常は数分で承認）
- **コスト**: 無料（Basicプランで十分）
- **注意**: 申請時に「Making a bot」を選択し、利用目的を具体的に記述する

### 2. Twitter API認証情報の取得

**開発前に必ず取得してください**

#### 必要な認証情報（5つ）
1. `TWITTER_API_KEY`
2. `TWITTER_API_SECRET`
3. `TWITTER_ACCESS_TOKEN`
4. `TWITTER_ACCESS_TOKEN_SECRET`
5. `TWITTER_BEARER_TOKEN`

#### 取得方法
- `GITHUB_SECRETS_SETUP.md` の「Twitter Developer Portalで認証情報を取得する方法」を参照
- 取得には数時間かかる場合があるため、開発前に取得しておくことを推奨

#### 注意点
- 認証情報は一度表示されると再表示できません。必ずコピーして保存してください
- 認証情報は他人に共有しないでください
- GitHub Secretsにのみ保存してください（コードに直接書かない）

### 3. Twitter APIの制限事項

#### レート制限
- **ツイート投稿**: 1時間あたり300ツイート（通常は十分）
- **アカウント情報取得**: 1時間あたり75回
- **注意**: レート制限に達すると、一定時間待機する必要があります

#### 文字数制限
- **ツイート本文**: 280文字
- **URL**: 23文字としてカウント（実際の長さに関わらず）
- **注意**: プログラムでは280文字以内に収まるように調整しています

#### アプリの権限
- **必須**: "Read and Write" 権限
- **設定場所**: Twitter Developer Portal → Settings → App permissions
- **注意**: 権限を変更した場合、Access Tokenを再生成する必要があります

### 4. GitHub Actionsの制限事項

#### 無料プランの制限
- **実行時間**: 1ヶ月あたり2,000分（約33時間）
- **同時実行**: 最大20ジョブ
- **注意**: 1日3回の投稿（約5分/回）なら、1ヶ月で約450分。無料プランで十分です

#### Secretsの制限
- **最大数**: リポジトリあたり100個
- **値の長さ**: 最大64KB
- **注意**: 必要なSecretsは5〜13個程度なので問題ありません

### 5. データベースの初期化

#### 初回実行時に必要
- 投稿データベース（`posts.db`）の初期化が必要
- 索引ページからURLを抽出してデータベースに保存
- **実行時間**: 約5〜10分（URL数による）

#### 注意点
- 初回実行は手動で実行する必要があります
- GitHub Actionsで自動実行されるように設定済み

### 6. スケジュール実行の設定

#### デフォルト設定
- **実行時間**: 8時、14時、20時（JST）
- **実行頻度**: 1日3回
- **注意**: GitHub Actionsのcron形式で設定されています

#### 変更方法
- `.github/workflows/scheduled_posts.yml` のcron設定を変更

### 7. ブログの構造について

#### 365botGary（FC2ブログ）
- **URL形式**: `http://notesofacim.blog.fc2.com/blog-entry-XXX.html`
- **索引ページ**: 4つの索引ページから365件のURLを抽出
- **注意**: 索引ページのURLが変更される可能性があります

#### pursahsgospel（Amebaブログ）
- **URL形式**: `https://ameblo.jp/pursahs-gospel/entry-XXXXX.html`
- **索引ページ**: 2つの索引ページから69件のURLを抽出
- **注意**: 索引ページのURLが変更される可能性があります

### 8. コスト

#### 無料で使用可能
- GitHub Actions（無料プラン）
- Twitter API（Basicプラン）
- データベース（SQLite、ファイルベース）

#### 有料になる場合
- GitHub Actionsの使用量が2,000分/月を超える場合（通常は超えません）
- Twitter APIの有料プランが必要な場合（通常は不要）

### 9. セキュリティに関する注意点

#### 認証情報の管理
- ⚠️ **絶対にGitにコミットしない**: `.env`ファイルは`.gitignore`に含まれています
- ⚠️ **GitHub Secretsにのみ保存**: コードに直接書かない
- ⚠️ **他人に共有しない**: 認証情報は機密情報です

#### データベースファイル
- `posts.db`は投稿履歴を含むため、必要に応じて`.gitignore`に追加
- 現在は`.gitignore`に含まれていませんが、公開リポジトリの場合は追加を推奨

### 10. 開発環境

#### 必要なソフトウェア
- **Python**: 3.11以上（推奨）
- **Git**: バージョン管理用
- **ブラウザ**: GitHub、Twitter Developer Portalへのアクセス用

#### 必要なPythonパッケージ
- `requirements.txt`に記載済み
- インストール: `pip install -r requirements.txt`

### 11. トラブルシューティングの準備

#### よくある問題
1. **認証エラー**: 認証情報の設定ミス、権限不足
2. **レート制限**: 投稿頻度が高すぎる
3. **URL抽出失敗**: ブログのHTML構造が変更された
4. **データベースエラー**: 初期化が完了していない

#### ログの確認
- プログラムはログを出力します
- GitHub Actionsのログでエラーを確認できます

## チェックリスト

開発を開始する前に、以下を確認してください：

- [ ] GitHubアカウントを作成済み
- [ ] X（Twitter）アカウントを作成済み（投稿先）
- [ ] Twitter Developer Portalでアカウント申請済み
- [ ] Twitter API認証情報を取得済み（5つすべて）
- [ ] GitHub Secretsに認証情報を設定済み
- [ ] Twitter APIのアプリ権限を「Read and Write」に設定済み
- [ ] Python 3.11以上がインストール済み
- [ ] Gitがインストール済み

## 次のステップ

前提条件が整ったら：

1. `GITHUB_SECRETS_SETUP.md` を参照してGitHub Secretsを設定
2. `test_twitter_connection.py` で接続テストを実行
3. `init_posts_from_index.py` でデータベースを初期化
4. `test_post.py --dry-run` で投稿内容を確認
5. GitHub Actionsで自動実行を開始

## 参考ドキュメント

- `GITHUB_SECRETS_SETUP.md`: GitHub Secretsの設定方法
- `DEPLOYMENT.md`: デプロイメント手順
- `README.md`: プロジェクトの概要
- `SETUP_GUIDE.md`: セットアップガイド

