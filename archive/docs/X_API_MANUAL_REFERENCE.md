# X（Twitter）API マニュアル参照

## 公式ドキュメント

### 1. X API v2 概要

**URL:** https://docs.x.com/x-api

**内容:**
- X API v2の概要と機能
- プログラムからXのデータにアクセスする方法
- 認証手順
- エンドポイントの詳細

### 2. X Developer Platform

**URL:** https://docs.x.com/

**内容:**
- X Developer Platform全体のガイド
- APIの利用方法
- 開発者向け情報

### 3. X API ポリシーとガイドライン

**URL:** https://help.x.com/ja/rules-and-policies/x-api

**内容:**
- X API利用に関するポリシー
- ガイドライン
- 利用規約

## 主要なエンドポイント

### 投稿関連

- **POST /2/tweets** - ツイートを投稿
  - レート制限: 15分間に300リクエスト（認証済みユーザー）
  - 最大文字数: 280文字（URLは23文字としてカウント）

### 認証

- OAuth 1.0a
- OAuth 2.0
- Bearer Token

## レート制限

### 投稿（POST /2/tweets）

- **認証済みユーザー**: 15分間に300リクエスト
- **リセット**: 15分間のスライディングウィンドウ

### エラーコード

- **403 Forbidden**: 権限の問題、アプリの状態、投稿内容による制限
- **429 Too Many Requests**: レート制限に達した

## 403エラーの原因

1. **アプリの権限設定**
   - 「Read and write」に設定されているか
   - 権限変更後にAccess Tokenを再生成したか

2. **アプリの状態**
   - 「Pending approval」（承認待ち）
   - 「SUSPENDED」（停止中）

3. **投稿内容**
   - テキストの長さによる制限
   - 投稿内容によるフィルタリング
   - URLを含む投稿に対する制限

4. **IPアドレス**
   - GitHub ActionsなどのIPアドレスがブロックされている可能性

## 現在のプロジェクトでの対応

### 実装済みの対策

1. **文字数制限の調整**
   - pursahsgospel: 190文字リミット（Twitterカウント）
   - 365botGary: 190文字リミット（Twitterカウント）

2. **レート制限管理**
   - `rate_limit_checker.py` - レート制限状態の管理
   - `rate_limit_state.json` - レート制限情報の記録

3. **エラーハンドリング**
   - 403エラーの詳細ログ
   - レート制限情報の記録

## 参考リンク

- [X API v2 - X](https://docs.x.com/x-api)
- [Welcome to the X Developer Platform - X](https://docs.x.com/)
- [X API ポリシーとガイドライン](https://help.x.com/ja/rules-and-policies/x-api)







