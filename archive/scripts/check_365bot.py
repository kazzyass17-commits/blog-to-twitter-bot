"""365botGaryのDay001-Day365を確認"""
import sqlite3
import re

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
cursor.execute("SELECT title FROM posts WHERE blog_url LIKE '%fc2%'")
rows = cursor.fetchall()

day_pattern = re.compile(r'Day(\d{3})')
day_posts = []
for r in rows:
    title = r[0] if r[0] else ''
    match = day_pattern.search(title)
    if match:
        day_num = int(match.group(1))
        if 1 <= day_num <= 365:
            day_posts.append(day_num)

print(f"DB総数: {len(rows)}件")
print(f"Day001-Day365: {len(day_posts)}件")

missing = [i for i in range(1, 366) if i not in day_posts]
if missing:
    print(f"欠番: {len(missing)}件")
    for m in missing:
        print(f"  Day{m:03d}")
else:
    print("欠番なし（Day001-Day365全て揃っている）")

conn.close()



