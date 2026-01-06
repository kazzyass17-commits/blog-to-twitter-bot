# -*- coding: utf-8 -*-
"""フォーマットの詳細確認"""
import sys
import io
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("365botGaryのフォーマット確認")
print("=" * 60)

# 365botGaryのテスト
url_365bot = "http://notesofacim.blog.fc2.com/blog-entry-193.html"
fetcher_365bot = BlogFetcher(url_365bot)
content_365bot = fetcher_365bot.fetch_latest_post()

if content_365bot:
    poster_365bot = TwitterPoster(Config.get_twitter_credentials_365bot())
    tweet_text_365bot = poster_365bot.format_blog_post(
        title=content_365bot.get('title', ''),
        content=content_365bot.get('content', ''),
        link=url_365bot
    )
    
    print(f"タイトル: {content_365bot.get('title', '')}")
    print(f"\nフォーマット後のテキスト:")
    print(tweet_text_365bot)
    print(f"\n文字数: {len(tweet_text_365bot)}文字")
    
    # タイトルが含まれているか確認
    title_normalized = content_365bot.get('title', '').replace('ACIM学習ガイド ', '').replace('ACIM学習ノート ', '').replace('神の使い', '神の使者')
    if title_normalized in tweet_text_365bot:
        print("[OK] タイトルが含まれています")
    else:
        print("[NG] タイトルが含まれていません")
    
    # リンクを含めた完全なツイート（post_tweet_with_linkと同じ形式）
    full_tweet_365bot = f"{tweet_text_365bot}\n{url_365bot}"
    print(f"\n完全なツイート（リンク含む、post_tweet_with_linkと同じ形式）:")
    print(full_tweet_365bot)
    print(f"文字数: {len(full_tweet_365bot)}文字")
    print(f"Twitterカウント: {len(tweet_text_365bot)} + 改行(1) + URL(23) = {len(tweet_text_365bot) + 1 + 23}文字")
    if url_365bot in full_tweet_365bot:
        print("[OK] リンクが含まれています")
    else:
        print("[NG] リンクが含まれていません")

print("\n" + "=" * 60)
print("pursahsgospelのフォーマット確認")
print("=" * 60)

# pursahsgospelのテスト
url_pursahs = "https://ameblo.jp/pursahs-gospel/entry-11577151274.html"
fetcher_pursahs = BlogFetcher(url_pursahs)
content_pursahs = fetcher_pursahs.fetch_latest_post()

if content_pursahs:
    poster_pursahs = TwitterPoster(Config.get_twitter_credentials_pursahs())
    tweet_text_pursahs = poster_pursahs.format_blog_post(
        title=content_pursahs.get('title', ''),
        content=content_pursahs.get('content', ''),
        link=url_pursahs
    )
    
    print(f"タイトル: {content_pursahs.get('title', '')}")
    print(f"\nフォーマット後のテキスト:")
    print(tweet_text_pursahs)
    print(f"\n文字数: {len(tweet_text_pursahs)}文字")
    
    # 語録の後に改行が入っているか確認
    import re
    match = re.search(r'(語録\d+)(\n)', tweet_text_pursahs)
    if match:
        print(f"[OK] 語録の後に改行が入っています: '{match.group(1)}' の後に改行")
    else:
        # 語録の後に改行がない場合
        match_no_newline = re.search(r'(語録\d+)([^\n])', tweet_text_pursahs)
        if match_no_newline:
            print(f"[NG] 語録の後に改行が入っていません: '{match_no_newline.group(1)}' の後に '{match_no_newline.group(2)[:1]}'")
        else:
            print("[?] 語録のパターンが見つかりません")
    
    # リンクを含めた完全なツイート（post_tweet_with_linkと同じ形式）
    full_tweet_pursahs = f"{tweet_text_pursahs}\n{url_pursahs}"
    print(f"\n完全なツイート（リンク含む、post_tweet_with_linkと同じ形式）:")
    print(full_tweet_pursahs)
    print(f"文字数: {len(full_tweet_pursahs)}文字")
    print(f"Twitterカウント: {len(tweet_text_pursahs)} + 改行(1) + URL(23) = {len(tweet_text_pursahs) + 1 + 23}文字")
    if url_pursahs in full_tweet_pursahs:
        print("[OK] リンクが含まれています")
    else:
        print("[NG] リンクが含まれていません")

print("\n" + "=" * 60)

