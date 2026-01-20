"""正規表現パターンのテスト"""
import re

# テストデータ（実際の問題のコンテンツを模倣）
test_content = 'ブログトップ記事一覧画像一覧語録 (Logion) １語録 (Logion) １そして彼は言った。「これらの言葉の解釈を見出す者は死を味わうことがない。」'

print('=== 元のコンテンツ ===')
print(test_content)
print()

# 語録番号パターン
goroku_pattern = r'語録(?:\s*\([^)]+\)\s*)?[０-９0-9]+'

# パターン1: ブログトップ...語録XX
pattern1 = rf'ブログトップ.*?{goroku_pattern}'
match1 = re.search(pattern1, test_content, flags=re.DOTALL)
print(f'パターン1マッチ: {bool(match1)}')
if match1:
    print(f'  マッチ部分: {match1.group()}')

# クリーニング
cleaned = test_content
cleaned = re.sub(rf'ブログトップ.*?{goroku_pattern}\s*\|\s*Pursah\'?s Gospelのブログ\s*{goroku_pattern}', '', cleaned, flags=re.DOTALL)
cleaned = re.sub(rf'ブログトップ.*?{goroku_pattern}\s*\|\s*パーサによるトマスの福音書\s*{goroku_pattern}', '', cleaned, flags=re.DOTALL)
cleaned = re.sub(rf'{goroku_pattern}\s*\|\s*Pursah\'?s Gospelのブログ\s*{goroku_pattern}', '', cleaned, flags=re.DOTALL)
cleaned = re.sub(rf'{goroku_pattern}\s*\|\s*パーサによるトマスの福音書\s*{goroku_pattern}', '', cleaned, flags=re.DOTALL)
cleaned = re.sub(rf'ブログトップ.*?{goroku_pattern}', '', cleaned, flags=re.DOTALL)
cleaned = re.sub(rf'^{goroku_pattern}\s*{goroku_pattern}', '', cleaned, flags=re.MULTILINE)
cleaned = cleaned.strip()

print()
print('=== クリーニング後 ===')
print(cleaned)

# 先頭が語録で始まるか確認
goroku_head_pattern = r'^(語録(?:\s*\([^)]+\)\s*)?[０-９0-9]+)'
match_head = re.match(goroku_head_pattern, cleaned)
print()
print(f'先頭が語録で始まる: {bool(match_head)}')
if match_head:
    print(f'  マッチ部分: {match_head.group(1)}')
    goroku_part = match_head.group(1)
    rest_content = cleaned[len(goroku_part):].lstrip()
    cleaned = f'{goroku_part}\n{rest_content}'
    print()
    print('=== 最終結果 ===')
    print(cleaned)
else:
    print()
    print('=== 最終結果（変更なし） ===')
    print(cleaned)

print()
print('=' * 60)
print()

# テスト2: 通常パターン（語録XX）
test_content2 = 'ブログトップ記事一覧画像一覧語録６３語録６３たくさんの金を持っている豊かな人がいた。'
print('=== テスト2: 通常パターン（語録XX） ===')
print(f'元: {test_content2}')

cleaned2 = test_content2
cleaned2 = re.sub(rf'ブログトップ.*?{goroku_pattern}', '', cleaned2, flags=re.DOTALL)
cleaned2 = re.sub(rf'^{goroku_pattern}\s*{goroku_pattern}', '', cleaned2, flags=re.MULTILINE)
cleaned2 = cleaned2.strip()

match_head2 = re.match(goroku_head_pattern, cleaned2)
if match_head2:
    goroku_part2 = match_head2.group(1)
    rest_content2 = cleaned2[len(goroku_part2):].lstrip()
    cleaned2 = f'{goroku_part2}\n{rest_content2}'

print(f'後: {cleaned2}')


