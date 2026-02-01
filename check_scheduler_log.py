"""スケジューラーのログを確認"""
import re
from datetime import datetime

# スケジューラーログを読み込み
try:
    with open('scheduler.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    print("scheduler.logが見つかりません")
    exit(1)

# 本日のログを抽出
today = '2026-01-21'
today_lines = [l for l in lines if today in l]

print(f"=== {today} のスケジューラーログ ===\n")

# 投稿関連のログを抽出
post_keywords = ['投稿', 'スケジュール', '実行', '成功', 'エラー', '開始']
relevant_lines = []
for line in today_lines:
    if any(kw in line for kw in post_keywords):
        relevant_lines.append(line.rstrip())

# 時間順に表示
for line in relevant_lines[-100:]:  # 最新100行
    print(line)

print(f"\n=== 本日の投稿履歴（データベース） ===")
import sqlite3
conn = sqlite3.connect('posts.db')
cur = conn.cursor()
rows = cur.execute(
    'SELECT posted_at, post_id, twitter_handle, cycle_number FROM post_history WHERE twitter_handle=? AND posted_at LIKE ? ORDER BY posted_at',
    ('pursahsgospel', f'{today}%')
).fetchall()

if rows:
    for r in rows:
        print(f"  {r[0]} - post_id={r[1]}, cycle={r[3]}")
else:
    print("  投稿履歴なし")
print(f"\n合計: {len(rows)}件")
