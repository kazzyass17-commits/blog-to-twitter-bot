"""
ブログからランダムに1つ投稿を選び、両方のアカウントで投稿を実施するスクリプト
"""
import logging
import sys
import os
import sqlite3
import time
import json
from datetime import datetime, timedelta
from database import PostDatabase
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
from config import Config
from rate_limit_checker import check_and_wait_for_account, record_rate_limit_reason, clear_rate_limit_state
import tweepy

# 失敗した投稿を保存するJSONファイル
FAILED_POSTS_FILE = "failed_posts.json"
BLOCKED_POSTS_FILE = "blocked_posts.json"


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


def load_blocked_posts():
    """403でブロック候補に入れた投稿を読み込む"""
    if os.path.exists(BLOCKED_POSTS_FILE):
        try:
            with open(BLOCKED_POSTS_FILE, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_blocked_posts(blocked_posts):
    """ブロック候補を保存"""
    try:
        with open(BLOCKED_POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(blocked_posts, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"ブロックリストの保存に失敗: {e}")


def add_blocked_post(post_data, account_key):
    """403が発生した投稿をブロックリストに追加"""
    blocked = load_blocked_posts()
    for b in blocked:
        if b.get('post_id') == post_data.get('id') and b.get('account_key') == account_key:
            return
    blocked.append({
        'post_id': post_data.get('id'),
        'title': post_data.get('title', ''),
        'link': post_data.get('link', ''),
        'account_key': account_key,
        'blocked_at': datetime.now().isoformat()
    })
    save_blocked_posts(blocked)
    logger.info(f"403のためブロックリストに追加: post_id={post_data.get('id')}, account={account_key}")


def clear_blocked_posts(account_key: str) -> int:
    """指定アカウントのブロックリストを全解除"""
    blocked = load_blocked_posts()
    kept = [b for b in blocked if b.get('account_key') != account_key]
    if len(kept) != len(blocked):
        save_blocked_posts(kept)
    return len(blocked) - len(kept)


def is_blocked(post_data, account_key) -> bool:
    """ブロックリストに含まれているか"""
    blocked = load_blocked_posts()
    return any(b.get('post_id') == post_data.get('id') and b.get('account_key') == account_key for b in blocked)


def save_failed_posts(failed_posts):
    """失敗した投稿を保存する"""
    try:
        with open(FAILED_POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(failed_posts, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"失敗投稿の保存に失敗: {e}")


def add_failed_post(post_data, page_content, blog_url, twitter_handle, account_key, error_info: dict = None, tweet_preview: str = None):
    """失敗した投稿を追加する"""
    failed_posts = load_failed_posts()
    
    # 同じ投稿が既に存在するかチェック
    for fp in failed_posts:
        if fp['post_id'] == post_data['id'] and fp['account_key'] == account_key:
            # リトライ回数を増やす
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
            save_failed_posts(failed_posts)
            logger.info(f"失敗投稿を更新: post_id={post_data['id']}, account={account_key}, retry_count={fp['retry_count']}")
            return
    
    # 新規追加
    failed_post = {
        'post_id': post_data['id'],
        'title': post_data.get('title', ''),
        'link': page_content.get('link', post_data.get('link', '')),
        'blog_url': blog_url,
        'twitter_handle': twitter_handle,
        'account_key': account_key,
        'retry_count': 0,
        'first_failed': datetime.now().isoformat(),
        'last_failed': datetime.now().isoformat(),
        'tweet_preview': (tweet_preview[:200] if tweet_preview else None),
        'last_error': (None if not error_info else {
            'status': error_info.get('status'),
            'reason': error_info.get('reason'),
            'transaction_id': error_info.get('transaction_id'),
            'headers': error_info.get('headers'),
            'error_message': error_info.get('error_message'),
        }),
    }
    failed_posts.append(failed_post)
    save_failed_posts(failed_posts)
    logger.info(f"失敗投稿を記録: post_id={post_data['id']}, account={account_key}")


def remove_failed_post(post_id, account_key):
    """成功した投稿を失敗リストから削除する"""
    failed_posts = load_failed_posts()
    failed_posts = [fp for fp in failed_posts if not (fp['post_id'] == post_id and fp['account_key'] == account_key)]
    save_failed_posts(failed_posts)


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
) -> (bool, object):
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
            return False, None
        
        poster = TwitterPoster(credentials, account_key=account_key, account_name=twitter_handle)
        
        # ツイートテキストをフォーマット
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=page_content.get('link', post_data.get('link', ''))
        )
        
        # リンク付きツイートを投稿（1回目）
        result = poster.post_tweet_with_link(
            text=tweet_text,
            link=page_content.get('link', post_data.get('link', ''))
        )

        def on_success(res):
            clear_rate_limit_state(account_key)
            remove_failed_post(post_data['id'], account_key)
            db = PostDatabase()
            cycle_number = db.get_current_cycle_number(blog_url, twitter_handle)
            db.record_post(
                post_id=post_data['id'],
                blog_url=blog_url,
                twitter_handle=twitter_handle,
                cycle_number=cycle_number,
                tweet_id=str(res.get('id', ''))
            )
            logger.info(f"✓ 投稿成功: @{twitter_handle}")
            logger.info(f"  ツイートID: {res.get('id')}")
            logger.info(f"  サイクル番号: {cycle_number}")
            headers_s = res.get("headers") or {}
            if headers_s:
                remain_app = headers_s.get("x-app-limit-24hour-remaining")
                remain_user = headers_s.get("x-user-limit-24hour-remaining")
                logger.info(f"  24h残数 app/user: {remain_app}/{remain_user} (headers={headers_s})")
            if db.check_cycle_complete(blog_url, twitter_handle, cycle_number):
                logger.info(f"  サイクル#{cycle_number}が完了しました。次のサイクルが開始されます。")
            return True, None

        def record_failure(res, preview_text):
            status_code = res.get("status") if isinstance(res, dict) else None
            if status_code == 403:
                add_blocked_post(post_data, account_key)
            add_failed_post(
                post_data=post_data,
                page_content=page_content,
                blog_url=blog_url,
                twitter_handle=twitter_handle,
                account_key=account_key,
                error_info=res if isinstance(res, dict) else None,
                tweet_preview=preview_text
            )
            return False, status_code

        def trim_first_word(text: str) -> str:
            # 先頭に「…」がなければ付与（既にあれば増やさない）
            has_leading_ellipsis = text.startswith("…")
            body = text[1:] if has_leading_ellipsis else text
            import re
            # 語録番号が先頭にある場合は保持し、その後の先頭1語を削る
            goroku_match = re.match(r"\s*(語録(?:\s*\([^)]+\)\s*)?[０-９0-9]+)\s*(.*)", body)
            if goroku_match:
                goroku = goroku_match.group(1)
                rest = goroku_match.group(2).lstrip()
                m2 = re.match(r"\s*([^\s]+)\s+(.*)", rest)
                if m2:
                    trimmed_rest = m2.group(2)
                else:
                    trimmed_rest = rest[2:] if len(rest) > 2 else ""
                trimmed_rest = trimmed_rest.lstrip()
                if trimmed_rest:
                    if not trimmed_rest.startswith("…"):
                        trimmed_rest = f"…{trimmed_rest}"
                    return f"{goroku}\n{trimmed_rest}"
                return goroku
            m = re.match(r"\s*([^\s]+)\s+(.*)", body)
            if m:
                trimmed = m.group(2)
            else:
                trimmed = body[2:] if len(body) > 2 else ""
            trimmed = trimmed.lstrip()
            return ("…" if not has_leading_ellipsis else "…") + trimmed if trimmed else ("…" if not has_leading_ellipsis else body)

        if result and result.get('success'):
            return on_success(result)
        else:
            status_code = result.get("status") if isinstance(result, dict) else None
            if status_code == 403:
                # 差し替えず、同一投稿で文頭を1語削って1回だけ再試行
                trimmed_text = trim_first_word(tweet_text)
                logger.warning("403のため、同一投稿で文頭1語削って再試行します (pursahs)")
                retry_res = poster.post_tweet_with_link(
                    text=trimmed_text,
                    link=page_content.get('link', post_data.get('link', ''))
                )
                if retry_res and retry_res.get("success"):
                    unblocked = clear_blocked_posts(account_key)
                    if unblocked:
                        logger.info(f"文頭削除で投稿成功のため、ブロックリストを解除: {unblocked}件 (account={account_key})")
                    return on_success(retry_res)
                else:
                    return record_failure(retry_res, trimmed_text)
            else:
                logger.error(f"✗ 投稿失敗: @{twitter_handle}")
                return record_failure(result, tweet_text)
            
    except Exception as e:
        logger.error(f"処理エラー (@{twitter_handle}): {e}", exc_info=True)
        return False, None


def main(only_account: str = None):
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
        
        def pick_post(blog_url, handle, account_key, max_try=10):
            for _ in range(max_try):
                cand = db.get_random_unposted_post(blog_url, handle)
                if not cand:
                    return None
                if is_blocked(cand, account_key):
                    logger.warning(f"ブロック対象のためスキップ: post_id={cand.get('id')}, account={account_key}")
                    continue
                return cand
            return None

        def refresh_posts_for_blog(blog_url: str, blog_name: str, max_posts: int = 500) -> int:
            """投稿リストを再作成（ブログから全投稿を再取得してDBへ追加）"""
            logger.info(f"\n{'='*60}")
            logger.info(f"{blog_name} の投稿リストを再作成: {blog_url}")
            logger.info(f"{'='*60}")
            fetcher = BlogFetcher(blog_url)
            posts = fetcher.fetch_all_posts(max_posts=max_posts)
            if not posts:
                logger.warning(f"投稿リストの再作成に失敗: {blog_url}")
                return 0
            saved_count = 0
            for post in posts:
                post_id = db.add_post(blog_url, post)
                if post_id:
                    saved_count += 1
            logger.info(f"{blog_name}: 追加 {saved_count} 件 / 取得 {len(posts)} 件")
            return saved_count

        # pursahsgospelのみ実行
        if only_account == "pursahs":
            logger.info("\n[pursahsgospelのみ] 投稿を検索中...")
            post_data_pursahs = pick_post(blog_url_pursahs, twitter_handle_pursahs, 'pursahs')
            if not post_data_pursahs:
                logger.warning(f"未投稿のURLがありません: {blog_url_pursahs} -> @{twitter_handle_pursahs}")
                refresh_posts_for_blog(blog_url_pursahs, "pursahsgospel (Ameba)")
                post_data_pursahs = pick_post(blog_url_pursahs, twitter_handle_pursahs, 'pursahs')
                if not post_data_pursahs:
                    logger.warning(f"再作成後も未投稿のURLがありません: {blog_url_pursahs} -> @{twitter_handle_pursahs}")
                    return False
            page_url_pursahs = post_data_pursahs.get('link', '')
            if not page_url_pursahs:
                logger.warning(f"URLが取得できませんでした: post_id={post_data_pursahs.get('id')}")
                return False
            logger.info(f"選択したURL (pursahsgospel): {page_url_pursahs}")
            logger.info(f"投稿ID: {post_data_pursahs['id']}")

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
                if page_content_pursahs.get('title'):
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute('UPDATE posts SET title = ?, updated_at = ? WHERE id = ?',
                                 (page_content_pursahs.get('title'), datetime.now().isoformat(), post_data_pursahs['id']))
                    conn.commit()
                    conn.close()

            logger.info(f"取得した投稿 (pursahsgospel): {page_content_pursahs.get('title', 'タイトルなし')}")
            success_pursahs, _ = post_blog_post_to_account(
                post_data=post_data_pursahs,
                page_content=page_content_pursahs,
                blog_url=blog_url_pursahs,
                twitter_handle=twitter_handle_pursahs,
                credentials=credentials_pursahs,
                account_key='pursahs'
            )
            logger.info("\n" + "=" * 60)
            logger.info("処理完了（pursahsgospelのみ）")
            logger.info(f"pursahsgospel: {'成功' if success_pursahs else '失敗'}")
            logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            return success_pursahs

        # 365botGary用の投稿をランダムに1件取得（ブロック済みを除外）
        logger.info(f"\n365botGary用の投稿を検索中...")
        post_data_365bot = pick_post(blog_url_365bot, twitter_handle_365bot, '365bot')

        if not post_data_365bot:
            logger.warning(f"未投稿のURLがありません: {blog_url_365bot} -> @{twitter_handle_365bot}")
            refresh_posts_for_blog(blog_url_365bot, "365botGary (notesofacim.blog.fc2.com)")
            post_data_365bot = pick_post(blog_url_365bot, twitter_handle_365bot, '365bot')
            if not post_data_365bot:
                logger.warning(f"再作成後も未投稿のURLがありません: {blog_url_365bot} -> @{twitter_handle_365bot}")
                return False
        
        page_url_365bot = post_data_365bot.get('link', '')
        if not page_url_365bot:
            logger.warning(f"URLが取得できませんでした: post_id={post_data_365bot.get('id')}")
            return False
        
        logger.info(f"選択したURL (365botGary): {page_url_365bot}")
        logger.info(f"投稿ID: {post_data_365bot['id']}")
        
        # pursahsgospel用の投稿をランダムに1件取得（ブロック済みを除外）
        logger.info(f"\npursahsgospel用の投稿を検索中...")
        post_data_pursahs = pick_post(blog_url_pursahs, twitter_handle_pursahs, 'pursahs')
        
        skip_pursahs = False
        page_url_pursahs = ""
        if not post_data_pursahs:
            logger.warning(f"未投稿のURLがありません: {blog_url_pursahs} -> @{twitter_handle_pursahs}")
            refresh_posts_for_blog(blog_url_pursahs, "pursahsgospel (Ameba)")
            post_data_pursahs = pick_post(blog_url_pursahs, twitter_handle_pursahs, 'pursahs')
            if not post_data_pursahs:
                logger.warning(f"再作成後も未投稿のURLがありません: {blog_url_pursahs} -> @{twitter_handle_pursahs}")
                skip_pursahs = True
        else:
            page_url_pursahs = post_data_pursahs.get('link', '')
            if not page_url_pursahs:
                logger.warning(f"URLが取得できませんでした: post_id={post_data_pursahs.get('id')}")
                skip_pursahs = True
            else:
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
        page_content_pursahs = None
        if not skip_pursahs:
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
        
        # 両方のアカウントで投稿（順番を pursahs → 365bot に変更）
        if skip_pursahs:
            success_pursahs, status_pursahs = False, None
            logger.warning("pursahsgospelは投稿対象なしのためスキップします")
        else:
            success_pursahs, status_pursahs = post_blog_post_to_account(
                post_data=post_data_pursahs,
                page_content=page_content_pursahs,
                blog_url=blog_url_pursahs,
                twitter_handle=twitter_handle_pursahs,
                credentials=credentials_pursahs,
                account_key='pursahs'
            )

        # pursahs → 365bot の間に60秒待機（連続投稿による一時ブロック防止）
        if success_pursahs:
            logger.info("60秒待機中（連続投稿防止）...")
            time.sleep(60)

        success_365bot, status_365bot = post_blog_post_to_account(
            post_data=post_data_365bot,
            page_content=page_content_365bot,
            blog_url=blog_url_365bot,
            twitter_handle=twitter_handle_365bot,
            credentials=credentials_365bot,
            account_key='365bot'
        )
        
        # 結果サマリー
        logger.info("\n" + "=" * 60)
        logger.info("処理完了（両アカウント）")
        logger.info(f"365botGary: {'成功' if success_365bot else '失敗'}")
        if skip_pursahs:
            logger.info("pursahsgospel: スキップ")
        else:
            logger.info(f"pursahsgospel: {'成功' if success_pursahs else '失敗'}")
        logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        return success_365bot if skip_pursahs else (success_365bot and success_pursahs)
        
    except Exception as e:
        logger.error(f"処理エラー: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    try:
        import argparse
        parser = argparse.ArgumentParser(description='両アカウント or 単独投稿の実行')
        parser.add_argument('--only-pursahs', action='store_true', help='pursahsgospelのみ投稿')
        args = parser.parse_args()
        main("pursahs" if args.only_pursahs else None)
    finally:
        # ログを確実に書き込む
        import logging
        for handler in logging.root.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()










