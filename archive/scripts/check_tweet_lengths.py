"""
投稿されたツイートの文字数を確認
"""
import sys
import io
import tweepy
from config import Config

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 投稿されたツイートID
tweet_ids = {
    '365bot': '2008123313303048228',
    'pursahs': '2008123316272590920'
}

print("=" * 80)
print("投稿されたツイートの文字数確認")
print("=" * 80)
print()

for account_key, tweet_id in tweet_ids.items():
    account_name = '365botGary' if account_key == '365bot' else 'pursahsgospel'
    credentials = Config.get_twitter_credentials_365bot() if account_key == '365bot' else Config.get_twitter_credentials_pursahs()
    
    print(f"[{account_name}]")
    print(f"ツイートID: {tweet_id}")
    print("-" * 80)
    
    try:
        client = tweepy.Client(
            bearer_token=credentials.get('bearer_token'),
            consumer_key=credentials.get('api_key'),
            consumer_secret=credentials.get('api_secret'),
            access_token=credentials.get('access_token'),
            access_token_secret=credentials.get('access_token_secret'),
            wait_on_rate_limit=False
        )
        
        tweet = client.get_tweet(tweet_id, tweet_fields=['created_at', 'text'])
        
        if tweet and tweet.data:
            text = tweet.data.text
            print(f"ツイート内容:")
            print(text)
            print()
            print(f"文字数: {len(text)} 文字")
            
            # URLを検出
            import re
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, text)
            if urls:
                url = urls[0]
                text_without_url = text.replace(url, '').strip()
                print(f"URL: {url} ({len(url)} 文字)")
                print(f"テキスト部分: {len(text_without_url)} 文字")
                print(f"合計: {len(text_without_url)} + {len(url)} = {len(text)} 文字")
            else:
                print(f"URLなし")
                print(f"テキスト部分: {len(text)} 文字")
            
            print(f"投稿日時: {tweet.data.created_at}")
        else:
            print("  ⚠ ツイートを取得できませんでした")
    except Exception as e:
        print(f"  ⚠ エラー: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print()

print("=" * 80)

