# GitHubからX（Twitter）へ投稿する方法

## 概要

GitHub Actionsを使用して、GitリポジトリからX（旧Twitter）へ自動投稿する方法があります。

## 実装方法

### 1. GitHub Actionsを使用した自動投稿

GitHub Actionsを活用すると、リポジトリ内の特定のイベント（記事の追加や更新など）をトリガーとして、Xに自動的に投稿を行うことが可能です。

**参考例：**
- Zennで記事を公開した際に自動でXに投稿するGitHub Actions
- 記事の新規公開や公開設定の変更を検知
- OpenAIを利用してリード文を生成し、Xへ投稿

**参考リンク：**
- [Zenn記事を自動でXに投稿するGitHub Actions](https://zenn.dev/kannna5296/articles/2025-06-19-auto-x-post-action)

### 2. 実装の流れ

1. **GitHub Actionsワークフローの作成**
   - `.github/workflows/` ディレクトリにワークフローファイルを作成
   - トリガーイベントを設定（push、scheduleなど）

2. **X API認証情報の設定**
   - GitHub SecretsにX APIの認証情報を保存
   - API Key、API Secret、Access Token、Access Token Secret

3. **投稿スクリプトの実装**
   - Python、Node.js、その他の言語でX APIを呼び出すスクリプトを作成
   - Tweepy（Python）やTwitter API v2 SDKを使用

4. **ワークフローでの実行**
   - ワークフロー内でスクリプトを実行
   - 認証情報を環境変数として渡す

## 現在のプロジェクトでの実装状況

現在のプロジェクトでは、以下のファイルでGitHub Actionsを使用した投稿が実装されています：

- `.github/workflows/scheduled_posts.yml` - スケジュール実行
- `.github/workflows/test_connection.yml` - 接続テスト

## 注意事項

- X APIのレート制限に注意
- 認証情報の管理（GitHub Secretsを使用）
- IPアドレスがブロックされる可能性（GitHub ActionsのIPアドレス）




