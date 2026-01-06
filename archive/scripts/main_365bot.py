"""
365botGary専用メインアプリケーション
データベースから未投稿のURLをランダムに選択して、そのページからコンテンツを取得してX（Twitter）に投稿
"""
import logging
import sys
import sqlite3
from datetime import datetime
from database import PostDatabase
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from pdf_generator import PDFGenerator
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_365bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def post_random_blog_post(blog_url: str, twitter_handle: str, credentials: dict, generate_pdf: bool = False):
    """
    データベースからランダムに未投稿のURLを選択して、そのページからコンテンツを取得してTwitterに投稿
    
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
        
        # 未投稿のURLをランダムに1件取得
        logger.info("未投稿のURLを検索中...")
        post_data = db.get_random_unposted_post(blog_url, twitter_handle)
        
        if not post_data:
            logger.warning(f"未投稿のURLがありません: {blog_url} -> @{twitter_handle}")
            return False
        
        page_url = post_data.get('link', '')
        if not page_url:
            logger.warning(f"URLが取得できませんでした: post_id={post_data.get('id')}")
            return False
        
        logger.info(f"選択したURL: {page_url}")
        logger.info(f"投稿ID: {post_data['id']}")
        
        # ページからコンテンツを取得
        logger.info("ページからコンテンツを取得中...")
        fetcher = BlogFetcher(page_url)
        page_content = fetcher.fetch_latest_post()
        
        if not page_content:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url}")
            # URLのみで投稿を試行
            page_content = {
                'title': post_data.get('title', ''),
                'content': '',
                'link': page_url,
                'published_date': '',
                'author': '',
            }
        else:
            # データベースのタイトルを更新（取得したタイトルで上書き）
            if page_content.get('title'):
                conn = sqlite3.connect(db.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE posts SET title = ?, updated_at = ? WHERE id = ?', 
                             (page_content.get('title'), datetime.now().isoformat(), post_data['id']))
                conn.commit()
                conn.close()
        
        logger.info(f"取得した投稿: {page_content.get('title', 'タイトルなし')}")
        
        # PDF生成（オプション）
        if generate_pdf:
            try:
                logger.info("PDFを生成中...")
                pdf_gen = PDFGenerator()
                pdf_path = pdf_gen.generate_pdf(page_content)
                if pdf_path:
                    logger.info(f"PDF生成成功: {pdf_path}")
            except Exception as e:
                logger.error(f"PDF生成エラー: {e}")
        
        # Twitterに投稿
        logger.info("Twitterに投稿中...")
        poster = TwitterPoster(credentials)
        
        # ツイートテキストをフォーマット
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=page_content.get('link', page_url)
        )
        
        # リンク付きツイートを投稿
        result = poster.post_tweet_with_link(
            text=tweet_text,
            link=page_content.get('link', page_url)
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
    """メイン関数 - 365botGary専用"""
    logger.info("=" * 60)
    logger.info("ブログ→Twitter自動投稿ボット開始 (365botGary)")
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        credentials_365bot = Config.get_twitter_credentials_365bot()
        
        # 認証情報の確認
        if not credentials_365bot.get('api_key') or not credentials_365bot.get('access_token'):
            logger.error("Twitter API認証情報が設定されていません（365botGary）")
            logger.error(".envファイルにTWITTER_365BOT_API_KEY、TWITTER_365BOT_ACCESS_TOKENなどを設定してください")
            return False
        
        success = post_random_blog_post(
            blog_url=Config.BLOG_365BOT_URL,
            twitter_handle=Config.TWITTER_365BOT_HANDLE,
            credentials=credentials_365bot,
            generate_pdf=False  # 毎回PDFを生成しない
        )
        
        # 結果サマリー
        logger.info("\n" + "=" * 60)
        logger.info("処理完了 (365botGary)")
        logger.info(f"成功: {'はい' if success else 'いいえ'}")
        logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        return success
        
    except Exception as e:
        logger.error(f"365botGary処理エラー: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    main()

