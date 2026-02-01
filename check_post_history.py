"""投稿履歴を確認"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('posts.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 語録111の投稿履歴
print("語録111の投稿履歴:")
rows = cur.execute("""
    SELECT ph.*, p.title 
    FROM post_history ph
    JOIN posts p ON ph.post_id = p.id
    WHERE ph.twitter_handle = 'pursahsgospel'
    AND p.title LIKE '%語録%111%'
    ORDER BY ph.posted_at DESC
""").fetchall()

for row in rows:
    print(f"  {row['posted_at']} - post_id={row['post_id']}, tweet_id={row['tweet_id']}, cycle={row['cycle_number']}, title={row['title']}")

# 本日の投稿履歴
print("\n本日のpursahsgospel投稿履歴:")
today = datetime.now().date().isoformat()
rows = cur.execute("""
    SELECT ph.*, p.title 
    FROM post_history ph
    JOIN posts p ON ph.post_id = p.id
    WHERE ph.twitter_handle = 'pursahsgospel'
    AND ph.posted_at LIKE ?
    ORDER BY ph.posted_at DESC
""", (f"{today}%",)).fetchall()

for row in rows:
    print(f"  {row['posted_at']} - post_id={row['post_id']}, tweet_id={row['tweet_id']}, cycle={row['cycle_number']}, title={row['title']}")

# post_id=9の詳細
print("\npost_id=9の詳細:")
row = cur.execute("SELECT * FROM posts WHERE id = 9").fetchone()
if row:
    print(f"  ID: {row['id']}")
    print(f"  タイトル: {row['title']}")
    print(f"  URL: {row['link']}")

conn.close()
