"""format_blog_postの動作確認"""
from twitter_poster import TwitterPoster
from config import Config

# 365botGaryの認証情報を取得
credentials = Config.get_twitter_credentials_365bot()
poster = TwitterPoster(credentials)

# テストデータ
title = "Day026（神の使者:P.145、ACIM:T-15.X.04.02）"
content = "「コース」による奇跡とは認識の変化への転換であり、単なる表面的な思考の変化や行動の変化ではない。（神の使者:P.145）This brings up one of the interesting features of the miracle"
link = "http://notesofacim.blog.fc2.com/blog-entry-69.html"

# フォーマット
tweet_text = poster.format_blog_post(title, content, link)

print("=" * 60)
print("format_blog_post の結果")
print("=" * 60)
print(f"タイトル: {title}")
print(f"本文（最初の100文字）: {content[:100]}...")
print(f"\nフォーマット後のテキスト:")
print(tweet_text)
print(f"\n文字数: {len(tweet_text)} 文字")
print(f"URLを含む場合: {len(tweet_text)} + 改行(1) + URL(23) = {len(tweet_text) + 24} 文字")
print(f"280文字以内: {len(tweet_text) + 24 <= 280}")

# post_tweet_with_linkで使用される形式を確認
print("\n" + "=" * 60)
print("post_tweet_with_link で使用される形式")
print("=" * 60)
final_text = f"{tweet_text}\n{link}"
print(f"最終テキスト（最初の150文字）:")
print(final_text[:150])
print(f"\n最終文字数: {len(final_text)} 文字")
print(f"280文字以内: {len(final_text) <= 280}")











