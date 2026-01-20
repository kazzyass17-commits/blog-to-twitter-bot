"""pursahsgospelのみ投稿テスト"""
import tweepy
from config import Config
from datetime import datetime

credentials = Config.get_twitter_credentials_pursahs()
client = tweepy.Client(
    bearer_token=credentials.get('bearer_token'),
    consumer_key=credentials.get('api_key'),
    consumer_secret=credentials.get('api_secret'),
    access_token=credentials.get('access_token'),
    access_token_secret=credentials.get('access_token_secret')
)

test_text = f"テスト投稿 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
print(f"投稿内容: {test_text}")

try:
    response = client.create_tweet(text=test_text)
    if response and response.data:
        print(f"成功! ツイートID: {response.data['id']}")
except tweepy.Forbidden as e:
    print(f"403エラー: {e}")
except Exception as e:
    print(f"エラー: {type(e).__name__}: {e}")


