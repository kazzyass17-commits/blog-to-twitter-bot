"""
メインアプリケーション
データベースから未投稿の投稿をランダムに選択してX（Twitter）に投稿
"""
import logging
import sys
from datetime import datetime
from database import PostDatabase
from twitter_poster import TwitterPoster
from pdf_generator import PDFGenerator
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


def post_random_blog_post(blog_url: str, twitter_handle: str, credentials: dict, generate_pdf: bool = False):
    """
    データベースからランダムに未投稿の投稿を選択してTwitterに投稿
    
    Args:
        blog_url: ブログのURL
        twitter_handle: Twitterハンドル（ログ用）
        credentials: Twitter API認証情報
        generate_pdf: PDFを生成するかどうか
    
    Returns:
        投稿に成功した場合True
    """
    try:
        logger.info(f"処理開始: {blog_url} -> @{twitter_handle}")
        
        db = PostDatabase()
        
        # 未投稿の投稿をランダムに1件取得
        logger.info("未投稿の投稿を検索中...")
        post_data = db.get_random_unposted_post(blog_url, twitter_handle)
        
        if not post_data:
            logger.warning(f"未投稿の投稿がありません: {blog_url} -> @{twitter_handle}")
            return False
        
        logger.info(f"選択した投稿: {post_data.get('title', 'タイトルなし')}")
        logger.info(f"投稿ID: {post_data['id']}, リンク: {post_data.get('link', '')}")
        
        # PDF生成（オプション）
        if generate_pdf:
            try:
                logger.info("PDFを生成中...")
                pdf_gen = PDFGenerator()
                pdf_path = pdf_gen.generate_pdf({
                    'title': post_data.get('title', ''),
                    'content': post_data.get('content', ''),
                    'link': post_data.get('link', ''),
                    'published_date': post_data.get('published_date', ''),
                    'author': post_data.get('author', ''),
                })
                if pdf_path:
                    logger.info(f"PDF生成成功: {pdf_path}")
            except Exception as e:
                logger.error(f"PDF生成エラー: {e}")
        
        # Twitterに投稿
        logger.info("Twitterに投稿中...")
        poster = TwitterPoster(credentials)
        
        # ツイートテキストをフォーマット
        tweet_text = poster.format_blog_post(
            title=post_data.get('title', ''),
            content=post_data.get('content', ''),
            link=post_data.get('link', blog_url)
        )
        
        # リンク付きツイートを投稿
        result = poster.post_tweet_with_link(
            text=tweet_text,
            link=post_data.get('link', blog_url)
        )
        
        if result and result.get('success'):
            # 投稿履歴を記録
            cycle_number = db.get_current_cycle_number(blog_url, twitter_handle)
            db.record_post(
                post_id=post_data['id'],
                blog_url=blog_url,
                twitter_handle=twitter_handle,
                cycle_number=cycle_number,
                tweet_id=str(result.get('id', ''))
            )
            
            logger.info(f"投稿成功: @{twitter_handle}")
            logger.info(f"ツイートID: {result.get('id')}")
            logger.info(f"サイクル番号: {cycle_number}")
            
            # サイクルの完了をチェック
            if db.check_cycle_complete(blog_url, twitter_handle, cycle_number):
                logger.info(f"サイクル#{cycle_number}が完了しました。次のサイクルが開始されます。")
            
            return True
        else:
            logger.error(f"投稿失敗: @{twitter_handle}")
            return False
            
    except Exception as e:
        logger.error(f"処理エラー ({blog_url}): {e}", exc_info=True)
        return False


def main():
    """メイン関数"""
    logger.info("=" * 60)
    logger.info("ブログ→Twitter自動投稿ボット開始")
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
            total_count += 1
            success = post_random_blog_post(
                blog_url=Config.BLOG_365BOT_URL,
                twitter_handle=Config.TWITTER_365BOT_HANDLE,
                credentials=credentials_365bot,
                generate_pdf=False  # 毎回PDFを生成しない
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
            total_count += 1
            success = post_random_blog_post(
                blog_url=Config.BLOG_PURSAHS_URL,
                twitter_handle=Config.TWITTER_PURSAHS_HANDLE,
                credentials=credentials_pursahs,
                generate_pdf=False  # 毎回PDFを生成しない
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
