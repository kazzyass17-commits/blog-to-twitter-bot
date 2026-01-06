# ローカル環境で接続テストを実行する方法

## 前提条件

- Python 3.11以上がインストールされていること
- 依存パッケージがインストールされていること

## ステップ1: 依存パッケージのインストール

```powershell
cd c:\Users\kazz17\.cursor\blog-to-twitter-bot-temp
python -m pip install -r requirements.txt
```

## ステップ2: .envファイルの作成（一時的）

**注意**: これは一時的なテスト用です。テスト後は削除してください。

```powershell
# env.example.txtをコピー
copy env.example.txt .env
```

## ステップ3: .envファイルの編集

`.env`ファイルをメモ帳などで開いて、以下の認証情報を入力してください：

### 365botGaryアカウント用

```env
TWITTER_365BOT_API_KEY=lcm2kwFqZ66bjpHGEbdtrYrkZ
TWITTER_365BOT_API_SECRET=fYoQNSWgrrRP69tYr1gy9JtqS40Ukgw8MGeFpIkUwKLrKwX0hZ
TWITTER_365BOT_ACCESS_TOKEN=2420551951-CfPGziiIrG4XS6KlnduemgKkldS0QJXthQ39Eff
TWITTER_365BOT_ACCESS_TOKEN_SECRET=gArEjOxTjLffrExFbmdOSfINxVwVz7nbKW1tfvfWgDHxC
TWITTER_365BOT_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAJGu6gEAAAAAKipWzEG60uYmmv8Qoe0n07Q9BSM%3DL91SZLeHUaDlrc8vplQdX14etmxAkIx3T8XihNSdG3hkaTjoWI
```

### pursahsgospelアカウント用

```env
TWITTER_PURSAHS_API_KEY=5Wlnhj5HUbCoH0QY6yXNZ2x4r
TWITTER_PURSAHS_API_SECRET=oSD2Xp7kc6Oxf7O0n7nW4R8CMDTOZboYYY7XaMEJ6AD2XLeapH
TWITTER_PURSAHS_ACCESS_TOKEN=2416625168-I1UdgjKXXunJQZhg38hwZqEYygzyjWo0ulWc3iD
TWITTER_PURSAHS_ACCESS_TOKEN_SECRET=ZLJajygqRbZcUL5juPU3VSOxenwnhFyvg2RfBpdb9YbMI
TWITTER_PURSAHS_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAP6u6gEAAAAAYj%2BasP05r85Q8tOuIOidqs%2FYQAM%3DAdI160P6XPfjytgmVgENMZBVaCh7RcT2N29DmBXGeC4xb87qmE
```

### その他の設定

```env
BLOG_365BOT_URL=http://notesofacim.blog.fc2.com/
TWITTER_365BOT_HANDLE=365botGary
BLOG_PURSAHS_URL=https://www.ameba.jp/profile/general/pursahs-gospel/
TWITTER_PURSAHS_HANDLE=pursahsgospel
POST_INTERVAL_HOURS=24
MAX_POST_LENGTH=280
```

## ステップ4: 接続テストの実行

```powershell
cd c:\Users\kazz17\.cursor\blog-to-twitter-bot-temp
python test_twitter_connection.py --account both
```

## 結果の確認

### 成功した場合

```
✓ 接続成功！
  ユーザー名: @365botGary
  表示名: 365botGary
  ユーザーID: 2420551951
```

### 失敗した場合

- **ローカルで成功、GitHub Actionsで失敗**: GitHub ActionsのIPアドレスがブロックされている可能性が高い
- **両方で失敗**: 認証情報やアプリの権限の問題

## テスト後のクリーンアップ

**重要**: テスト後は`.env`ファイルを削除してください。

```powershell
# .envファイルを削除
Remove-Item .env
```

または、`.gitignore`に`.env`が含まれているので、Gitにコミットされることはありません。

## トラブルシューティング

### ModuleNotFoundError

依存パッケージがインストールされていない場合：

```powershell
python -m pip install -r requirements.txt
```

### 認証エラー

`.env`ファイルの認証情報が正しく設定されているか確認してください。

### 接続エラー

インターネット接続を確認してください。




