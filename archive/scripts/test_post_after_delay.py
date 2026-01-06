"""10分後に再投稿テストを実行"""
import time
import subprocess
from datetime import datetime, timedelta

delay_minutes = 10
delay_seconds = delay_minutes * 60

print("=" * 60)
print("再投稿テスト（10分後）")
print("=" * 60)
print(f"現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"実行予定時刻: {(datetime.now() + timedelta(seconds=delay_seconds)).strftime('%Y-%m-%d %H:%M:%S')}")
print(f"待機時間: {delay_minutes}分（{delay_seconds}秒）")
print("=" * 60)
print()

# 1分ごとに残り時間を表示しながら待機
for remaining in range(delay_seconds, 0, -60):
    minutes = remaining // 60
    seconds = remaining % 60
    print(f"残り時間: {minutes}分{seconds}秒 - 現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(60)

# 残り時間が60秒未満の場合
if delay_seconds % 60 != 0:
    remaining = delay_seconds % 60
    print(f"残り時間: {remaining}秒")
    time.sleep(remaining)

print()
print("=" * 60)
print("待機時間が終了しました。投稿テストを実行します。")
print("=" * 60)
print()

# 投稿テストを実行
subprocess.run(["python", "test_post.py", "--account", "both", "--yes"])







