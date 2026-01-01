"""実際のタイトルをデバッグ"""
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config

url = "https://ameblo.jp/pursahs-gospel/entry-11575416820.html"
fetcher = BlogFetcher(url)
page_content = fetcher.fetch_latest_post()

if page_content:
    title = page_content.get('title', '')
    print(f"実際のタイトル: {title}")
    print(f"タイトルの文字コード: {repr(title)}")
    
    # TwitterPosterでフォーマット
    poster = TwitterPoster(Config.get_twitter_credentials_pursahs())
    result = poster.format_blog_post(title, page_content.get('content', ''), url)
    print(f"\nフォーマット後のタイトル（最初の50文字）: {result[:50]}")

