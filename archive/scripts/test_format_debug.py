"""フォーマットのデバッグ"""
from twitter_poster import TwitterPoster
from config import Config
import re

# 実際のタイトルをテスト
title = "語録４９ | Pursah's Gospelのブログ"
link = "https://ameblo.jp/pursahs-gospel/entry-11575416820.html"

# 正規化のテスト
normalized_title = title
if 'ameblo.jp/pursahs-gospel' in link or 'ameba.jp/profile/general/pursahs-gospel' in link:
    pattern = r'\s*\|\s*Pursah\'?s Gospelのブログ\s*$'
    print(f"Pattern: {pattern}")
    print(f"Before: {repr(normalized_title)}")
    normalized_title = re.sub(pattern, '', normalized_title)
    print(f"After:  {repr(normalized_title)}")
    print(f"Match: {normalized_title != title}")

# TwitterPosterでテスト
poster = TwitterPoster(Config.get_twitter_credentials_pursahs())
content = "テストコンテンツ"
result = poster.format_blog_post(title, content, link)
print(f"\nformat_blog_post result (first 50 chars): {result[:50]}")




