"""get_unposted_posts_in_cycleの動作を検証"""
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

blog_url = "http://notesofacim.blog.fc2.com/"
twitter_handle = "365botGary"
cycle_number = 1

# サイクル#1で投稿された投稿IDを取得
cur.execute('''
    SELECT DISTINCT post_id FROM post_history 
    WHERE blog_url = ? AND twitter_handle = ? AND cycle_number = ?
''', (blog_url, twitter_handle, cycle_number))
posted_ids = [row[0] for row in cur.fetchall()]

print("="*70)
print("get_unposted_posts_in_cycleの動作検証")
print("="*70)
print(f"\nサイクル#{cycle_number}で投稿された投稿ID: {posted_ids}")
print(f"投稿済み数: {len(posted_ids)}件")

# 全投稿数を取得
cur.execute('SELECT COUNT(*) FROM posts WHERE blog_url = ?', (blog_url,))
total_posts = cur.fetchone()[0]
print(f"全投稿数: {total_posts}件")

# get_unposted_posts_in_cycleと同じロジックで未投稿を取得
if posted_ids:
    placeholders = ','.join('?' * len(posted_ids))
    cur.execute(f'''
        SELECT COUNT(*) FROM posts 
        WHERE blog_url = ? AND id NOT IN ({placeholders})
    ''', [blog_url] + posted_ids)
else:
    cur.execute('SELECT COUNT(*) FROM posts WHERE blog_url = ?', (blog_url,))

unposted_count = cur.fetchone()[0]
print(f"未投稿数（計算値）: {unposted_count}件")
print(f"投稿済み + 未投稿 = {len(posted_ids)} + {unposted_count} = {len(posted_ids) + unposted_count}件")
print(f"全投稿数との差: {total_posts - (len(posted_ids) + unposted_count)}件")

conn.close()
