# テスト投稿ガイド

テスト投稿を行うための手順を説明します。

## 前提条件

1. Python 3.8以上がインストールされていること
2. 依存パッケージがインストールされていること
3. `.env`ファイルが設定されていること
4. Twitter API認証情報が設定されていること

## セットアップ手順

### 1. 依存パッケージのインストール

```powershell
cd blog-to-twitter-bot
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルがまだ作成されていない場合：

```powershell
copy env.example.txt .env
```

`.env`ファイルを編集して、Twitter API認証情報を設定してください。

### 3. 投稿データベースの初期化（初回のみ）

```powershell
python init_posts.py
```

このスクリプトはブログから全投稿を取得してデータベース（`posts.db`）に保存します。
初回セットアップ時に1回だけ実行してください。

## テスト投稿の実行

### 方法1: ドライラン（実際に投稿しない）

実際にTwitterに投稿せずに、投稿予定の内容を確認できます：

```powershell
# 両方のアカウントでドライラン
python test_post.py --dry-run

# 365botGaryのみ
python test_post.py --dry-run --account 365bot

# pursahsgospelのみ
python test_post.py --dry-run --account pursahs
```

### 方法2: 実際にテスト投稿

実際にTwitterに投稿します：

```powershell
# 両方のアカウントでテスト投稿
python test_post.py

# 365botGaryのみ
python test_post.py --account 365bot

# pursahsgospelのみ
python test_post.py --account pursahs
```

実行すると、確認プロンプトが表示されます。`y`を入力すると投稿が実行されます。

## テスト投稿の流れ

1. **データベースから未投稿の投稿をランダムに選択**
2. **ツイートテキストを生成**
3. **Twitterに投稿**
4. **投稿履歴をデータベースに記録**

## 確認事項

テスト投稿前に以下を確認してください：

- [ ] `.env`ファイルにTwitter API認証情報が正しく設定されている
- [ ] `posts.db`ファイルが存在し、投稿データが含まれている
- [ ] 投稿先のTwitterアカウントが正しい
- [ ] Twitter APIのレート制限に達していない

## トラブルシューティング

### エラー: "データベースに投稿がありません"

`python init_posts.py`を実行して投稿データベースを初期化してください。

### エラー: "認証情報が設定されていません"

`.env`ファイルを確認して、Twitter API認証情報が正しく設定されているか確認してください。

### エラー: "tweepy.errors.Unauthorized: 401 Unauthorized"

Twitter API認証情報が間違っている可能性があります。`.env`ファイルの認証情報を確認してください。

### エラー: "ModuleNotFoundError"

依存パッケージがインストールされていません。`pip install -r requirements.txt`を実行してください。

## 注意事項

- テスト投稿は実際にTwitterに投稿されます
- 投稿した内容は公開されます
- レート制限に注意してください
- テスト投稿も通常の投稿としてカウントされ、サイクル管理の対象になります


