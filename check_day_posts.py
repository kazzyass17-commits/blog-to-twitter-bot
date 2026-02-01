"""Day001～Day365の投稿数を正確に確認"""
import sqlite3
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

blog_url = "http://notesofacim.blog.fc2.com/"
cur.execute('SELECT id, title FROM posts WHERE blog_url = ?', (blog_url,))
all_posts = cur.fetchall()

day_pattern = re.compile(r'Day(\d{3})')
day_posts = []
day_numbers = []

for post_id, title in all_posts:
    if title:
        match = day_pattern.search(title)
        if match:
            day_num = int(match.group(1))
            if 1 <= day_num <= 365:
                day_posts.append((post_id, title, day_num))
                day_numbers.append(day_num)

print("="*70)
print("Day001～Day365の投稿数確認")
print("="*70)

print(f"\nDay001～Day365の投稿数: {len(day_posts)}件")

# 重複チェック
if len(day_numbers) != len(set(day_numbers)):
    duplicates = [d for d in day_numbers if day_numbers.count(d) > 1]
    print(f"重複するDay番号: {set(duplicates)}")

# Day366以上の投稿があるか確認
over_365 = []
for post_id, title in all_posts:
    if title:
        match = day_pattern.search(title)
        if match:
            day_num = int(match.group(1))
            if day_num > 365:
                over_365.append((post_id, title, day_num))

if over_365:
    print(f"\nDay366以上の投稿: {len(over_365)}件")
    for post_id, title, day_num in over_365[:10]:
        print(f"  Day{day_num:03d} - post_id={post_id}, title={title[:50]}")

# Day001～Day365の範囲で欠けている番号を確認
if len(day_posts) < 365:
    existing_days = set(day_numbers)
    missing_days = [d for d in range(1, 366) if d not in existing_days]
    print(f"\n欠けているDay番号: {len(missing_days)}件")
    if len(missing_days) <= 20:
        print(f"  {missing_days}")
    else:
        print(f"  最初の20件: {missing_days[:20]}")

conn.close()
