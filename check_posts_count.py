"""pursahsgospelの投稿数を確認"""
import sqlite3

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# 総投稿数
rows = cur.execute("SELECT COUNT(*) FROM posts WHERE blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%'").fetchone()
print(f'pursahsgospelの総投稿数: {rows[0]}')

# 語録投稿数（原書除外）
goroku_rows = cur.execute("SELECT COUNT(*) FROM posts WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%') AND title LIKE '%語録%' AND title NOT LIKE '%原書%'").fetchone()
print(f'語録投稿数（原書除外）: {goroku_rows[0]}')

# サイクル2で未投稿の投稿数
cycle2_unposted = cur.execute("""
    SELECT COUNT(*) FROM posts p
    WHERE (p.blog_url LIKE '%pursahs%' OR p.blog_url LIKE '%ameblo%')
    AND p.title LIKE '%語録%' AND p.title NOT LIKE '%原書%'
    AND NOT EXISTS (
        SELECT 1 FROM post_history ph
        WHERE ph.post_id = p.id
        AND ph.twitter_handle = 'pursahsgospel'
        AND ph.cycle_number = 2
    )
""").fetchone()
print(f'サイクル2で未投稿の語録数: {cycle2_unposted[0]}')

# 語録111の情報
post_111 = cur.execute("SELECT id, title FROM posts WHERE title LIKE '%語録%111%' AND title NOT LIKE '%原書%'").fetchall()
print(f'\n語録111の投稿数: {len(post_111)}')
for p in post_111:
    print(f'  ID:{p[0]}, {p[1]}')

conn.close()
