"""最近の投稿履歴を確認"""
import sqlite3
from datetime import datetime, timedelta

db_path = "posts.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# すべての投稿履歴を取得
cursor.execute('''
    SELECT ph.posted_at, ph.tweet_id, ph.post_id, ph.twitter_handle, p.link, p.title
    FROM post_history ph
    JOIN posts p ON ph.post_id = p.id
    ORDER BY ph.posted_at DESC
    LIMIT 50
''')

rows = cursor.fetchall()

print("=" * 60)
print("最近の投稿履歴（最新50件）")
print("=" * 60)

for i, row in enumerate(rows, 1):
    posted_at = row[0]
    tweet_id = row[1]
    post_id = row[2]
    twitter_handle = row[3]
    link = row[4]
    title = row[5]
    
    # 投稿日時を解析
    try:
        posted_datetime = datetime.fromisoformat(posted_at)
        now = datetime.now()
        time_diff = now - posted_datetime
        
        if time_diff.days == 0:
            time_str = f"{int(time_diff.seconds / 3600)}時間前"
        elif time_diff.days == 1:
            time_str = "昨日"
        else:
            time_str = f"{time_diff.days}日前"
    except:
        time_str = posted_at
    
    print(f"\n{i}. {time_str} - @{twitter_handle}")
    print(f"   投稿日時: {posted_at}")
    print(f"   ツイートID: {tweet_id}")
    print(f"   投稿ID: {post_id}")
    print(f"   URL: {link}")
    print(f"   URL長さ: {len(link)}文字")
    print(f"   タイトル: {title[:50]}...")

conn.close()

