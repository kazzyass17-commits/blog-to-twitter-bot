"""投稿可能かどうかを確認"""
from rate_limit_checker import check_and_wait_for_account
from config import Config
from datetime import datetime

print("=" * 60)
print("投稿可能かどうかを確認")
print("=" * 60)
print(f"現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 365botGary
print("[365botGary]")
result_365bot = check_and_wait_for_account('365bot', '365botGary', skip_wait=True)
if result_365bot:
    print("[OK] 投稿可能")
else:
    print("[NG] 投稿不可（レート制限中）")

print()

# pursahsgospel
print("[pursahsgospel]")
result_pursahs = check_and_wait_for_account('pursahs', 'pursahsgospel', skip_wait=True)
if result_pursahs:
    print("[OK] 投稿可能")
else:
    print("[NG] 投稿不可（レート制限中）")

print()
print("=" * 60)
if result_pursahs:
    print("pursahsgospelアカウントで投稿可能です")
else:
    print("pursahsgospelアカウントはレート制限中です")

