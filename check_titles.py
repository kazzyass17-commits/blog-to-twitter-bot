"""登録されているタイトルを確認"""
import sqlite3

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# 最新の10件のタイトルを確認
rows = cur.execute("""
    SELECT id, title 
    FROM posts 
    WHERE blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%'
    ORDER BY id DESC
    LIMIT 20
""").fetchall()

print("最新の20件のタイトル:")
for row in rows:
    print(f"  ID:{row[0]}, {row[1][:80]}")

# 「語録」を含むタイトルを確認
goroku_rows = cur.execute("""
    SELECT id, title 
    FROM posts 
    WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%')
    AND title LIKE '%語録%'
    ORDER BY id DESC
    LIMIT 10
""").fetchall()

print(f"\n「語録」を含むタイトル（最新10件）:")
for row in goroku_rows:
    print(f"  ID:{row[0]}, {row[1][:80]}")

conn.close()
