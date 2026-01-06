# 引継ぎテキスト

## 現在のタスク

**ブログからランダムに1つ投稿を選び、両方のアカウント（365botGaryとpursahsgospel）で投稿を実施する**

## 作成したスクリプト

### `post_both_accounts.py`
- 両方のアカウントで投稿を実施するスクリプト
- 365botGary用とpursahsgospel用のそれぞれのブログからランダムに1つずつ投稿を選ぶ
- 各アカウントの待機時間をチェックしてから投稿
- レート制限エラー（429）が発生した場合は原因を記録

## 実行状況

- スクリプトは作成済み
- 実行は未実施（コマンドがタイムアウトまたはエラー）
- ログファイル（`post_both_accounts.log`）は空

## 次のステップ

1. **スクリプトの実行**
   ```powershell
   cd C:\Users\kazz17\.cursor\blog-to-twitter-bot-temp
   python post_both_accounts.py
   ```

2. **実行結果の確認**
   - ログファイル（`post_both_accounts.log`）を確認
   - コンソール出力を確認
   - 投稿が成功したかどうかを確認

3. **エラーが発生した場合**
   - エラーメッセージを確認
   - 待機時間が発生していないか確認（`check_wait_time.py`）
   - レート制限状態を確認（`check_rate_limit_from_api.py`）

## 重要な設定

### アカウント設定
- **365botGary**: 
  - ブログURL: `http://notesofacim.blog.fc2.com/`
  - Twitterハンドル: `365botGary`
  - タイトルなしで投稿（本文のみ）

- **pursahsgospel**: 
  - ブログURL: `https://www.ameba.jp/profile/general/pursahs-gospel/`
  - Twitterハンドル: `pursahsgospel`
  - タイトルありで投稿

### 文字数制限
- 最大280文字（URLは23文字としてカウント）
- `format_blog_post`メソッドで自動調整

### レート制限管理
- `rate_limit_checker.py`で待機時間を管理
- `rate_limit_state.json`に待機状態を保存
- 429エラー発生時は原因を記録して次のアカウントに移る

## 関連ファイル

- `post_both_accounts.py`: 両アカウント投稿スクリプト（新規作成）
- `main_365bot.py`: 365botGary専用スクリプト
- `main_pursahs.py`: pursahsgospel専用スクリプト
- `twitter_poster.py`: Twitter投稿モジュール
- `rate_limit_checker.py`: レート制限管理モジュール
- `database.py`: データベース管理モジュール
- `blog_fetcher.py`: ブログコンテンツ取得モジュール

## 確認用コマンド

```powershell
# 待機時間の確認
python check_wait_time.py

# レート制限状態の確認（X APIから直接取得）
python check_rate_limit_from_api.py

# レート制限の理由を確認
python check_rate_limit_reasons.py
```

## 注意事項

- 両方のアカウントが待機時間中の場合は、投稿をスキップする
- 429エラーが発生した場合は、原因を記録して次のアカウントに移る
- 投稿成功時は、データベースに投稿履歴を記録する




