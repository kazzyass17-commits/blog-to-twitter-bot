"""投稿対象件数を確認"""
import sqlite3
import re
from database import PostDatabase

db = PostDatabase()

conn = sqlite3.connect(db.db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 365botGary
cursor.execute("SELECT * FROM posts WHERE blog_url LIKE '%notesofacim%'")
rows = cursor.fetchall()
all_365bot = [dict(row) for row in rows]

day_pattern = re.compile(r'Day(\d{3})')
day_posts = []
for post in all_365bot:
    title = post.get('title', '')
    match = day_pattern.search(title)
    if match:
        day_num = int(match.group(1))
        if 1 <= day_num <= 365:
            day_posts.append(post)

print("365botGary:")
print(f"  DB総数: {len(all_365bot)}件")
print(f"  投稿対象（Day001-Day365）: {len(day_posts)}件")
print()

# pursahsgospel
cursor.execute("SELECT * FROM posts WHERE blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%'")
rows = cursor.fetchall()
all_pursahs = [dict(row) for row in rows]

goroku_posts = [p for p in all_pursahs if '語録' in p.get('title', '')]

print("pursahsgospel:")
print(f"  DB総数: {len(all_pursahs)}件")
print(f"  投稿対象（語録）: {len(goroku_posts)}件")

conn.close()

