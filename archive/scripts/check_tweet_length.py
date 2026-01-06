# -*- coding: utf-8 -*-
"""成功した投稿と失敗した投稿の文字数を比較"""
import sqlite3
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config

# 成功した投稿のツイートID
successful_tweet_id = "2007697732786667551"

# データベースから成功した投稿の情報を取得
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT p.link, p.title, ph.posted_at
    FROM posts p 
    JOIN post_history ph ON p.id = ph.post_id 
    WHERE ph.tweet_id = ?
''', (successful_tweet_id,))
row = cursor.fetchone()
conn.close()

if row:
    url, title, posted_at = row
    print("=" * 60)
    print("成功した投稿の文字数確認")
    print("=" * 60)
    print(f"ツイートID: {successful_tweet_id}")
    print(f"投稿日時: {posted_at}")
    print(f"URL: {url}")
    print(f"タイトル: {title}")
    print()
    
    # コンテンツを取得
    fetcher = BlogFetcher(url)
    content = fetcher.fetch_latest_post()
    
    if content:
        # ツイートテキストをフォーマット
        poster = TwitterPoster(Config.get_twitter_credentials_365bot())
        tweet_text = poster.format_blog_post(
            title=content.get('title', ''),
            content=content.get('content', ''),
            link=url
        )
        
        print(f"フォーマット後の本文: {len(tweet_text)}文字")
        print(f"URLを含む合計: {len(tweet_text) + 1 + 23}文字（改行1 + URL23）")
        print(f"実際のURL長: {len(url)}文字")
        print()
        print("投稿テキスト（最初の100文字）:")
        print(tweet_text[:100] + "...")
        print()
        print("=" * 60)
    else:
        print("コンテンツを取得できませんでした")
else:
    print(f"ツイートID {successful_tweet_id} が見つかりませんでした")

# 失敗した投稿（最新のドライラン結果）と比較
print()
print("=" * 60)
print("失敗した投稿の文字数（最新のドライラン結果）")
print("=" * 60)
print("本文: 142文字")
print("URLを含む: 166文字（改行1 + URL23）")
print()
print("=" * 60)
print("比較結果")
print("=" * 60)
if row and content:
    poster = TwitterPoster(Config.get_twitter_credentials_365bot())
    tweet_text = poster.format_blog_post(
        title=content.get('title', ''),
        content=content.get('content', ''),
        link=url
    )
    success_length = len(tweet_text) + 1 + 23
    fail_length = 166
    print(f"成功した投稿: {success_length}文字")
    print(f"失敗した投稿: {fail_length}文字")
    print(f"差: {fail_length - success_length}文字")
    if fail_length > success_length:
        print(f"⚠️ 失敗した投稿の方が {fail_length - success_length}文字長いです")

