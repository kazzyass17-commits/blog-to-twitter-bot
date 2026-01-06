"""
成功した投稿と今回のテスト投稿を比較するスクリプト
"""
import sqlite3
import sys
import io
from datetime import datetime
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config
import tweepy

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_tweet_content(tweet_id: str, credentials: dict, account_name: str):
    """ツイートIDから実際のツイート内容を取得"""
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
            return {
                'text': tweet.data.text,
                'created_at': tweet.data.created_at,
                'length': len(tweet.data.text)
            }
        else:
            return None
    except Exception as e:
        print(f"  エラー: {e}")
        return None

def format_post_for_comparison(post_data: dict, page_content: dict, account_key: str):
    """投稿をフォーマットして比較用のデータを返す"""
    credentials = Config.get_twitter_credentials_365bot() if account_key == '365bot' else Config.get_twitter_credentials_pursahs()
    poster = TwitterPoster(credentials, account_key=account_key, account_name='365botGary' if account_key == '365bot' else 'pursahsgospel')
    
    tweet_text = poster.format_blog_post(
        title=page_content.get('title', ''),
        content=page_content.get('content', ''),
        link=page_content.get('link', post_data.get('link', ''))
    )
    
    return {
        'formatted_text': tweet_text,
        'length': len(tweet_text),
        'length_with_url': len(tweet_text) + 24,  # URL(23) + 改行(1)
        'title': page_content.get('title', ''),
        'has_title': bool(page_content.get('title', '')),
        'content_preview': page_content.get('content', '')[:100]
    }

def compare_posts():
    """成功した投稿と今回のテスト投稿を比較"""
    print("=" * 80)
    print("成功した投稿と今回のテスト投稿の比較")
    print("=" * 80)
    print(f"比較時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    db = PostDatabase()
    conn = sqlite3.connect('posts.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 成功した投稿（最新の2件）
    successful_tweet_ids = {
        '365bot': '2007706817548431615',  # 最新の成功投稿
        'pursahs': '2007704172121207056'  # 最新の成功投稿
    }
    
    # 今回のテスト投稿のデータ（post_both_accounts.logから取得するか、データベースから最新の未投稿を取得）
    # 今回は、データベースから最新の未投稿を取得して比較
    print("[成功した投稿]")
    print()
    
    for account_key, tweet_id in successful_tweet_ids.items():
        account_name = '365botGary' if account_key == '365bot' else 'pursahsgospel'
        credentials = Config.get_twitter_credentials_365bot() if account_key == '365bot' else Config.get_twitter_credentials_pursahs()
        
        print(f"--- {account_name} ---")
        print(f"ツイートID: {tweet_id}")
        
        # データベースから投稿情報を取得
        cursor.execute('''
            SELECT ph.*, p.title, p.content, p.link
            FROM post_history ph
            JOIN posts p ON ph.post_id = p.id
            WHERE ph.tweet_id = ?
        ''', (tweet_id,))
        
        row = cursor.fetchone()
        if row:
            print(f"投稿日時: {row['posted_at']}")
            print(f"タイトル: {row['title']}")
            print(f"URL: {row['link']}")
            
            # 実際のツイート内容を取得
            print(f"\n実際のツイート内容を取得中...")
            tweet_content = get_tweet_content(tweet_id, credentials, account_name)
            
            if tweet_content:
                print(f"実際のツイート:")
                print(f"  文字数: {tweet_content['length']} 文字")
                print(f"  投稿日時: {tweet_content['created_at']}")
                print(f"  内容（最初の200文字）:")
                print(f"  {tweet_content['text'][:200]}...")
                print()
                
                # 現在の設定でフォーマットした場合の内容
                page_content = BlogFetcher(row['link']).fetch_latest_post()
                if not page_content:
                    page_content = {
                        'title': row['title'],
                        'content': row['content'] or '',
                        'link': row['link']
                    }
                
                formatted = format_post_for_comparison(
                    {'id': row['post_id'], 'link': row['link']},
                    page_content,
                    account_key
                )
                
                print(f"現在の設定でフォーマットした場合:")
                print(f"  文字数: {formatted['length']} 文字（URL含む: {formatted['length_with_url']} 文字）")
                print(f"  タイトル有無: {'あり' if formatted['has_title'] else 'なし'}")
                print(f"  内容（最初の200文字）:")
                print(f"  {formatted['formatted_text'][:200]}...")
                print()
                
                # 比較
                print(f"比較結果:")
                print(f"  実際のツイート文字数: {tweet_content['length']} 文字")
                print(f"  現在の設定での文字数: {formatted['length_with_url']} 文字")
                print(f"  差: {abs(tweet_content['length'] - formatted['length_with_url'])} 文字")
                if abs(tweet_content['length'] - formatted['length_with_url']) > 5:
                    print(f"  ⚠ 文字数に大きな差があります")
            else:
                print(f"  ⚠ 実際のツイート内容を取得できませんでした")
        else:
            print(f"  ⚠ データベースに投稿情報が見つかりませんでした")
        
        print()
    
    # 今回のテスト投稿（post_both_accounts.logから読み取るか、データベースから最新の未投稿を取得）
    print("[今回のテスト投稿]")
    print()
    
    # 今回選択された投稿のURL（post_both_accounts.logから読み取る）
    # 簡易的に、データベースから最新の未投稿を取得して比較
    blog_url_365bot = Config.BLOG_365BOT_URL
    blog_url_pursahs = Config.BLOG_PURSAHS_URL
    
    for account_key in ['365bot', 'pursahs']:
        account_name = '365botGary' if account_key == '365bot' else 'pursahsgospel'
        blog_url = blog_url_365bot if account_key == '365bot' else blog_url_pursahs
        twitter_handle = Config.TWITTER_365BOT_HANDLE if account_key == '365bot' else Config.TWITTER_PURSAHS_HANDLE
        
        print(f"--- {account_name} ---")
        
        # 最新の未投稿を取得（実際には選択された投稿を指定する必要がある）
        # 今回は、post_both_accounts.logから読み取ったURLを使用
        # 簡易的に、データベースからランダムに1件取得
        post_data = db.get_random_unposted_post(blog_url, twitter_handle)
        
        if post_data:
            page_url = post_data.get('link', '')
            print(f"投稿ID: {post_data['id']}")
            print(f"URL: {page_url}")
            print(f"タイトル: {post_data.get('title', '')}")
            
            # ページからコンテンツを取得
            page_content = BlogFetcher(page_url).fetch_latest_post()
            if not page_content:
                page_content = {
                    'title': post_data.get('title', ''),
                    'content': '',
                    'link': page_url
                }
            
            formatted = format_post_for_comparison(post_data, page_content, account_key)
            
            print(f"\nフォーマット結果:")
            print(f"  文字数: {formatted['length']} 文字（URL含む: {formatted['length_with_url']} 文字）")
            print(f"  タイトル有無: {'あり' if formatted['has_title'] else 'なし'}")
            print(f"  内容（最初の200文字）:")
            print(f"  {formatted['formatted_text'][:200]}...")
        else:
            print(f"  ⚠ 未投稿の投稿が見つかりませんでした")
        
        print()
    
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    from database import PostDatabase
    compare_posts()

