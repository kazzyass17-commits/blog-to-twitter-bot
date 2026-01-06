# -*- coding: utf-8 -*-
"""成功した投稿の文字数を確認"""
import sqlite3
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config

# 成功した投稿のツイートID
successful_tweet_ids = ["2007673086020334017", "2007669957476397294"]

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()

for tweet_id in successful_tweet_ids:
    cursor.execute('''
        SELECT p.link, p.title, ph.posted_at
        FROM posts p 
        JOIN post_history ph ON p.id = ph.post_id 
        WHERE ph.tweet_id = ?
    ''', (tweet_id,))
    row = cursor.fetchone()
    
    if row:
        url, title, posted_at = row
        print("=" * 60)
        print(f"成功した投稿: {tweet_id}")
        print(f"投稿日時: {posted_at}")
        print(f"URL: {url}")
        print()
        
        # コンテンツを取得
        fetcher = BlogFetcher(url)
        content = fetcher.fetch_latest_post()
        
        if content:
            # 現在の設定でフォーマット
            poster = TwitterPoster(Config.get_twitter_credentials_365bot())
            tweet_text = poster.format_blog_post(
                title=content.get('title', ''),
                content=content.get('content', ''),
                link=url
            )
            
            print(f"現在の設定での文字数:")
            print(f"  本文: {len(tweet_text)}文字")
            print(f"  URL含む: {len(tweet_text) + 1 + 23}文字")
            print()
            
            # 以前の設定（256文字まで）でフォーマット
            # 以前は max_text_length = 280 - 23 - 1 = 256文字
            max_text_length_old = 280 - 23 - 1  # 256文字
            cleaned_content = content.get('content', '').strip()
            if len(cleaned_content) <= max_text_length_old:
                tweet_text_old = cleaned_content
            else:
                tweet_text_old = cleaned_content[:max_text_length_old]
            
            print(f"以前の設定（256文字まで）での文字数:")
            print(f"  本文: {len(tweet_text_old)}文字")
            print(f"  URL含む: {len(tweet_text_old) + 1 + 23}文字")
            print()

conn.close()




