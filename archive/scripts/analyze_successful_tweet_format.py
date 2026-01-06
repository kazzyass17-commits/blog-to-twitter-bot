"""
成功した投稿のフォーマットを詳しく分析
"""
import sys
import io
import sqlite3
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config
import tweepy

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_successful_tweet(tweet_id: str, account_key: str):
    """成功した投稿を詳しく分析"""
    account_name = '365botGary' if account_key == '365bot' else 'pursahsgospel'
    credentials = Config.get_twitter_credentials_365bot() if account_key == '365bot' else Config.get_twitter_credentials_pursahs()
    
    print("=" * 80)
    print(f"成功した投稿の分析: {account_name}")
    print(f"ツイートID: {tweet_id}")
    print("=" * 80)
    print()
    
    # データベースから投稿情報を取得
    conn = sqlite3.connect('posts.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ph.*, p.title, p.content, p.link
        FROM post_history ph
        JOIN posts p ON ph.post_id = p.id
        WHERE ph.tweet_id = ?
    ''', (tweet_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"  ⚠ データベースに投稿情報が見つかりませんでした")
        return
    
    # 実際のツイート内容を取得
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
            actual_text = tweet.data.text
            print(f"[実際のツイート内容]")
            print(f"文字数: {len(actual_text)} 文字")
            print(f"投稿日時: {tweet.data.created_at}")
            print()
            print("全文:")
            print(actual_text)
            print()
            print(f"文字数詳細:")
            print(f"  全体: {len(actual_text)} 文字")
            
            # URLを検出
            import re
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, actual_text)
            if urls:
                url = urls[0]
                text_without_url = actual_text.replace(url, '').strip()
                print(f"  URL: {url} ({len(url)} 文字)")
                print(f"  テキスト部分: {len(text_without_url)} 文字")
            else:
                text_without_url = actual_text
                print(f"  URLなし")
                print(f"  テキスト部分: {len(text_without_url)} 文字")
            
            print()
            
            # 改行で分割
            lines = actual_text.split('\n')
            print(f"[構造分析]")
            print(f"行数: {len(lines)}")
            for i, line in enumerate(lines, 1):
                if line.strip() and not line.startswith('http'):
                    print(f"  行{i}: {len(line)} 文字 - {line[:50]}...")
                elif line.startswith('http'):
                    print(f"  行{i}: URL - {line}")
            
            print()
            
            # データベースから取得した情報
            print(f"[データベースの情報]")
            print(f"タイトル: {row['title']}")
            print(f"URL: {row['link']}")
            print(f"コンテンツ（最初の200文字）: {row['content'][:200] if row['content'] else 'なし'}...")
            print()
            
            # ページからコンテンツを取得
            print(f"[現在の設定でフォーマットした場合]")
            page_content = BlogFetcher(row['link']).fetch_latest_post()
            if not page_content:
                page_content = {
                    'title': row['title'],
                    'content': row['content'] or '',
                    'link': row['link']
                }
            
            poster = TwitterPoster(credentials, account_key=account_key, account_name=account_name)
            formatted_text = poster.format_blog_post(
                title=page_content.get('title', ''),
                content=page_content.get('content', ''),
                link=page_content.get('link', row['link'])
            )
            
            print(f"フォーマット後のテキスト（URL除く）: {len(formatted_text)} 文字")
            print(f"フォーマット後のテキスト + URL: {len(formatted_text) + 1 + len(urls[0]) if urls else len(formatted_text)} 文字")
            print()
            print("全文:")
            print(formatted_text)
            print()
            
            # 比較
            print(f"[比較結果]")
            print(f"実際のツイート文字数: {len(actual_text)} 文字")
            if urls:
                print(f"実際のテキスト部分: {len(text_without_url)} 文字")
            print(f"現在の設定での文字数（URL含む）: {len(formatted_text) + 1 + len(urls[0]) if urls else len(formatted_text)} 文字")
            print(f"現在の設定での文字数（URL除く）: {len(formatted_text)} 文字")
            
            if urls:
                diff = len(text_without_url) - len(formatted_text)
                print(f"差（テキスト部分）: {diff} 文字")
                if abs(diff) > 5:
                    print(f"  ⚠ 文字数に大きな差があります")
                    
                    # 実際のテキストとフォーマット後のテキストを比較
                    print()
                    print(f"[詳細比較]")
                    print(f"実際のテキスト（最初の100文字）:")
                    print(f"  {text_without_url[:100]}")
                    print()
                    print(f"フォーマット後のテキスト（最初の100文字）:")
                    print(f"  {formatted_text[:100]}")
            
        else:
            print(f"  ⚠ ツイートを取得できませんでした")
    except Exception as e:
        print(f"  ⚠ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 成功した投稿を分析
    print("\n[365botGary]")
    analyze_successful_tweet('2007706817548431615', '365bot')
    print()
    print("\n[pursahsgospel]")
    analyze_successful_tweet('2007704172121207056', 'pursahs')

