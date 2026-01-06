"""pursahsgospelの投稿を確認"""
import sqlite3
from database import PostDatabase

db = PostDatabase()

conn = sqlite3.connect(db.db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM posts WHERE blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%' ORDER BY id")
rows = cursor.fetchall()
posts = [dict(row) for row in rows]
conn.close()

print(f"pursahsgospel 総投稿数: {len(posts)}")

goroku_posts = []
non_goroku_posts = []

for post in posts:
    title = post.get('title', '')
    if '語録' in title:
        goroku_posts.append(post)
    else:
        non_goroku_posts.append(post)

print(f"語録投稿数: {len(goroku_posts)}")
print(f"語録以外の投稿数: {len(non_goroku_posts)}")

if non_goroku_posts:
    print()
    print("語録以外の投稿:")
    for i, post in enumerate(non_goroku_posts, 1):
        title = post.get('title', 'No title')[:60]
        link = post.get('link', '')[:80]
        print(f"{i}. ID: {post['id']}, タイトル: {title}")
        print(f"   URL: {link}")
else:
    print()
    print("語録以外の投稿はありません。")

