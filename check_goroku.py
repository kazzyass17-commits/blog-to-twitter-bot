"""語録で始まるタイトルを確認"""
import sqlite3

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
cursor.execute("SELECT id, title, link FROM posts WHERE blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%' ORDER BY id")
rows = cursor.fetchall()

print("DBに登録されているタイトル:")
for r in rows:
    print(f"ID:{r[0]:3d} | {r[1][:50] if r[1] else 'None'}")

conn.close()

