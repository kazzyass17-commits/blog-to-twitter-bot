"""過去のツイートを確認して、URLを含む投稿が成功していたか確認"""
import tweepy
from config import Config
from datetime import datetime, timedelta

# 365botGaryアカウントの認証情報を取得
credentials = Config.get_twitter_credentials_365bot()

# Tweepyクライアントを作成
client = tweepy.Client(
    bearer_token=credentials.get('bearer_token'),
    consumer_key=credentials.get('api_key'),
    consumer_secret=credentials.get('api_secret'),
    access_token=credentials.get('access_token'),
    access_token_secret=credentials.get('access_token_secret'),
    wait_on_rate_limit=True
)

# 自分のアカウント情報を取得
me = client.get_me()
print(f"アカウント: @{me.data.username}")

# 過去7日間のツイートを取得
print("\n過去7日間のツイートを確認中...")
start_time = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
tweets = client.get_users_tweets(
    id=me.data.id,
    max_results=50,
    tweet_fields=['created_at', 'text'],
    start_time=start_time
)

if tweets and tweets.data:
    print(f"\n{len(tweets.data)}件のツイートを取得しました\n")
    
    url_posts = []
    no_url_posts = []
    
    for tweet in tweets.data:
        text = tweet.text
        created_at = tweet.created_at
        has_url = 'http://' in text or 'https://' in text
        
        if has_url:
            url_posts.append((created_at, text[:100]))
        else:
            no_url_posts.append((created_at, text[:100]))
    
    print("=" * 60)
    print("URLを含む投稿")
    print("=" * 60)
    if url_posts:
        for created_at, text in url_posts[:10]:
            print(f"\n{created_at}")
            print(f"  {text}...")
    else:
        print("URLを含む投稿は見つかりませんでした")
    
    print("\n" + "=" * 60)
    print("URLを含まない投稿")
    print("=" * 60)
    if no_url_posts:
        for created_at, text in no_url_posts[:10]:
            print(f"\n{created_at}")
            print(f"  {text}...")
    else:
        print("URLを含まない投稿は見つかりませんでした")
    
    print(f"\n\n統計:")
    print(f"  URLを含む投稿: {len(url_posts)}件")
    print(f"  URLを含まない投稿: {len(no_url_posts)}件")
else:
    print("ツイートが見つかりませんでした")

