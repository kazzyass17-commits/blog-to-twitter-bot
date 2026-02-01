"""9時、12時、15時のpursahsgospel投稿ログを確認"""
import sys
import io

# 標準出力のエンコーディングを設定
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
print("9時、12時、15時のpursahsgospel投稿実行ログ")
print("="*70)

# 各時間帯のログを抽出
time_slots = {
    '09時台': ['09:', 'T09:'],
    '12時台': ['12:', 'T12:'],
    '15時台': ['15:', 'T15:']
}

for time_name, patterns in time_slots.items():
    print(f"\n{time_name}:")
    matching_lines = []
    for line in today_lines:
        if any(pattern in line for pattern in patterns):
            if 'pursahsgospel' in line.lower() or '投稿' in line or 'record' in line.lower():
                matching_lines.append(line.rstrip())
    
    if matching_lines:
        print(f"  見つかったログ: {len(matching_lines)}行")
        for line in matching_lines[:20]:  # 最初の20行
            print(f"    {line}")
    else:
        print("  ログが見つかりません")

# 投稿履歴記録のログを確認
print(f"\n" + "="*70)
print("投稿履歴記録のログ（pursahsgospel）")
print("="*70)

record_lines = [l for l in today_lines if '投稿履歴を記録' in l and 'pursahsgospel' in l.lower()]
if record_lines:
    print(f"記録ログ: {len(record_lines)}件")
    for line in record_lines:
        print(f"  {line.rstrip()}")
else:
    print("記録ログ: 見つかりません")

# 投稿成功のログを確認
print(f"\n" + "="*70)
print("投稿成功のログ（pursahsgospel）")
print("="*70)

success_lines = [l for l in today_lines if ('投稿成功' in l or 'success' in l.lower()) and 'pursahsgospel' in l.lower()]
if success_lines:
    print(f"成功ログ: {len(success_lines)}件")
    for line in success_lines:
        print(f"  {line.rstrip()}")
else:
    print("成功ログ: 見つかりません")
