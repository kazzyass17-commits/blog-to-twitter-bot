"""365botGaryのサイクル#1の投稿状況を詳細確認"""
import sqlite3
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# サイクル#1で投稿された投稿IDを取得
cur.execute('''
    SELECT DISTINCT post_id FROM post_history 
    WHERE twitter_handle = '365botGary' AND cycle_number = 1
''')
posted_ids = [row[0] for row in cur.fetchall()]

print("="*70)
print("365botGary サイクル#1の詳細確認")
print("="*70)

print(f"\nサイクル#1で投稿された投稿ID: {posted_ids}")
print(f"投稿済み数: {len(posted_ids)}件")

# 全投稿数を取得
blog_url_365 = "http://notesofacim.blog.fc2.com/"
cur.execute('SELECT COUNT(*) FROM posts WHERE blog_url = ?', (blog_url_365,))
total_posts = cur.fetchone()[0]
print(f"全投稿数: {total_posts}件")

# Day001～Day365の投稿数を取得
cur.execute('SELECT id, title FROM posts WHERE blog_url = ?', (blog_url_365,))
all_posts = cur.fetchall()
day_pattern = re.compile(r'Day(\d{3})')
day_posts = []
for post_id, title in all_posts:
    if title:
        match = day_pattern.search(title)
        if match:
            day_num = int(match.group(1))
            if 1 <= day_num <= 365:
                day_posts.append(post_id)

print(f"Day001～Day365の投稿数: {len(day_posts)}件")

# サイクル#1で未投稿のDay001～Day365の投稿を取得
unposted_day_ids = [pid for pid in day_posts if pid not in posted_ids]
print(f"サイクル#1で未投稿のDay001～Day365の投稿数: {len(unposted_day_ids)}件")

# 投稿済みのDay001～Day365の投稿を確認
posted_day_ids = [pid for pid in posted_ids if pid in day_posts]
print(f"サイクル#1で投稿済みのDay001～Day365の投稿数: {len(posted_day_ids)}件")
if posted_day_ids:
    print(f"投稿済みのDay001～Day365の投稿ID: {posted_day_ids}")

conn.close()
