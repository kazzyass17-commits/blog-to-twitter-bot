"""明日の投稿準備状況を確認"""
import sqlite3
import os
import sys
import re
sys.path.insert(0, '.')
from database import PostDatabase

db = PostDatabase()

# 365botGaryの状況
blog_url_365 = "http://notesofacim.blog.fc2.com/"
twitter_handle_365 = "365botGary"
cycle_365 = db.get_current_cycle_number(blog_url_365, twitter_handle_365)
unposted_all_365 = db.get_unposted_posts_in_cycle(blog_url_365, twitter_handle_365, cycle_365)
# Day001～Day365の投稿のみをフィルタリング（重複を除外）
day_pattern = re.compile(r'Day(\d{3})')
unposted_365 = []
seen_days = set()
for post in unposted_all_365:
    title = post.get('title', '')
    match = day_pattern.search(title)
    if match:
        day_num = int(match.group(1))
        if 1 <= day_num <= 365 and day_num not in seen_days:
            unposted_365.append(post)
            seen_days.add(day_num)

# pursahsgospelの状況
blog_url_pursahs = "https://www.ameba.jp/profile/general/pursahs-gospel/"
twitter_handle_pursahs = "pursahsgospel"
cycle_pursahs = db.get_current_cycle_number(blog_url_pursahs, twitter_handle_pursahs)
unposted_all_pursahs = db.get_unposted_posts_in_cycle(blog_url_pursahs, twitter_handle_pursahs, cycle_pursahs)
# 「語録」を含む投稿のみをフィルタリング（『原書』と『索引』は除外）
unposted_pursahs = []
for post in unposted_all_pursahs:
    title = post.get('title', '') or ''
    if '語録' in title and '原書' not in title and '索引' not in title:
        unposted_pursahs.append(post)

print("="*60)
print("明日の投稿準備状況")
print("="*60)
print(f"\n365botGary:")
print(f"  現在のサイクル: #{cycle_365}")
print(f"  未投稿数: {len(unposted_365)}件（Day001～Day365のみ）")
print(f"\npursahsgospel:")
print(f"  現在のサイクル: #{cycle_pursahs}")
print(f"  未投稿数: {len(unposted_pursahs)}件（語録のみ）")

# スケジューラーのロックファイルを確認
lock_file = "scheduler.lock"
if os.path.exists(lock_file):
    print(f"\nスケジューラー: 実行中の可能性あり（ロックファイル存在）")
else:
    print(f"\nスケジューラー: 実行中ではない（ロックファイルなし）")
