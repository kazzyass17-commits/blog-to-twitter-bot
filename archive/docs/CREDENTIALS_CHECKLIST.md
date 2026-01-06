# 必要な認証情報のチェックリスト

## ✅ 必要な認証情報（5つ）

Twitter Developer Portalで取得する必要がある認証情報は**5つ**です：

### 1. API Key
- **環境変数名**: `TWITTER_API_KEY`
- **GitHub Secret名**: `TWITTER_API_KEY`
- **取得場所**: Twitter Developer Portal → Keys and tokens → API Key and Secret
- **表示名**: "API Key" または "Consumer Key"

### 2. API Secret
- **環境変数名**: `TWITTER_API_SECRET`
- **GitHub Secret名**: `TWITTER_API_SECRET`
- **取得場所**: Twitter Developer Portal → Keys and tokens → API Key and Secret
- **表示名**: "API Key Secret" または "Consumer Secret"

### 3. Access Token
- **環境変数名**: `TWITTER_ACCESS_TOKEN`
- **GitHub Secret名**: `TWITTER_ACCESS_TOKEN`
- **取得場所**: Twitter Developer Portal → Keys and tokens → Access Token and Secret
- **表示名**: "Access Token"

### 4. Access Token Secret
- **環境変数名**: `TWITTER_ACCESS_TOKEN_SECRET`
- **GitHub Secret名**: `TWITTER_ACCESS_TOKEN_SECRET`
- **取得場所**: Twitter Developer Portal → Keys and tokens → Access Token and Secret
- **表示名**: "Access Token Secret"

### 5. Bearer Token
- **環境変数名**: `TWITTER_BEARER_TOKEN`
- **GitHub Secret名**: `TWITTER_BEARER_TOKEN`
- **取得場所**: Twitter Developer Portal → Keys and tokens → Bearer Token
- **表示名**: "Bearer Token"

## ❌ 不要な情報

以下の情報は**必要ありません**：

- ❌ Developer ID
- ❌ Project ID
- ❌ App ID
- ❌ User ID
- ❌ その他のID

## 📋 チェックリスト

### Twitter Developer Portalで確認

- [ ] API Key を取得済み
- [ ] API Secret を取得済み
- [ ] Access Token を取得済み
- [ ] Access Token Secret を取得済み
- [ ] Bearer Token を取得済み
- [ ] すべての認証情報を安全な場所に保存済み

### GitHub Secretsで確認

- [ ] `TWITTER_API_KEY` を設定済み
- [ ] `TWITTER_API_SECRET` を設定済み
- [ ] `TWITTER_ACCESS_TOKEN` を設定済み
- [ ] `TWITTER_ACCESS_TOKEN_SECRET` を設定済み
- [ ] `TWITTER_BEARER_TOKEN` を設定済み

### オプション: 別アカウント用（365botGaryとpursahsgospelを別アカウントで運用する場合）

- [ ] `TWITTER_365BOT_API_KEY` を設定済み
- [ ] `TWITTER_365BOT_API_SECRET` を設定済み
- [ ] `TWITTER_365BOT_ACCESS_TOKEN` を設定済み
- [ ] `TWITTER_365BOT_ACCESS_TOKEN_SECRET` を設定済み
- [ ] `TWITTER_PURSAHS_API_KEY` を設定済み
- [ ] `TWITTER_PURSAHS_API_SECRET` を設定済み
- [ ] `TWITTER_PURSAHS_ACCESS_TOKEN` を設定済み
- [ ] `TWITTER_PURSAHS_ACCESS_TOKEN_SECRET` を設定済み

## 🔍 認証情報の確認方法

### 方法1: 接続テストを実行

```powershell
python test_twitter_connection.py --account both
```

### 方法2: アカウント情報を確認

```powershell
python check_account_info.py --account both
```

### 方法3: API v2接続テスト

```powershell
python test_api_v2.py --method bearer
```

## ⚠️ 重要な注意事項

1. **認証情報は一度表示されると再表示できません**
   - 必ずコピーして安全な場所に保存してください
   - 画面を閉じる前に確認してください

2. **認証情報は機密情報です**
   - 他人に共有しないでください
   - コードに直接書かないでください
   - GitHub Secretsにのみ保存してください

3. **Bearer Tokenだけでは投稿できません**
   - 投稿には Access Token と Access Token Secret が必要です
   - Bearer Token は読み取り専用の操作に使用されます

## 📝 取得手順の詳細

詳細な取得手順は `GITHUB_SECRETS_SETUP.md` の「Twitter Developer Portalで認証情報を取得する方法」を参照してください。




