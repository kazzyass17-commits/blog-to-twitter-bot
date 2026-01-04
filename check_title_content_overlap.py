"""タイトルと本文の重複を確認"""
from database import PostDatabase
from twitter_poster import TwitterPoster
from blog_fetcher import BlogFetcher
from config import Config
import sqlite3

db = PostDatabase()
conn = sqlite3.connect("posts.db")
cursor = conn.cursor()

# 投稿ID 437を取得
cursor.execute('SELECT * FROM posts WHERE id = 437')
post_row = cursor.fetchone()
conn.close()

if post_row:
    url = post_row[4]  # link
    title = post_row[2]  # title
    
    print("=" * 60)
    print("投稿ID 437の内容を確認")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"タイトル（DB）: {title}")
    
    # ページからコンテンツを取得
    fetcher = BlogFetcher(url)
    page_content = fetcher.fetch_latest_post()
    
    if page_content:
        fetched_title = page_content.get('title', '')
        content = page_content.get('content', '')
        
        print(f"\n取得したタイトル: {fetched_title}")
        print(f"本文の最初50文字: {content[:50]}")
        
        # タイトルを正規化
        import re
        normalized_title = fetched_title
        if 'ameblo.jp/pursahs-gospel' in url or 'ameba.jp/profile/general/pursahs-gospel' in url:
            normalized_title = re.sub(r'\s*\|\s*Pursah\'?s Gospelのブログ\s*$', '', normalized_title)
            normalized_title = re.sub(r'\s*\|\s*パーサによるトマスの福音書\s*$', '', normalized_title)
        
        print(f"\n正規化後のタイトル: {normalized_title}")
        print(f"本文の最初: {content[:len(normalized_title)]}")
        
        # タイトルと本文の最初が同じか確認
        if content.startswith(normalized_title):
            print(f"\n⚠️ タイトルと本文の最初が同じです！")
            print(f"   タイトル: {normalized_title}")
            print(f"   本文の最初: {content[:len(normalized_title)]}")
        else:
            print(f"\n✓ タイトルと本文の最初は異なります")
        
        # フォーマット後のテキストを確認
        poster = TwitterPoster(Config.get_twitter_credentials_pursahs())
        tweet_text = poster.format_blog_post(fetched_title, content, url)
        
        print(f"\nフォーマット後の投稿テキスト（最初の200文字）:")
        print(f"{tweet_text[:200]}")
        
        # タイトルが含まれているか確認
        if normalized_title in tweet_text:
            print(f"\nタイトルが投稿テキストに含まれています")
            # タイトルの位置を確認
            title_pos = tweet_text.find(normalized_title)
            print(f"タイトルの位置: {title_pos}")
            if title_pos == 0:
                print(f"本文の開始位置: {len(normalized_title) + 1} (改行後)")
                print(f"本文の最初: {tweet_text[len(normalized_title) + 1:len(normalized_title) + 1 + len(normalized_title)]}")
                if tweet_text[len(normalized_title) + 1:len(normalized_title) + 1 + len(normalized_title)] == normalized_title:
                    print(f"\n⚠️ タイトルと本文の最初が重複しています！")
    else:
        print("コンテンツを取得できませんでした")
else:
    print("投稿ID 437が見つかりませんでした")




