"""除外された投稿を確認"""
import sqlite3

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
cursor.execute("SELECT id, title FROM posts WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%') AND title NOT LIKE '%語録%'")
rows = cursor.fetchall()
print("「語録」を含まないタイトル:")
for r in rows:
    print(f"  ID:{r[0]} | {r[1]}")
conn.close()



