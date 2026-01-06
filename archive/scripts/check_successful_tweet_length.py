# -*- coding: utf-8 -*-
"""成功した投稿の実際の文字数を確認"""
import tweepy
from config import Config

# 成功した投稿のツイートID
tweet_ids = ["2007673086020334017", "2007669957476397294"]

credentials = Config.get_twitter_credentials_365bot()
client = tweepy.Client(
    bearer_token=credentials['bearer_token'],
    consumer_key=credentials['api_key'],
    consumer_secret=credentials['api_secret'],
    access_token=credentials['access_token'],
    access_token_secret=credentials['access_token_secret']
)

for tweet_id in tweet_ids:
    try:
        tweet = client.get_tweet(tweet_id, tweet_fields=['text'])
        if tweet and tweet.data:
            text = tweet.data.text
            print("=" * 60)
            print(f"ツイートID: {tweet_id}")
            print(f"実際の文字数: {len(text)}文字")
            print(f"内容（最初の100文字）: {text[:100]}...")
            print()
            
            # URLを抽出
            import re
            url_match = re.search(r'https?://[^\s]+', text)
            if url_match:
                url = url_match.group(0)
                text_without_url = text.replace(url, '').strip()
                print(f"URL: {url}")
                print(f"URL長: {len(url)}文字（Xは23文字としてカウント）")
                print(f"本文（URL除く）: {len(text_without_url)}文字")
                print(f"Xカウント: {len(text_without_url)} + 改行(1) + URL(23) = {len(text_without_url) + 1 + 23}文字")
            print()
    except Exception as e:
        print(f"エラー ({tweet_id}): {e}")




