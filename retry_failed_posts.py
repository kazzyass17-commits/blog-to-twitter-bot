"""
失敗した投稿をリトライするスクリプト
10時、13時、16時に実行され、1時間前の投稿で失敗したものを再投稿
"""
import logging
import sys
import os
import json
from datetime import datetime
from database import PostDatabase
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config
from rate_limit_checker import check_and_wait_for_account, clear_rate_limit_state

# Windowsでの文字化け対策
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('retry_failed_posts.log', encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)
logger = logging.getLogger(__name__)

# 失敗した投稿を保存するJSONファイル
FAILED_POSTS_FILE = "failed_posts.json"
MAX_RETRY_COUNT = 3  # 最大リトライ回数


def load_failed_posts():
    """失敗した投稿を読み込む"""
    if os.path.exists(FAILED_POSTS_FILE):
        try:
            # WindowsのOut-File等でUTF-8 BOM付きになることがあるため utf-8-sig を使用
            with open(FAILED_POSTS_FILE, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_failed_posts(failed_posts):
    """失敗した投稿を保存する"""
    try:
        with open(FAILED_POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(failed_posts, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"失敗投稿の保存に失敗: {e}")


def remove_failed_post(post_id, account_key):
    """成功した投稿を失敗リストから削除する"""
    failed_posts = load_failed_posts()
    failed_posts = [fp for fp in failed_posts if not (fp['post_id'] == post_id and fp['account_key'] == account_key)]
    save_failed_posts(failed_posts)


def update_retry_count(post_id, account_key, error_info: dict = None, tweet_preview: str = None):
    """リトライ回数を更新する"""
    failed_posts = load_failed_posts()
    for fp in failed_posts:
        if fp['post_id'] == post_id and fp['account_key'] == account_key:
            fp['retry_count'] = fp.get('retry_count', 0) + 1
            fp['last_failed'] = datetime.now().isoformat()
            if tweet_preview is not None:
                fp['tweet_preview'] = tweet_preview[:200]
            if error_info:
                fp['last_error'] = {
                    'status': error_info.get('status'),
                    'reason': error_info.get('reason'),
                    'transaction_id': error_info.get('transaction_id'),
                    'headers': error_info.get('headers'),
                    'error_message': error_info.get('error_message'),
                }
            break
    save_failed_posts(failed_posts)


def retry_post(failed_post):
    """失敗した投稿を再試行"""
    account_key = failed_post['account_key']
    twitter_handle = failed_post['twitter_handle']
    post_id = failed_post['post_id']
    link = failed_post['link']
    blog_url = failed_post['blog_url']
    
    logger.info(f"\n{'='*60}")
    logger.info(f"リトライ開始: @{twitter_handle}")
    logger.info(f"  post_id: {post_id}")
    logger.info(f"  タイトル: {failed_post.get('title', '')[:50]}")
    logger.info(f"  リトライ回数: {failed_post.get('retry_count', 0) + 1}/{MAX_RETRY_COUNT}")
    logger.info(f"{'='*60}")
    
    try:
        # レート制限チェック
        if not check_and_wait_for_account(account_key, twitter_handle, skip_wait=False):
            logger.warning(f"@{twitter_handle}: 待機時間中のため、リトライをスキップします")
            return False
        
        # 認証情報を取得
        if account_key == '365bot':
            credentials = Config.get_twitter_credentials_365bot()
        else:
            credentials = Config.get_twitter_credentials_pursahs()
        
        # ページからコンテンツを再取得
        logger.info(f"コンテンツを再取得中: {link}")
        fetcher = BlogFetcher(link)
        page_content = fetcher.fetch_latest_post()
        
        if not page_content:
            logger.warning(f"コンテンツ取得失敗、DBの情報を使用")
            page_content = {
                'title': failed_post.get('title', ''),
                'content': '',
                'link': link
            }
        
        # ツイート投稿
        poster = TwitterPoster(credentials, account_key=account_key, account_name=twitter_handle)
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=link
        )
        
        result = poster.post_tweet_with_link(text=tweet_text, link=link)
        
        if result and result.get('success'):
            # 投稿成功
            clear_rate_limit_state(account_key)
            remove_failed_post(post_id, account_key)
            
            # 投稿履歴を記録
            db = PostDatabase()
            cycle_number = db.get_current_cycle_number(blog_url, twitter_handle)
            db.record_post(
                post_id=post_id,
                blog_url=blog_url,
                twitter_handle=twitter_handle,
                cycle_number=cycle_number,
                tweet_id=str(result.get('id', ''))
            )
            
            logger.info(f"✓ リトライ成功: @{twitter_handle}")
            logger.info(f"  ツイートID: {result.get('id')}")
            return True
        else:
            # 投稿失敗
            update_retry_count(post_id, account_key, error_info=result if isinstance(result, dict) else None, tweet_preview=tweet_text)
            logger.error(f"✗ リトライ失敗: @{twitter_handle}")
            return False
            
    except Exception as e:
        logger.error(f"リトライエラー (@{twitter_handle}): {e}", exc_info=True)
        update_retry_count(post_id, account_key, error_info={'reason': type(e).__name__, 'error_message': str(e)[:500]})
        return False


def main():
    """メイン関数 - 失敗した投稿をリトライ"""
    logger.info("=" * 60)
    logger.info("失敗投稿リトライ開始")
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    failed_posts = load_failed_posts()
    
    if not failed_posts:
        logger.info("リトライ対象の失敗投稿はありません")
        return True
    
    logger.info(f"リトライ対象: {len(failed_posts)}件")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    # リトライ対象をコピー（ループ中に変更されるため）
    posts_to_retry = list(failed_posts)
    
    for fp in posts_to_retry:
        retry_count = fp.get('retry_count', 0)
        
        # 最大リトライ回数を超えた場合はスキップ（削除はしない：調査用に残す）
        if retry_count >= MAX_RETRY_COUNT:
            logger.warning(f"最大リトライ回数超過、スキップ（調査のため保持）: post_id={fp['post_id']}, account={fp['account_key']}")
            # 印だけ付けて残す
            fp['exhausted'] = True
            fp['exhausted_at'] = datetime.now().isoformat()
            # リスト内を更新
            current = load_failed_posts()
            for i, cur in enumerate(current):
                if cur.get('post_id') == fp.get('post_id') and cur.get('account_key') == fp.get('account_key'):
                    current[i] = fp
                    break
            save_failed_posts(current)
            skip_count += 1
            continue
        
        # リトライ実行
        if retry_post(fp):
            success_count += 1
        else:
            fail_count += 1
        
        # 複数のリトライ間に60秒待機（連続投稿防止）
        remaining = [p for p in load_failed_posts() if p.get('retry_count', 0) < MAX_RETRY_COUNT]
        if remaining:
            logger.info("60秒待機中（連続投稿防止）...")
            import time
            time.sleep(60)
    
    # 結果サマリー
    logger.info("\n" + "=" * 60)
    logger.info("リトライ完了")
    logger.info(f"成功: {success_count}件")
    logger.info(f"失敗: {fail_count}件")
    logger.info(f"スキップ（最大回数超過）: {skip_count}件")
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    return fail_count == 0


if __name__ == "__main__":
    try:
        main()
    finally:
        # ログを確実に書き込む
        for handler in logging.root.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()

