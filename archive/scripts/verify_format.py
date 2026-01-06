# -*- coding: utf-8 -*-
"""フォーマットの検証"""
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config

# 成功した投稿のURL
url = "http://notesofacim.blog.fc2.com/blog-entry-193.html"

fetcher = BlogFetcher(url)
content = fetcher.fetch_latest_post()

if content:
    poster = TwitterPoster(Config.get_twitter_credentials_365bot())
    tweet_text = poster.format_blog_post(
        title=content.get('title', ''),
        content=content.get('content', ''),
        link=url
    )
    
    print("=" * 60)
    print("フォーマット結果の検証")
    print("=" * 60)
    print(f"タイトル: {content.get('title', '')}")
    print(f"フォーマット後のテキスト: {tweet_text[:100]}...")
    print(f"文字数: {len(tweet_text)}文字")
    print(f"URL含む: {len(tweet_text) + 1 + 23}文字（改行1 + URL23）")
    print()
    print("成功した投稿は189文字でした")
    print(f"現在の結果: {len(tweet_text) + 1 + 23}文字")
    print("=" * 60)




