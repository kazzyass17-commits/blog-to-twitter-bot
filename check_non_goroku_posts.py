"""語録以外の投稿を確認"""
import sqlite3

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# 語録以外の投稿を取得
rows = cur.execute("""
    SELECT id, title 
    FROM posts 
    WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%')
    AND (title NOT LIKE '%語録%' OR title LIKE '%原書%' OR title LIKE '%索引%')
    ORDER BY id
""").fetchall()

print(f'語録以外の投稿数: {len(rows)}件')
print('\n語録以外の投稿:')
for row in rows:
    print(f'  ID:{row[0]}, {row[1][:80]}')

# 語録投稿数を確認
goroku_rows = cur.execute("""
    SELECT COUNT(*) FROM posts 
    WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%') 
    AND title LIKE '%語録%' 
    AND title NOT LIKE '%原書%'
    AND title NOT LIKE '%索引%'
""").fetchone()
print(f'\n語録投稿数（原書・索引除外）: {goroku_rows[0]} 件')

conn.close()
