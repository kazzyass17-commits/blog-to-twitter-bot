# 認証情報を再取得する方法

## 認証情報を再表示する方法

Twitter Developer Portalでは、一度表示した認証情報は再表示できません。**再生成する必要があります**。

## 再取得手順

### ステップ1: Twitter Developer Portalにアクセス

1. https://developer.twitter.com/ にアクセス
2. Xアカウントでログイン

### ステップ2: pursahsgospel用のアプリを開く

1. 左サイドバーの「**Projects & Apps**」をクリック
2. pursahsgospel用のプロジェクトまたはアプリを探す
3. アプリをクリック

### ステップ3: 「Keys and tokens」タブを開く

1. アプリを開いたら、「**Keys and tokens**」タブをクリック

### ステップ4: 認証情報を再生成

#### API Key and Secret

1. 「**API Key and Secret**」セクションを探す
2. 「**Regenerate**」ボタンをクリック
3. 表示された値をコピー：
   - **API Key** → `TWITTER_PURSAHS_API_KEY`
   - **API Key Secret** → `TWITTER_PURSAHS_API_SECRET`
   - ⚠️ **重要**: この画面を閉じると再表示できません。必ずコピーしてください

#### Access Token and Secret

1. 「**Access Token and Secret**」セクションを探す
2. 「**Regenerate**」ボタンをクリック
3. 表示された値をコピー：
   - **Access Token** → `TWITTER_PURSAHS_ACCESS_TOKEN`
   - **Access Token Secret** → `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET`
   - ⚠️ **重要**: この画面を閉じると再表示できません。必ずコピーしてください

#### Bearer Token

1. 「**Bearer Token**」セクションを探す
2. 「**Regenerate**」ボタンをクリック（必要に応じて）
3. 表示された値をコピー：
   - **Bearer Token** → `TWITTER_PURSAHS_BEARER_TOKEN`
   - ⚠️ **重要**: この画面を閉じると再表示できません。必ずコピーしてください

## 注意事項

### 再生成の影響

- **Access Tokenを再生成すると、以前のAccess Tokenは無効になります**
- 既に設定されている認証情報も更新する必要があります

### コピーする場所

1. **メモ帳やテキストエディタに一時的に保存**
2. **.envファイルに貼り付け**
3. **GitHub Secretsに設定**（GitHub Actionsで使用する場合）

## 認証情報の確認方法

### 現在の.envファイルを確認

`.env`ファイルを開いて、現在設定されている認証情報を確認できます。

**注意**: `.env`ファイルには機密情報が含まれているため、他人に見せないでください。

### 接続テストで確認

認証情報を更新した後、接続テストを実行して確認：

```powershell
cd c:\Users\kazz17\.cursor\blog-to-twitter-bot-temp
python test_twitter_connection.py --account pursahs
```

## トラブルシューティング

### 認証情報が見つからない

- 「Keys and tokens」タブを確認
- アプリが正しく選択されているか確認

### 再生成ボタンが表示されない

- アプリの権限を確認
- アプリの状態が「Active」になっているか確認

### 認証エラーが続く

- 認証情報が正しくコピーされているか確認
- 前後の空白がないか確認
- Access Tokenを再生成した場合、すべての認証情報を更新する必要があります

