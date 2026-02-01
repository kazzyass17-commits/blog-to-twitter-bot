"""365botGaryの2026年の投稿履歴を確認"""
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# 2026年の投稿履歴を取得
rows = cur.execute('''
    SELECT ph.posted_at, ph.post_id, ph.tweet_id, ph.cycle_number, p.title
    FROM post_history ph
    JOIN posts p ON ph.post_id = p.id
    WHERE ph.twitter_handle = '365botGary' 
    AND ph.posted_at LIKE '2026%'
    ORDER BY ph.posted_at
''').fetchall()

print("="*70)
print("365botGaryの2026年投稿履歴")
print("="*70)
print(f"\n合計: {len(rows)}件\n")

for r in rows:
    posted_at = r[0][:19]  # 2026-01-21T09:43:21
    post_id = r[1]
    tweet_id = r[2]
    cycle = r[3]
    title = r[4][:50] if r[4] else ''
    print(f"{posted_at} - post_id={post_id:3d}, cycle={cycle}, tweet_id={tweet_id}")
    print(f"  タイトル: {title}")
    print()

conn.close()
