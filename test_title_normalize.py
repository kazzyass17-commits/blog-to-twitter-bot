"""タイトル正規化の詳細テスト"""
from twitter_poster import TwitterPoster
from config import Config
import re

# 実際のタイトルをテスト
test_cases = [
    ("語録９９ | Pursah's Gospelのブログ", "https://ameblo.jp/pursahs-gospel/entry-11577153204.html"),
    ("ACIM学習ガイド Day196（神の使い:P.318、ACIM:T-06.I.13-14:01）", "http://notesofacim.blog.fc2.com/blog-entry-326.html"),
]

for title, link in test_cases:
    print(f"\n=== Test Case ===")
    print(f"Title: {title}")
    print(f"Link: {link}")
    
    # 正規化処理を手動で実行
    normalized_title = title
    if 'notesofacim.blog.fc2.com' in link:
        normalized_title = re.sub(r'^ACIM学習(ガイド|ノート)\s+', '', normalized_title)
        normalized_title = normalized_title.replace('神の使い', '神の使者')
        print(f"After 365botGary normalization: {normalized_title}")
    elif 'ameblo.jp/pursahs-gospel' in link or 'ameba.jp/profile/general/pursahs-gospel' in link:
        pattern = r'\s*\|\s*Pursah\'?s Gospelのブログ\s*$'
        print(f"Pattern: {pattern}")
        print(f"Before: {repr(normalized_title)}")
        normalized_title = re.sub(pattern, '', normalized_title)
        print(f"After:  {repr(normalized_title)}")
    
    # TwitterPosterでテスト
    poster = TwitterPoster(Config.get_twitter_credentials_pursahs() if 'pursahs' in link else Config.get_twitter_credentials_365bot())
    result = poster.format_blog_post(title, "テストコンテンツ", link)
    print(f"format_blog_post result (first 50 chars): {result[:50]}")

