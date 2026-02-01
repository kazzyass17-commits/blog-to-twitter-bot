"""本日のpursahsgospelの投稿ログを確認"""
import re
from datetime import datetime

# post_both_accounts.logを読み込み
try:
    with open('post_both_accounts.log', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
except FileNotFoundError:
    print("post_both_accounts.logが見つかりません")
    exit(1)

# 本日のログを抽出
today = '2026-01-21'
today_lines = [l for l in lines if today in l]

print(f"=== {today} のpursahsgospel関連ログ ===\n")

# pursahsgospel関連のログを抽出
pursahs_keywords = ['pursahsgospel', '投稿', 'record', 'エラー', '成功', '失敗', '記録']
relevant_lines = []
for line in today_lines:
    line_lower = line.lower()
    if any(kw in line_lower for kw in pursahs_keywords):
        relevant_lines.append(line.rstrip())

# 時間順に表示（最新100行）
print(f"関連ログ: {len(relevant_lines)}行（最新100行を表示）\n")
for line in relevant_lines[-100:]:
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

# 9時、12時、15時の投稿実行を確認
print(f"\n=== 9時、12時、15時の投稿実行確認 ===")
time_patterns = ['09:', '12:', '15:']
for pattern in time_patterns:
    matching_lines = [l for l in today_lines if pattern in l and 'pursahsgospel' in l.lower()]
    if matching_lines:
        print(f"\n{pattern}のログ:")
        for line in matching_lines[:10]:  # 最初の10行
            print(f"  {line.rstrip()}")
    else:
        print(f"\n{pattern}のログ: 見つかりません")

# 投稿履歴記録のログを確認
print(f"\n=== 投稿履歴記録のログ ===")
record_lines = [l for l in today_lines if '投稿履歴を記録' in l and 'pursahsgospel' in l.lower()]
if record_lines:
    print(f"記録ログ: {len(record_lines)}件")
    for line in record_lines:
        print(f"  {line.rstrip()}")
else:
    print("記録ログ: 見つかりません")

# エラーログを確認
print(f"\n=== エラーログ ===")
error_lines = [l for l in today_lines if 'エラー' in l and 'pursahsgospel' in l.lower()]
if error_lines:
    print(f"エラーログ: {len(error_lines)}件")
    for line in error_lines[:20]:  # 最初の20行
        print(f"  {line.rstrip()}")
else:
    print("エラーログ: 見つかりません")
