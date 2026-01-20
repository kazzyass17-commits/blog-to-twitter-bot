"""語録１の再投稿テスト"""
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config

# 語録１のURL
url = 'https://ameblo.jp/pursahs-gospel/entry-11568990494.html'

# コンテンツ取得
print('=== コンテンツ取得中 ===')
fetcher = BlogFetcher(url)
page_content = fetcher.fetch_latest_post()

print('=== 取得したコンテンツ ===')
print(f'タイトル: {page_content.get("title", "")}')
print(f'コンテンツ（最初の200文字）: {page_content.get("content", "")[:200]}')
print()

# フォーマット
credentials = Config.get_twitter_credentials_pursahs()
poster = TwitterPoster(credentials, account_key='pursahs', account_name='pursahsgospel')
tweet_text = poster.format_blog_post(
    title=page_content.get('title', ''),
    content=page_content.get('content', ''),
    link=url
)

print('=== フォーマット後のツイートテキスト ===')
print(tweet_text)
print()
print(f'文字数: {len(tweet_text)}')
print()

# 投稿実行
print('=== 投稿実行中 ===')
result = poster.post_tweet_with_link(text=tweet_text, link=url)
if result and result.get('success'):
    print(f'✓ 投稿成功！ ツイートID: {result.get("id")}')
else:
    print('✗ 投稿失敗')

