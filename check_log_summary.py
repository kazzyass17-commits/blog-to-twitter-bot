"""本日のログをまとめて確認"""
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# post_both_accounts.logを確認
print("="*70)
print("post_both_accounts.log の確認")
print("="*70)

try:
    with open('post_both_accounts.log', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
except FileNotFoundError:
    print("post_both_accounts.logが見つかりません")
    lines = []

today = '2026-01-21'
today_lines = [l for l in lines if today in l]

print(f"\n本日の全実行開始ログ:")
start_lines = [l for l in today_lines if 'ブログ→Twitter自動投稿ボット開始' in l]
for line in start_lines:
    print(f"  {line.rstrip()}")

print(f"\n本日の全投稿履歴記録ログ:")
record_lines = [l for l in today_lines if '投稿履歴を記録' in l]
for line in record_lines:
    print(f"  {line.rstrip()}")

print(f"\n本日の投稿成功ログ:")
success_lines = [l for l in today_lines if '投稿成功' in l]
for line in success_lines:
    print(f"  {line.rstrip()}")

# 他のログファイルも確認
print("\n" + "="*70)
print("他のログファイルの確認")
print("="*70)

other_logs = ['bot_365bot.log', 'bot_pursahs.log', 'bot.log']
for log_file in other_logs:
    if os.path.exists(log_file):
        print(f"\n{log_file}:")
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                other_lines = f.readlines()
            other_today = [l for l in other_lines if today in l]
            print(f"  本日のログ: {len(other_today)}行")
            if other_today:
                print("  最新5行:")
                for line in other_today[-5:]:
                    print(f"    {line.rstrip()}")
        except Exception as e:
            print(f"  読み込みエラー: {e}")
    else:
        print(f"\n{log_file}: ファイルが存在しません")
