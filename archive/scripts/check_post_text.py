"""
投稿文を確認するスクリプト
実際に投稿せずに、投稿予定の文章を確認し、mdファイルに書き込む
"""
import logging
import sys
from datetime import datetime
from database import PostDatabase
from twitter_poster import TwitterPoster
from blog_fetcher import BlogFetcher
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def check_post_text(blog_url: str, twitter_handle: str, save_to_md: bool = True):
    """
    投稿文を確認し、mdファイルに書き込む
    
    Args:
        blog_url: ブログURL
        twitter_handle: Twitterハンドル
        save_to_md: mdファイルに保存するかどうか（デフォルト: True）
    """
    logger.info("=" * 60)
    logger.info("投稿文確認スクリプト")
    logger.info("=" * 60)
    
    try:
        db = PostDatabase()
        
        # データベース内の投稿数を確認
        all_posts = db.get_all_posts(blog_url)
        logger.info(f"\nデータベース内の投稿数: {len(all_posts)} 件")
        
        if not all_posts:
            logger.warning("データベースに投稿がありません。")
            logger.info("先に 'python init_posts.py' を実行してください。")
            return
        
        # 未投稿の投稿を取得
        post_data = db.get_random_unposted_post(blog_url, twitter_handle)
        
        if not post_data:
            logger.warning("未投稿の投稿がありません。")
            return
        
        page_url = post_data.get('link', '')
        if not page_url:
            logger.warning("URLが取得できませんでした")
            return
        
        logger.info(f"\n選択された投稿:")
        logger.info(f"  ID: {post_data['id']}")
        logger.info(f"  URL: {page_url}")
        logger.info(f"  タイトル（DB）: {post_data.get('title', '')}")
        
        # ページからコンテンツを取得
        logger.info("\nページからコンテンツを取得中...")
        fetcher = BlogFetcher(page_url)
        page_content = fetcher.fetch_latest_post()
        
        if not page_content:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url}")
            # URLのみでテスト
            page_content = {
                'title': post_data.get('title', ''),
                'content': '',
                'link': page_url,
                'published_date': '',
                'author': '',
            }
        
        logger.info(f"  タイトル: {page_content.get('title', 'タイトルなし')}")
        logger.info(f"  リンク: {page_content.get('link', page_url)}")
        logger.info(f"  コンテンツ（最初の200文字）: {page_content.get('content', '')[:200]}...")
        
        # Twitter投稿テキストをフォーマット
        credentials = Config.get_twitter_credentials_365bot() if twitter_handle == Config.TWITTER_365BOT_HANDLE else Config.get_twitter_credentials_pursahs()
        poster = TwitterPoster(credentials)
        
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=page_content.get('link', page_url)
        )
        
        logger.info(f"\n{'='*60}")
        logger.info("投稿予定のツイートテキスト:")
        logger.info(f"{'='*60}")
        logger.info(f"\n{tweet_text}\n")
        logger.info(f"文字数: {len(tweet_text)} 文字")
        
        logger.info(f"\n実際の投稿形式（改行とURLを含む）:")
        logger.info(f"{'='*60}")
        actual_tweet = f"{tweet_text}\n{page_content.get('link', page_url)}"
        logger.info(f"\n{actual_tweet}\n")
        # Twitter APIはURLを23文字としてカウントする
        twitter_counted_length = len(tweet_text) + 1 + 23  # tweet_text + 改行(1) + URL(23)
        actual_length = len(actual_tweet)  # 実際の文字数
        logger.info(f"文字数: {len(tweet_text)} 文字")
        logger.info(f"Twitterカウント: {twitter_counted_length} 文字（合計280文字以内: {'✓' if twitter_counted_length <= 280 else '✗'}）")
        logger.info(f"実際の文字数: {actual_length} 文字")
        
        # mdファイルに書き込む（強制的に書き込む）
        if save_to_md:
            logger.info(f"\n{'='*60}")
            logger.info("mdファイルに書き込み中...")
            logger.info(f"{'='*60}")
            
            # アカウント名を決定
            if twitter_handle == Config.TWITTER_365BOT_HANDLE:
                account_name = '365botgary'
            elif twitter_handle == Config.TWITTER_PURSAHS_HANDLE:
                account_name = 'pursahsgospel'
            else:
                account_name = twitter_handle.lower()
            
            # 確率1.0（100%）で書き込む
            saved = TwitterPoster.save_post_to_markdown(
                tweet_text=tweet_text,
                link=page_content.get('link', page_url),
                title=page_content.get('title', 'タイトルなし'),
                account_name=account_name,
                probability=1.0  # 100%の確率で書き込む
            )
            
            if saved:
                logger.info(f"✓ mdファイルに書き込みました")
            else:
                logger.warning("mdファイルへの書き込みに失敗しました")
        
        logger.info("\n" + "=" * 60)
        logger.info("確認完了")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='投稿文を確認するスクリプト')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both', help='確認するアカウント')
    parser.add_argument('--no-save', action='store_true', help='mdファイルに保存しない')
    
    args = parser.parse_args()
    
    save_to_md = not args.no_save
    
    if args.account in ['365bot', 'both']:
        logger.info("\n" + "="*60)
        logger.info("[365botGary]")
        logger.info("="*60)
        check_post_text(Config.BLOG_365BOT_URL, Config.TWITTER_365BOT_HANDLE, save_to_md=save_to_md)
    
    if args.account in ['pursahs', 'both']:
        logger.info("\n" + "="*60)
        logger.info("[pursahsgospel]")
        logger.info("="*60)
        check_post_text(Config.BLOG_PURSAHS_URL, Config.TWITTER_PURSAHS_HANDLE, save_to_md=save_to_md)


if __name__ == "__main__":
    main()

