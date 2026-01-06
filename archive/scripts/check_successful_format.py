# -*- coding: utf-8 -*-
"""成功した投稿のフォーマットを確認"""
import sqlite3
from blog_fetcher import BlogFetcher

# 成功した投稿のツイートID
tweet_id = "2007673086020334017"

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT p.link, p.title
    FROM posts p 
    JOIN post_history ph ON p.id = ph.post_id 
    WHERE ph.tweet_id = ?
''', (tweet_id,))
row = cursor.fetchone()
conn.close()

if row:
    url, db_title = row
    print("=" * 60)
    print(f"成功した投稿: {tweet_id}")
    print(f"URL: {url}")
    print(f"DBタイトル: {db_title}")
    print()
    
    # コンテンツを取得
    fetcher = BlogFetcher(url)
    content = fetcher.fetch_latest_post()
    
    if content:
        fetched_title = content.get('title', '')
        fetched_content = content.get('content', '').strip()
        
        print(f"取得したタイトル: {fetched_title}")
        print(f"取得したコンテンツ（最初の100文字）: {fetched_content[:100]}...")
        print()
        
        # タイトルを正規化（365botGaryの場合）
        import re
        normalized_title = fetched_title
        if 'notesofacim.blog.fc2.com' in url:
            normalized_title = re.sub(r'^ACIM学習(ガイド|ノート)\s+', '', normalized_title)
            normalized_title = normalized_title.replace('神の使い', '神の使者')
        
        print(f"正規化後のタイトル: {normalized_title}")
        print(f"タイトル長: {len(normalized_title)}文字")
        print()
        
        # タイトル + 改行 + 本文の形式を試す
        title_with_newline = f"{normalized_title}\n"
        print(f"タイトル + 改行: {len(title_with_newline)}文字")
        print(f"利用可能な本文長: {189 - 23 - 1 - len(title_with_newline)}文字（189 - URL23 - 改行1 - タイトル改行）")
        print()
        
        # 実際の形式を推測
        # 成功した投稿は189文字だったので、タイトル + 改行 + 本文 + 改行 + URL = 189文字
        # 本文 = 189 - 23 - 1 - len(title_with_newline) = 189 - 23 - 1 - (タイトル長 + 1)
        available_content_length = 189 - 23 - 1 - len(title_with_newline)
        print(f"推測される形式:")
        print(f"  タイトル: {normalized_title}")
        print(f"  改行: 1文字")
        print(f"  本文: {available_content_length}文字まで")
        print(f"  改行: 1文字")
        print(f"  URL: 23文字")
        print(f"  合計: {len(normalized_title) + 1 + available_content_length + 1 + 23}文字")




