"""本日の全ログを確認して、9時、12時、15時の実行を確認"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    with open('post_both_accounts.log', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
except FileNotFoundError:
    print("post_both_accounts.logが見つかりません")
    exit(1)

today = '2026-01-21'
today_lines = [l for l in lines if today in l]

print("="*70)
print("本日の投稿実行開始ログ（全アカウント）")
print("="*70)

# 投稿開始のログを抽出
start_keywords = ['ブログ→Twitter自動投稿ボット開始', 'スケジュール実行を開始']
start_lines = []
for line in today_lines:
    if any(kw in line for kw in start_keywords):
        start_lines.append(line.rstrip())

if start_lines:
    print(f"実行開始ログ: {len(start_lines)}件\n")
    for line in start_lines:
        print(f"  {line}")
else:
    print("実行開始ログ: 見つかりません")

# 9時、12時、15時の実行を確認
print("\n" + "="*70)
print("9時、12時、15時の実行確認")
print("="*70)

time_slots = {
    '09時台': ['09:', 'T09:'],
    '12時台': ['12:', 'T12:'],
    '15時台': ['15:', 'T15:']
}

for time_name, patterns in time_slots.items():
    print(f"\n{time_name}:")
    matching_lines = [l for l in today_lines if any(pattern in l for pattern in patterns)]
    if matching_lines:
        print(f"  ログ行数: {len(matching_lines)}行")
        # 最初の5行と最後の5行を表示
        for line in matching_lines[:5]:
            print(f"    {line.rstrip()}")
        if len(matching_lines) > 10:
            print("    ...")
        for line in matching_lines[-5:]:
            print(f"    {line.rstrip()}")
    else:
        print("  ログが見つかりません")

# 365botとpursahsの投稿成功ログを確認
print("\n" + "="*70)
print("投稿成功ログの時刻分布")
print("="*70)

success_lines_365 = [l for l in today_lines if '投稿成功' in l and '365botGary' in l]
success_lines_pursahs = [l for l in today_lines if '投稿成功' in l and 'pursahsgospel' in l]

print(f"\n365botGary: {len(success_lines_365)}件")
for line in success_lines_365:
    time_part = line[:19] if len(line) > 19 else line[:10]
    print(f"  {time_part}")

print(f"\npursahsgospel: {len(success_lines_pursahs)}件")
for line in success_lines_pursahs:
    time_part = line[:19] if len(line) > 19 else line[:10]
    print(f"  {time_part}")
