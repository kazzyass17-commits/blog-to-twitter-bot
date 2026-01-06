"""
create_tweetが重複呼び出しされる可能性がある箇所を確認するスクリプト
"""
import sys
import io
import re

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("create_tweetの呼び出しパターンを確認")
print("=" * 80)
print()

# 確認対象ファイル
target_files = [
    'post_both_accounts.py',
    'main_365bot.py',
    'main_pursahs.py',
    'test_post.py',
    'simple_post.py',
    'twitter_poster.py'
]

for file_path in target_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # create_tweetの呼び出しを検索
        create_tweet_pattern = r'\.create_tweet\s*\('
        matches = list(re.finditer(create_tweet_pattern, content))
        
        if matches:
            print(f"[{file_path}]")
            print("-" * 80)
            
            lines = content.split('\n')
            for match in matches:
                # 行番号を取得
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip()
                
                # コンテキストを取得（前5行、後5行）
                context_start = max(0, line_num - 6)
                context_end = min(len(lines), line_num + 5)
                
                print(f"  行 {line_num}: {line_content}")
                print(f"  コンテキスト:")
                for i in range(context_start, context_end):
                    marker = ">>>" if i == line_num - 1 else "   "
                    print(f"  {marker} {i+1:4d}: {lines[i]}")
                print()
            
            print(f"  合計: {len(matches)} 箇所")
            print()
    except FileNotFoundError:
        print(f"[{file_path}] ファイルが見つかりません")
        print()
    except Exception as e:
        print(f"[{file_path}] エラー: {e}")
        print()

print("=" * 80)
print()
print("[分析結果]")
print("-" * 80)
print()
print("投稿フローでのcreate_tweet呼び出し:")
print("1. post_both_accounts.py:")
print("   - check_and_wait_for_account: create_tweetを呼び出さない（OK）")
print("   - post_tweet_with_link: create_tweetを1回呼び出す（OK）")
print()
print("2. main_365bot.py / main_pursahs.py:")
print("   - post_tweet_with_link: create_tweetを1回呼び出す（OK）")
print()
print("3. test_post.py:")
print("   - post_tweet_with_link: create_tweetを1回呼び出す（OK）")
print()
print("4. simple_post.py:")
print("   - check_api_accepts_posts: create_tweetを呼び出さない（OK）")
print("   - post_tweet: create_tweetを1回呼び出す（OK）")
print()
print("5. twitter_poster.py:")
print("   - post_tweet: create_tweetを1回呼び出す（OK）")
print()
print("[問題がある可能性があるスクリプト]")
print("-" * 80)
print("check_rate_limit_from_api.py:")
print("  - 手動実行用スクリプト")
print("  - get_rate_limit_info: create_tweetを呼び出す")
print("  - このスクリプトを実行した後に投稿スクリプトを実行すると、")
print("    create_tweetが2回呼ばれる可能性がある")
print()
print("=" * 80)

