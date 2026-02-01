"""語録111の投稿履歴を削除"""
import sqlite3

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()

# 語録111の投稿履歴を確認
cursor.execute("""
    SELECT ph.*, p.title 
    FROM post_history ph
    JOIN posts p ON ph.post_id = p.id
    WHERE ph.twitter_handle = 'pursahsgospel'
    AND p.title LIKE '%語録%111%'
    ORDER BY ph.posted_at DESC
""")
rows = cursor.fetchall()

print(f"削除対象: {len(rows)}件")
for row in rows:
    print(f"  ID:{row[0]}, post_id={row[1]}, tweet_id={row[4]}, posted_at={row[5]}, cycle={row[6]}")

# 削除を実行
if rows:
    cursor.execute("""
        DELETE FROM post_history 
        WHERE id IN (
            SELECT ph.id 
            FROM post_history ph
            JOIN posts p ON ph.post_id = p.id
            WHERE ph.twitter_handle = 'pursahsgospel'
            AND p.title LIKE '%語録%111%'
        )
    """)
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"\n削除完了: {deleted_count}件")
else:
    print("\n削除対象なし")

conn.close()
