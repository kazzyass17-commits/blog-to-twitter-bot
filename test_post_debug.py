"""投稿デバッグスクリプト - エラー詳細を確認"""
import logging
import sys
from database import PostDatabase
from twitter_poster import TwitterPoster
from blog_fetcher import BlogFetcher
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_post_with_debug(blog_url: str, twitter_handle: str):
    """投稿をテストしてエラー詳細を確認"""
    logger.info("=" * 60)
    logger.info(f"投稿テスト: {twitter_handle}")
    logger.info("=" * 60)
    
    try:
        db = PostDatabase()
        
        # 未投稿の投稿を取得
        post_data = db.get_random_unposted_post(blog_url, twitter_handle)
        
        if not post_data:
            logger.warning("未投稿の投稿がありません。")
            return False
        
        page_url = post_data.get('link', '')
        if not page_url:
            logger.warning("URLが取得できませんでした")
            return False
        
        logger.info(f"選択された投稿: {post_data.get('title', '')}")
        logger.info(f"URL: {page_url}")
        
        # ページからコンテンツを取得
        logger.info("ページからコンテンツを取得中...")
        fetcher = BlogFetcher(page_url)
        page_content = fetcher.fetch_latest_post()
        
        if not page_content:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url}")
            return False
        
        logger.info(f"取得した投稿: {page_content.get('title', 'タイトルなし')}")
        
        # 認証情報を取得
        if twitter_handle == Config.TWITTER_365BOT_HANDLE:
            credentials = Config.get_twitter_credentials_365bot()
        else:
            credentials = Config.get_twitter_credentials_pursahs()
        
        # Twitter投稿テキストをフォーマット
        poster = TwitterPoster(credentials)
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=page_content.get('link', page_url)
        )
        
        logger.info(f"\n投稿テキスト（最初の200文字）:")
        logger.info(f"{tweet_text[:200]}...")
        logger.info(f"文字数: {len(tweet_text)} 文字")
        
        # 最終的な投稿形式を確認
        final_text = f"{tweet_text}\n{page_content.get('link', page_url)}"
        logger.info(f"\n最終投稿形式（最初の200文字）:")
        logger.info(f"{final_text[:200]}...")
        logger.info(f"最終文字数: {len(final_text)} 文字")
        logger.info(f"280文字以内: {len(final_text) <= 280}")
        
        # 投稿を試行
        logger.info("\n投稿を試行中...")
        result = poster.post_tweet_with_link(
            text=tweet_text,
            link=page_content.get('link', page_url)
        )
        
        if result and result.get('success'):
            logger.info(f"✓ 投稿成功!")
            logger.info(f"  ツイートID: {result.get('id')}")
            logger.info(f"  URL: https://twitter.com/{twitter_handle}/status/{result.get('id')}")
            return True
        else:
            logger.error("✗ 投稿失敗")
            logger.error(f"  結果: {result}")
            return False
            
    except Exception as e:
        logger.error(f"エラー: {type(e).__name__}: {e}", exc_info=True)
        import traceback
        logger.error(f"トレースバック:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='投稿デバッグスクリプト')
    parser.add_argument('--account', choices=['365bot', 'pursahs'], default='365bot', help='投稿するアカウント')
    
    args = parser.parse_args()
    
    if args.account == '365bot':
        test_post_with_debug(Config.BLOG_365BOT_URL, Config.TWITTER_365BOT_HANDLE)
    else:
        test_post_with_debug(Config.BLOG_PURSAHS_URL, Config.TWITTER_PURSAHS_HANDLE)








