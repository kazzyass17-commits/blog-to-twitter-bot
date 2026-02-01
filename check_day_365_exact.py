"""Day001～Day365の正確な投稿数を確認（重複除外）"""
import sqlite3
import sys
import io
import re

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
posted_ids = set([row[0] for row in cur.fetchall()])

# 全投稿を取得
cur.execute('SELECT id, title FROM posts WHERE blog_url = ?', (blog_url,))
all_posts = cur.fetchall()

day_pattern = re.compile(r'Day(\d{3})')
day_posts_dict = {}  # day_num -> (post_id, title)

for post_id, title in all_posts:
    if title:
        match = day_pattern.search(title)
        if match:
            day_num = int(match.group(1))
            if 1 <= day_num <= 365:
                # 重複がある場合、最初に見つかったものを使う（または投稿済みのものを優先）
                if day_num not in day_posts_dict:
                    day_posts_dict[day_num] = (post_id, title)
                elif post_id in posted_ids:
                    # 投稿済みのものを優先
                    day_posts_dict[day_num] = (post_id, title)

print("="*70)
print("Day001～Day365の正確な投稿数確認（重複除外）")
print("="*70)

print(f"\nDay001～Day365のユニークな投稿数: {len(day_posts_dict)}件")

# 投稿済みと未投稿を分ける
posted_day_posts = {day: (pid, title) for day, (pid, title) in day_posts_dict.items() if pid in posted_ids}
unposted_day_posts = {day: (pid, title) for day, (pid, title) in day_posts_dict.items() if pid not in posted_ids}

print(f"サイクル#1で投稿済み: {len(posted_day_posts)}件")
print(f"サイクル#1で未投稿: {len(unposted_day_posts)}件")
print(f"合計: {len(posted_day_posts) + len(unposted_day_posts)}件")

if len(day_posts_dict) != 365:
    missing_days = [d for d in range(1, 366) if d not in day_posts_dict]
    print(f"\n欠けているDay番号: {len(missing_days)}件")
    if missing_days:
        print(f"  例: {missing_days[:10]}")

conn.close()
