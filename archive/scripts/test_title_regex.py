"""タイトル正規化のテスト"""
import re

test_titles = [
    "語録２２ | Pursah's Gospelのブログ",
    "語録１１０ | Pursah's Gospelのブログ",
    "語録９ | Pursah's Gospelのブログ",
]

pattern = r'\s*\|\s*Pursah\'?s Gospelのブログ\s*$'

for title in test_titles:
    result = re.sub(pattern, '', title)
    print(f"Original: {title}")
    print(f"Result:   {result}")
    print(f"Match: {result != title}")
    print()




