"""投稿テキストの文字数を確認"""
from database import PostDatabase
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config

db = PostDatabase()
posts = db.get_all_posts('http://notesofacim.blog.fc2.com/')
post = [p for p in posts if p['id'] == 347][0]

fetcher = BlogFetcher(post['link'])
page_content = fetcher.fetch_latest_post()

poster = TwitterPoster(Config.get_twitter_credentials_365bot())
tweet_text = poster.format_blog_post(
    page_content.get('title', ''),
    page_content.get('content', ''),
    page_content.get('link', '')
)

final_text = f"{tweet_text}\n{page_content.get('link', '')}"

print(f"ツイートテキスト文字数: {len(tweet_text)}")
print(f"最終テキスト文字数（URL含む）: {len(final_text)}")
print(f"188文字以内: {len(final_text) <= 188}")
print(f"\nツイートテキスト（最初の200文字）:")
print(tweet_text[:200])

