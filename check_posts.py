"""データベース内の投稿を確認"""
import sqlite3
from database import PostDatabase

db = PostDatabase()

# データベースに直接接続して全投稿を確認
conn = sqlite3.connect(db.db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 365botのブログURLで投稿を取得
cursor.execute("SELECT * FROM posts WHERE blog_url LIKE '%notesofacim%' ORDER BY id")
rows = cursor.fetchall()
posts = [dict(row) for row in rows]
conn.close()

print(f"総投稿数: {len(posts)}")

# Day投稿とDay以外の投稿を分類
day_posts = []
non_day_posts = []

for post in posts:
    title = post.get('title', '')
    if 'Day' in title:
        day_posts.append(post)
    else:
        non_day_posts.append(post)

print(f"Day投稿数: {len(day_posts)}")
print(f"Day以外の投稿数: {len(non_day_posts)}")

if non_day_posts:
    print("\nDay以外の投稿（最初の10件）:")
    for i, post in enumerate(non_day_posts[:10], 1):
        print(f"{i}. ID: {post['id']}, タイトル: {post.get('title', 'No title')[:60]}")
        print(f"   URL: {post.get('link', '')[:80]}")

# ID: 102の投稿を確認
print("\nID: 102の投稿:")
cursor = conn.cursor()
cursor.execute("SELECT * FROM posts WHERE id = 102")
row = cursor.fetchone()
if row:
    post = dict(row)
    print(f"タイトル: {post.get('title', 'No title')}")
    print(f"URL: {post.get('link', '')}")

