"""365botGaryの全サイクルの投稿状況を確認"""
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# 全サイクルの投稿数を確認
cur.execute('''
    SELECT cycle_number, COUNT(DISTINCT post_id) as count
    FROM post_history 
    WHERE twitter_handle = '365botGary'
    GROUP BY cycle_number
    ORDER BY cycle_number
''')
cycle_counts = cur.fetchall()

print("="*70)
print("365botGaryの全サイクルの投稿状況")
print("="*70)

total_posted = 0
for cycle_num, count in cycle_counts:
    print(f"サイクル#{cycle_num}: {count}件")
    total_posted += count

print(f"\n合計投稿済み: {total_posted}件")

# 全投稿履歴の投稿IDを確認
cur.execute('''
    SELECT DISTINCT post_id FROM post_history 
    WHERE twitter_handle = '365botGary'
    ORDER BY post_id
''')
all_posted_ids = [row[0] for row in cur.fetchall()]
print(f"投稿済み投稿ID数: {len(all_posted_ids)}件")
print(f"投稿済み投稿ID（最初の20件）: {all_posted_ids[:20]}")

conn.close()
