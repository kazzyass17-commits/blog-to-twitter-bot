"""
ブログからランダムに1つ投稿を選び、両方のアカウントで投稿を実施するスクリプト
"""
import logging
import sys
import os
import sqlite3
import time
from datetime import datetime, timedelta
from database import PostDatabase
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config
from rate_limit_checker import check_and_wait_for_account, record_rate_limit_reason, clear_rate_limit_state
import tweepy

# Windowsでの文字化け対策（環境変数を設定）
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('post_both_accounts.log', encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # 既存のログ設定を上書き
)
logger = logging.getLogger(__name__)

# ログハンドラーを取得してflushを有効化
for handler in logger.handlers:
    if isinstance(handler, logging.FileHandler):
        handler.flush()


def post_blog_post_to_account(
    post_data: dict,
    page_content: dict,
    blog_url: str,
    twitter_handle: str,
    credentials: dict,
    account_key: str
) -> bool:
    """
    ブログ投稿を指定されたアカウントに投稿
    
    Args:
        post_data: データベースから取得した投稿データ
        page_content: ブログから取得したコンテンツ
        blog_url: ブログURL
        twitter_handle: Twitterハンドル
        credentials: Twitter API認証情報
        account_key: アカウントキー（'365bot' または 'pursahs'）
    
    Returns:
        投稿に成功した場合True
    """
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"@{twitter_handle} への投稿開始")
        logger.info(f"{'='*60}")
        
        # 待機時間をチェック
        if not check_and_wait_for_account(account_key, twitter_handle, skip_wait=False):
            logger.warning(f"@{twitter_handle}: 待機時間中のため、処理をスキップします")
            return False
        
        poster = TwitterPoster(credentials)
        
        # ツイートテキストをフォーマット
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=page_content.get('link', post_data.get('link', ''))
        )
        
        # リンク付きツイートを投稿
        result = poster.post_tweet_with_link(
            text=tweet_text,
            link=page_content.get('link', post_data.get('link', ''))
        )
        
        if result and result.get('success'):
            # 投稿成功時はレート制限状態をクリア
            clear_rate_limit_state(account_key)
            
            # 投稿履歴を記録
            db = PostDatabase()
            cycle_number = db.get_current_cycle_number(blog_url, twitter_handle)
            db.record_post(
                post_id=post_data['id'],
                blog_url=blog_url,
                twitter_handle=twitter_handle,
                cycle_number=cycle_number,
                tweet_id=str(result.get('id', ''))
            )
            
            logger.info(f"✓ 投稿成功: @{twitter_handle}")
            logger.info(f"  ツイートID: {result.get('id')}")
            logger.info(f"  サイクル番号: {cycle_number}")
            
            # サイクルの完了をチェック
            if db.check_cycle_complete(blog_url, twitter_handle, cycle_number):
                logger.info(f"  サイクル#{cycle_number}が完了しました。次のサイクルが開始されます。")
            
            return True
        else:
            logger.error(f"✗ 投稿失敗: @{twitter_handle}")
            return False
            
    except Exception as e:
        logger.error(f"処理エラー (@{twitter_handle}): {e}", exc_info=True)
        return False


def main():
    """メイン関数 - 両方のアカウントで投稿"""
    logger.info("=" * 60)
    logger.info("ブログ→Twitter自動投稿ボット開始（両アカウント）")
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        db = PostDatabase()
        
        # 365botGary用の認証情報とブログURL
        credentials_365bot = Config.get_twitter_credentials_365bot()
        blog_url_365bot = Config.BLOG_365BOT_URL
        twitter_handle_365bot = Config.TWITTER_365BOT_HANDLE
        
        # pursahsgospel用の認証情報とブログURL
        credentials_pursahs = Config.get_twitter_credentials_pursahs()
        blog_url_pursahs = Config.BLOG_PURSAHS_URL
        twitter_handle_pursahs = Config.TWITTER_PURSAHS_HANDLE
        
        # 認証情報の確認
        if not credentials_365bot.get('api_key') or not credentials_365bot.get('access_token'):
            logger.error("Twitter API認証情報が設定されていません（365botGary）")
            return False
        
        if not credentials_pursahs.get('api_key') or not credentials_pursahs.get('access_token'):
            logger.error("Twitter API認証情報が設定されていません（pursahsgospel）")
            return False
        
        # 365botGary用の投稿をランダムに1件取得
        logger.info(f"\n365botGary用の投稿を検索中...")
        post_data_365bot = db.get_random_unposted_post(blog_url_365bot, twitter_handle_365bot)
        
        if not post_data_365bot:
            logger.warning(f"未投稿のURLがありません: {blog_url_365bot} -> @{twitter_handle_365bot}")
            return False
        
        page_url_365bot = post_data_365bot.get('link', '')
        if not page_url_365bot:
            logger.warning(f"URLが取得できませんでした: post_id={post_data_365bot.get('id')}")
            return False
        
        logger.info(f"選択したURL (365botGary): {page_url_365bot}")
        logger.info(f"投稿ID: {post_data_365bot['id']}")
        
        # pursahsgospel用の投稿をランダムに1件取得
        logger.info(f"\npursahsgospel用の投稿を検索中...")
        post_data_pursahs = db.get_random_unposted_post(blog_url_pursahs, twitter_handle_pursahs)
        
        if not post_data_pursahs:
            logger.warning(f"未投稿のURLがありません: {blog_url_pursahs} -> @{twitter_handle_pursahs}")
            return False
        
        page_url_pursahs = post_data_pursahs.get('link', '')
        if not page_url_pursahs:
            logger.warning(f"URLが取得できませんでした: post_id={post_data_pursahs.get('id')}")
            return False
        
        logger.info(f"選択したURL (pursahsgospel): {page_url_pursahs}")
        logger.info(f"投稿ID: {post_data_pursahs['id']}")
        
        # ページからコンテンツを取得（365botGary）
        logger.info(f"\n365botGary用のページからコンテンツを取得中...")
        fetcher_365bot = BlogFetcher(page_url_365bot)
        page_content_365bot = fetcher_365bot.fetch_latest_post()
        
        if not page_content_365bot:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url_365bot}")
            page_content_365bot = {
                'title': post_data_365bot.get('title', ''),
                'content': '',
                'link': page_url_365bot,
                'published_date': '',
                'author': '',
            }
        else:
            # データベースのタイトルを更新
            if page_content_365bot.get('title'):
                conn = sqlite3.connect(db.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE posts SET title = ?, updated_at = ? WHERE id = ?', 
                             (page_content_365bot.get('title'), datetime.now().isoformat(), post_data_365bot['id']))
                conn.commit()
                conn.close()
        
        logger.info(f"取得した投稿 (365botGary): {page_content_365bot.get('title', 'タイトルなし')}")
        
        # ページからコンテンツを取得（pursahsgospel）
        logger.info(f"\npursahsgospel用のページからコンテンツを取得中...")
        fetcher_pursahs = BlogFetcher(page_url_pursahs)
        page_content_pursahs = fetcher_pursahs.fetch_latest_post()
        
        if not page_content_pursahs:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url_pursahs}")
            page_content_pursahs = {
                'title': post_data_pursahs.get('title', ''),
                'content': '',
                'link': page_url_pursahs,
                'published_date': '',
                'author': '',
            }
        else:
            # データベースのタイトルを更新
            if page_content_pursahs.get('title'):
                conn = sqlite3.connect(db.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE posts SET title = ?, updated_at = ? WHERE id = ?', 
                             (page_content_pursahs.get('title'), datetime.now().isoformat(), post_data_pursahs['id']))
                conn.commit()
                conn.close()
        
        logger.info(f"取得した投稿 (pursahsgospel): {page_content_pursahs.get('title', 'タイトルなし')}")
        
        # 両方のアカウントで投稿
        success_365bot = post_blog_post_to_account(
            post_data=post_data_365bot,
            page_content=page_content_365bot,
            blog_url=blog_url_365bot,
            twitter_handle=twitter_handle_365bot,
            credentials=credentials_365bot,
            account_key='365bot'
        )
        
        # 365botとpursahsの投稿間に10秒待機（連続投稿による一時ブロック防止）
        if success_365bot:
            logger.info("10秒待機中（連続投稿防止）...")
            time.sleep(10)
        
        success_pursahs = post_blog_post_to_account(
            post_data=post_data_pursahs,
            page_content=page_content_pursahs,
            blog_url=blog_url_pursahs,
            twitter_handle=twitter_handle_pursahs,
            credentials=credentials_pursahs,
            account_key='pursahs'
        )
        
        # 結果サマリー
        logger.info("\n" + "=" * 60)
        logger.info("処理完了（両アカウント）")
        logger.info(f"365botGary: {'成功' if success_365bot else '失敗'}")
        logger.info(f"pursahsgospel: {'成功' if success_pursahs else '失敗'}")
        logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        return success_365bot and success_pursahs
        
    except Exception as e:
        logger.error(f"処理エラー: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    try:
        main()
    finally:
        # ログを確実に書き込む
        import logging
        for handler in logging.root.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()










