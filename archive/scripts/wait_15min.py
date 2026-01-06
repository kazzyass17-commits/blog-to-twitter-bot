# -*- coding: utf-8 -*-
"""15分待機スケジュール表示・確認"""
from datetime import datetime, timedelta

# 開始時刻（15:28:03）
start_time = datetime(2026, 1, 4, 15, 28, 3)
now = datetime.now()
wait_until = start_time + timedelta(minutes=15)
elapsed = (now - start_time).total_seconds()
remaining = (wait_until - now).total_seconds()

print("=" * 60)
print("15分待機スケジュール確認")
print("=" * 60)
print(f"開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"再試行時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"経過時間: {int(elapsed // 60)}分 {int(elapsed % 60)}秒")
print("=" * 60)

if elapsed >= 900:  # 15分 = 900秒
    print("[OK] 待機時間が終了しました。再試行可能です。")
    print("以下のコマンドで再試行してください:")
    print("python test_post.py --account 365bot --no-confirm")
else:
    print(f"[待機中] 残り時間: {int(remaining // 60)}分 {int(remaining % 60)}秒")
    print("まだ待機中です。")
print("=" * 60)

