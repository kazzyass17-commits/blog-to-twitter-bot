"""語録111を確認"""
import sqlite3

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# 語録111を含むタイトルを検索
rows = cur.execute("""
    SELECT id, title 
    FROM posts 
    WHERE (title LIKE '%111%' OR title LIKE '%１１１%')
    AND (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%')
""").fetchall()

print('語録111を含むタイトル:')
for row in rows:
    print(f'  ID:{row[0]}, {row[1]}')

conn.close()
