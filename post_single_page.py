"""
個別ページをX（Twitter）に投稿するスクリプト
指定されたURLのページを取得して投稿
"""
import logging
import sys
from datetime import datetime
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def post_single_page(page_url: str, twitter_handle: str, credentials: dict):
    """
    個別ページを取得してTwitterに投稿
    
    Args:
        page_url: 投稿するページのURL
        twitter_handle: Twitterハンドル（ログ用）
        credentials: Twitter API認証情報
    
    Returns:
        投稿に成功した場合True
    """
    try:
        logger.info(f"処理開始: {page_url} -> @{twitter_handle}")
        
        # ページコンテンツを取得
        logger.info("ページコンテンツを取得中...")
        fetcher = BlogFetcher(page_url)
        post_data = fetcher.fetch_latest_post()
        
        if not post_data:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url}")
            return False
        
        logger.info(f"取得した投稿: {post_data.get('title', 'タイトルなし')}")
        logger.info(f"リンク: {post_data.get('link', page_url)}")
        
        # Twitterに投稿
        logger.info("Twitterに投稿中...")
        poster = TwitterPoster(credentials)
        
        # ツイートテキストをフォーマット
        tweet_text = poster.format_blog_post(
            title=post_data.get('title', ''),
            content=post_data.get('content', ''),
            link=post_data.get('link', page_url)
        )
        
        # リンク付きツイートを投稿
        result = poster.post_tweet_with_link(
            text=tweet_text,
            link=post_data.get('link', page_url)
        
        if result and result.get('success'):
            logger.info(f"✓ 投稿成功: @{twitter_handle}")
            logger.info(f"  ツイートID: {result.get('id')}")
            logger.info(f"  URL: https://twitter.com/{twitter_handle}/status/{result.get('id')}")
            return True
        else:
            logger.error(f"投稿失敗: @{twitter_handle}")
            return False
            
    except Exception as e:
        logger.error(f"処理エラー ({page_url}): {e}", exc_info=True)
        return False


def main():
    """メイン関数"""
    logger.info("=" * 60)
    logger.info("個別ページ→Twitter自動投稿ボット開始")
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    success_count = 0
    total_count = 0
    
    # 365botGary の処理
    logger.info("\n[1/2] 365botGary の処理を開始")
    try:
        credentials_365bot = Config.get_twitter_credentials_365bot()
        
        # 認証情報の確認
        if not credentials_365bot.get('api_key') or not credentials_365bot.get('access_token'):
            logger.error("Twitter API認証情報が設定されていません（365botGary）")
            logger.error(".envファイルにTWITTER_API_KEY、TWITTER_ACCESS_TOKENなどを設定してください")
        else:
            # 個別ページのURLを指定
            page_url = "http://notesofacim.blog.fc2.com/blog-entry-44.html"
            total_count += 1
            success = post_single_page(
                page_url=page_url,
                twitter_handle=Config.TWITTER_365BOT_HANDLE,
                credentials=credentials_365bot
            )
            if success:
                success_count += 1
    except Exception as e:
        logger.error(f"365botGary処理エラー: {e}", exc_info=True)
    
    # pursahsgospel の処理
    logger.info("\n[2/2] pursahsgospel の処理を開始")
    try:
        credentials_pursahs = Config.get_twitter_credentials_pursahs()
        
        # 認証情報の確認
        if not credentials_pursahs.get('api_key') or not credentials_pursahs.get('access_token'):
            logger.error("Twitter API認証情報が設定されていません（pursahsgospel）")
            logger.error(".envファイルにTWITTER_API_KEY、TWITTER_ACCESS_TOKENなどを設定してください")
        else:
            # 個別ページのURLを指定
            page_url = "https://ameblo.jp/pursahs-gospel/entry-11577213279.html"
            total_count += 1
            success = post_single_page(
                page_url=page_url,
                twitter_handle=Config.TWITTER_PURSAHS_HANDLE,
                credentials=credentials_pursahs
            )
            if success:
                success_count += 1
    except Exception as e:
        logger.error(f"pursahsgospel処理エラー: {e}", exc_info=True)
    
    # 結果サマリー
    logger.info("\n" + "=" * 60)
    logger.info("処理完了")
    logger.info(f"成功: {success_count}/{total_count}")
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
