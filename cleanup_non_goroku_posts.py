"""語録以外の投稿をデータベースから削除"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()

# 語録以外の投稿を取得
cursor.execute("""
    SELECT id, title 
    FROM posts 
    WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%')
    AND (title NOT LIKE '%語録%' OR title LIKE '%原書%' OR title LIKE '%索引%')
    ORDER BY id
""")
rows = cursor.fetchall()

logger.info(f"削除対象: {len(rows)}件")
for row in rows:
    logger.info(f"  ID:{row[0]}, {row[1][:80]}")

# 削除を実行
if rows:
    cursor.execute("""
        DELETE FROM posts 
        WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%')
        AND (title NOT LIKE '%語録%' OR title LIKE '%原書%' OR title LIKE '%索引%')
    """)
    deleted_count = cursor.rowcount
    conn.commit()
    logger.info(f"削除完了: {deleted_count}件")
else:
    logger.info("削除対象なし")

# 語録投稿数を確認
goroku_rows = cursor.execute("""
    SELECT COUNT(*) FROM posts 
    WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%') 
    AND title LIKE '%語録%' 
    AND title NOT LIKE '%原書%'
    AND title NOT LIKE '%索引%'
""").fetchone()
logger.info(f"残りの語録投稿数: {goroku_rows[0]} 件")

conn.close()
