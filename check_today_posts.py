"""本日のスケジュール投稿の記録状況を確認"""
import sqlite3

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# 全投稿履歴を取得
rows = cur.execute(
    'SELECT posted_at, post_id, twitter_handle, cycle_number, tweet_id FROM post_history WHERE posted_at LIKE ? ORDER BY posted_at',
    ('2026-01-21%',)
).fetchall()

print('='*70)
print('本日の投稿履歴（時刻順）')
print('='*70)

for r in rows:
    time_str = r[0][:19]  # 2026-01-21T09:43:21
    print(f'{time_str} - @{r[2]:15s} post_id={r[1]:3d}, cycle={r[3]}, tweet_id={r[4]}')

print('='*70)

# 365botGaryのスケジュール投稿
bot_rows = [r for r in rows if r[2]=='365botGary']
print(f'\n365botGary（スケジュール投稿）:')
for r in bot_rows:
    print(f'  {r[0][:19]} - post_id={r[1]}, tweet_id={r[4]}')
print(f'  合計: {len(bot_rows)}件（期待: 3件）')
if len(bot_rows) == 3:
    print('  [OK] 正常: 3件すべて記録されています')
else:
    print(f'  [NG] 異常: {len(bot_rows)}件しか記録されていません')

# pursahsgospelのスケジュール投稿
pursahs_rows = [r for r in rows if r[2]=='pursahsgospel']
print(f'\npursahsgospel（スケジュール投稿）:')
for r in pursahs_rows:
    time_str = r[0][:19]
    hour = int(time_str[11:13])
    time_type = 'スケジュール' if hour in [9, 12, 15] else '手動'
    print(f'  {time_str} - post_id={r[1]}, tweet_id={r[4]} ({time_type})')

# 9時、12時、15時のスケジュール投稿をカウント
schedule_count = len([r for r in pursahs_rows if int(r[0][11:13]) in [9, 12, 15]])
print(f'  スケジュール投稿: {schedule_count}件（期待: 2件）')
print(f'  手動投稿: {len(pursahs_rows) - schedule_count}件')
print(f'  合計: {len(pursahs_rows)}件')

if schedule_count == 2:
    print('  [OK] 正常: スケジュール投稿2件が記録されています')
else:
    print(f'  [NG] 異常: スケジュール投稿が{schedule_count}件しか記録されていません')

conn.close()
