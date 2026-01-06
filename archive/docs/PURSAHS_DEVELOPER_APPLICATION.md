# pursahsgospel用 Twitter Developer Portal 申請理由

## 申請フォームの記入内容

### "Describe all of your use cases of X's data and API:"（使用目的の説明）

以下のテキストを入力してください（英語）：

```
I want to create a bot that automatically posts blog content to Twitter for the Pursah's Gospel account. The bot will:

1. Fetch blog posts from a completed blog (Pursah's Gospel - spiritual/religious content)
2. Post quotes from this blog to Twitter at scheduled times (3 times per day: 8 AM, 2 PM, 8 PM JST)
3. Ensure all posts are shared once before reposting (cycle management)
4. Format posts to fit within Twitter's 280-character limit

This is for personal use to share spiritual content (Pursah's Gospel quotes) with followers. The bot will not:
- Resell any data received via X APIs
- Violate any terms of service
- Post spam or inappropriate content

The bot will be hosted on GitHub Actions and will post to the @pursahsgospel Twitter account.

This is part of a project that also includes another bot for @365botGary account, but they are managed separately with different authentication credentials.
```

日本語版（必要に応じて）：

```
Pursah's Gospelアカウント用に、ブログの内容を自動的にTwitterに投稿するボットを作成したいです。このボットは：

1. 完了したブログ（Pursah's Gospel - スピリチュアル/宗教的なコンテンツ）から投稿を取得
2. スケジュールされた時間（1日3回：8時、14時、20時 JST）にこのブログからの引用をTwitterに投稿
3. すべての投稿が再投稿される前に1回ずつ共有されることを保証（サイクル管理）
4. Twitterの280文字制限内に収まるように投稿をフォーマット

これは、フォロワーとスピリチュアルなコンテンツ（Pursah's Gospelの引用）を共有するための個人的な使用です。このボットは：
- X APIから受け取ったデータを再販売しません
- 利用規約に違反しません
- スパムや不適切なコンテンツを投稿しません

ボットはGitHub Actionsでホストされ、@pursahsgospel Twitterアカウントに投稿します。

このプロジェクトには@365botGaryアカウント用の別のボットも含まれていますが、それぞれ異なる認証情報で個別に管理されています。
```

## チェックボックス

以下の3つすべてにチェックを入れてください：

- [x] "You understand that you may not resell anything you receive via the X APIs"
- [x] "You understand your Developer account may be terminated if you violate the Developer Agreement or any of the Incorporated Developer Terms"
- [x] "You accept the Terms & Conditions"

## 注意事項

- 使用目的は具体的に記述してください
- 商用利用でない場合は明記してください
- 利用規約に同意する必要があります
- 申請後、通常は数分で承認されます

## 申請後の次のステップ

承認後：
1. プロジェクトとアプリを作成
2. 認証情報を取得（API Key, API Secret, Access Token, Access Token Secret, Bearer Token）
3. GitHub Secretsに設定（`TWITTER_PURSAHS_API_KEY` 等）




