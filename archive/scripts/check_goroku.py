"""語録を含むタイトルを確認"""
import sqlite3

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
cursor.execute("SELECT title FROM posts WHERE blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%'")
rows = cursor.fetchall()

goroku = [r[0] for r in rows if r[0] and '語録' in r[0]]
print(f"語録を含むタイトル: {len(goroku)}件")
print()
for t in sorted(goroku):
    print(t)

conn.close()

