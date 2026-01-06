# 403 Forbidden エラーの詳細な原因調査

## 現在の状況

- 権限設定: 「Read and write」に設定済み
- Access Token: 再生成済み
- GitHub Secrets: 更新済み
- それでも403エラーが発生

## 考えられる他の原因

### 1. Bearer Tokenが未設定

ログに「*** ✗ 未設定」と表示されています。Bearer Tokenを設定してください。

**解決方法:**
- GitHub Secretsに `TWITTER_BEARER_TOKEN` を追加
- または `TWITTER_365BOT_BEARER_TOKEN` と `TWITTER_PURSAHS_BEARER_TOKEN` を追加

### 2. X側の承認/審査が必要

新しく作成したアプリや権限を変更したアプリは、X側の承認が必要な場合があります。

**確認方法:**
1. Twitter Developer Portalでアプリの状態を確認
2. 「Overview」タブでアプリの状態を確認
3. 「Pending approval」や「Under review」などの表示がないか確認

**解決方法:**
- 承認を待つ（通常、数時間〜数日）
- または、アプリの説明や使用目的をより詳細に記述

### 3. アプリが停止（SUSPENDED）されている

アプリが停止されている場合、403エラーが発生します。

**確認方法:**
1. Twitter Developer Portalでアプリの一覧を確認
2. アプリの状態が「SUSPENDED」になっていないか確認

**解決方法:**
- アプリを再アクティブ化する
- または、新しいアプリを作成

### 4. API v2のエンドポイントへのアクセス権限

API v2のエンドポイントにアクセスするには、追加の権限が必要な場合があります。

**確認方法:**
1. Twitter Developer Portalでアプリの「Settings」を確認
2. 「API v2」や「Elevated access」の設定を確認

**解決方法:**
- API v2へのアクセスを有効化
- または、Elevated accessを申請

### 5. 認証情報の形式の問題

認証情報に特殊文字や空白が含まれている場合、エラーが発生する可能性があります。

**確認方法:**
- GitHub Secretsの値に前後の空白がないか確認
- 値が正しくコピーされているか確認

**解決方法:**
- 認証情報を再コピーして設定
- 前後の空白を削除

### 6. レート制限

レート制限に達している場合、403エラーが発生する可能性があります。

**確認方法:**
- Twitter Developer Portalでレート制限の状態を確認
- エラーメッセージに「Rate limit」が含まれているか確認

**解決方法:**
- しばらく待ってから再試行

### 7. OAuth 1.0aとOAuth 2.0の混在

OAuth 1.0aとOAuth 2.0の認証情報が混在している場合、エラーが発生する可能性があります。

**確認方法:**
- 使用している認証情報がOAuth 1.0a用かOAuth 2.0用か確認

**解決方法:**
- OAuth 1.0a用の認証情報（API Key, API Secret, Access Token, Access Token Secret）を使用
- OAuth 2.0用の認証情報（Client ID, Client Secret）は使用しない

## 推奨される確認手順

### ステップ1: Bearer Tokenを設定

1. Twitter Developer Portalでアプリを開く
2. 「Keys and tokens」タブを開く
3. 「Bearer Token」をコピー
4. GitHub Secretsに設定

### ステップ2: アプリの状態を確認

1. Twitter Developer Portalでアプリの「Overview」タブを確認
2. アプリの状態が「Active」になっているか確認
3. 「Pending approval」などの表示がないか確認

### ステップ3: エラーメッセージの詳細を確認

GitHub Actionsのログで、より詳細なエラーメッセージを確認してください。

### ステップ4: 直接APIをテスト

curlコマンドで直接APIをテストして、認証情報が正しいか確認：

```bash
curl --request GET \
  --url 'https://api.x.com/2/users/me' \
  --header 'Authorization: Bearer YOUR_BEARER_TOKEN'
```

## トラブルシューティングのチェックリスト

- [ ] Bearer Tokenが設定されている
- [ ] アプリの状態が「Active」になっている
- [ ] アプリが「Pending approval」状態でない
- [ ] 認証情報に前後の空白がない
- [ ] OAuth 1.0a用の認証情報を使用している
- [ ] レート制限に達していない
- [ ] API v2へのアクセス権限がある




