# 403 Forbidden エラーの解決方法

## エラーの原因

403 Forbiddenエラーは、通常以下のいずれかが原因です：

1. **アプリの権限が「Read and Write」に設定されていない**
2. **権限変更後にAccess Tokenを再生成していない**
3. **Bearer Tokenが正しく設定されていない**

## 解決方法

### ステップ1: アプリの権限設定を確認

#### 365botGaryアカウント用

1. Twitter Developer Portalにアクセス
2. 「2006671045663797250365botGary」アプリを開く
3. 「**Settings**」タブをクリック
4. 「**App permissions**」セクションを確認
5. 「**Read and Write**」または「**Read and write and Direct message**」が選択されているか確認
6. 選択されていない場合は選択して「**Save**」をクリック

#### pursahsgospelアカウント用

1. Twitter Developer Portalにアクセス
2. pursahsgospel用のアプリを開く
3. 「**Settings**」タブをクリック
4. 「**App permissions**」セクションを確認
5. 「**Read and Write**」または「**Read and write and Direct message**」が選択されているか確認
6. 選択されていない場合は選択して「**Save**」をクリック

### ステップ2: Access Tokenを再生成

**重要**: 権限を変更した場合、Access TokenとAccess Token Secretを再生成する必要があります。

#### 365botGaryアカウント用

1. 「**Keys and tokens**」タブを開く
2. 「**Access Token and Secret**」セクションを探す
3. 「**Regenerate**」ボタンをクリック
4. 新しいAccess TokenとAccess Token Secretをコピー
5. GitHub Secretsの `TWITTER_365BOT_ACCESS_TOKEN` と `TWITTER_365BOT_ACCESS_TOKEN_SECRET` を更新

#### pursahsgospelアカウント用

1. 「**Keys and tokens**」タブを開く
2. 「**Access Token and Secret**」セクションを探す
3. 「**Regenerate**」ボタンをクリック
4. 新しいAccess TokenとAccess Token Secretをコピー
5. GitHub Secretsの `TWITTER_PURSAHS_ACCESS_TOKEN` と `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET` を更新

### ステップ3: Bearer Tokenの確認

Bearer Tokenは表示されていませんが、設定されている可能性があります。念のため確認：

1. GitHub Secretsで `TWITTER_365BOT_BEARER_TOKEN` と `TWITTER_PURSAHS_BEARER_TOKEN` が設定されているか確認
2. 設定されていない場合は、Twitter Developer Portalから取得して設定

### ステップ4: 接続テストを再実行

1. GitHub Actionsで「Test Twitter Connection」ワークフローを再実行
2. エラーが解消されているか確認

## チェックリスト

- [ ] 365botGaryアプリの権限が「Read and Write」に設定されている
- [ ] pursahsgospelアプリの権限が「Read and Write」に設定されている
- [ ] 365botGaryアプリのAccess Tokenを再生成済み
- [ ] pursahsgospelアプリのAccess Tokenを再生成済み
- [ ] GitHub SecretsのAccess Tokenを更新済み
- [ ] Bearer Tokenが設定されている
- [ ] 接続テストを再実行済み

## それでも解決しない場合

1. **認証情報を再確認**
   - GitHub Secretsの値が正しくコピーされているか確認
   - 前後の空白がないか確認

2. **アプリの状態を確認**
   - アプリが停止（SUSPENDED）されていないか確認
   - アプリが有効になっているか確認

3. **ログを確認**
   - GitHub Actionsのログで詳細なエラーメッセージを確認

