"""
テスト投稿スクリプト
実際にTwitterに投稿せずに動作確認を行う（ドライラン）
または、実際に投稿する前に確認を行う
"""
import logging
import sys
import os
from datetime import datetime

# archive配下から直接実行しても、プロジェクトルートのモジュールをimportできるようにする
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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


def test_dry_run(blog_url: str, twitter_handle: str):
    """
    ドライラン（実際に投稿しない）
    
    Args:
        blog_url: ブログURL
        twitter_handle: Twitterハンドル
    """
    logger.info("=" * 60)
    logger.info("ドライラン（テストモード）")
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
        
        logger.info(f"\n投稿予定のツイートテキスト:")
        logger.info(f"  {tweet_text}")
        logger.info(f"  文字数: {len(tweet_text)} 文字")
        logger.info(f"\n実際の投稿形式（改行とURLを含む）:")
        actual_tweet = f"{tweet_text}\n{page_content.get('link', page_url)}"
        logger.info(f"  {actual_tweet}")
        logger.info(f"  文字数: {len(tweet_text)} 文字 + 改行(1) + URL(23) = {len(tweet_text) + 24} 文字（合計280文字以内）")
        
        logger.info("\n" + "=" * 60)
        logger.info("ドライラン完了（実際には投稿されていません）")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)


def test_actual_post(blog_url: str, twitter_handle: str, credentials: dict):
    """
    実際にTwitterに投稿（テスト用）
    
    Args:
        blog_url: ブログURL
        twitter_handle: Twitterハンドル
        credentials: Twitter API認証情報
    """
    logger.info("=" * 60)
    logger.info("テスト投稿を実行します")
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
            page_content = {
                'title': post_data.get('title', ''),
                'content': '',
                'link': page_url,
                'published_date': '',
                'author': '',
            }
        
        logger.info(f"取得した投稿: {page_content.get('title', 'タイトルなし')}")
        
        # Twitterに投稿
        # アカウントキーとアカウント名を設定
        if twitter_handle == Config.TWITTER_365BOT_HANDLE:
            account_key = '365bot'
            account_name = '365botGary'
        else:
            account_key = 'pursahs'
            account_name = 'pursahsgospel'
        poster = TwitterPoster(credentials, account_key=account_key, account_name=account_name)
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=page_content.get('link', page_url)
        )
        
        logger.info(f"投稿テキスト: {tweet_text}")
        logger.info(f"文字数: {len(tweet_text)} 文字（リンク含む: {len(tweet_text) + 24} 文字）")
        
        # データベースのURLを優先（BlogFetcherが返すlinkは異なる可能性があるため）
        result = poster.post_tweet_with_link(
            text=tweet_text,
            link=page_url  # データベースに保存されているURLを使用
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
            
            logger.info(f"✓ 投稿成功!")
            logger.info(f"  ツイートID: {result.get('id')}")
            logger.info(f"  サイクル番号: {cycle_number}")
            logger.info(f"  URL: https://twitter.com/{twitter_handle}/status/{result.get('id')}")
            return True
        else:
            logger.error("投稿失敗")
            return False
            
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)
        return False


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='テスト投稿スクリプト')
    parser.add_argument('--dry-run', action='store_true', help='ドライラン（実際に投稿しない）')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both', help='投稿するアカウント')
    parser.add_argument('--no-confirm', action='store_true', help='確認プロンプトをスキップして自動実行')
    parser.add_argument('--post-id', type=int, default=None, help='指定したpost_idを投稿（失敗投稿の再投稿用）')
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("ドライランモードで実行します（実際には投稿されません）")
        
        if args.account in ['365bot', 'both']:
            logger.info("\n[365botGary]")
            test_dry_run(Config.BLOG_365BOT_URL, Config.TWITTER_365BOT_HANDLE)
        
        if args.account in ['pursahs', 'both']:
            logger.info("\n[pursahsgospel]")
            test_dry_run(Config.BLOG_PURSAHS_URL, Config.TWITTER_PURSAHS_HANDLE)
    else:
        logger.warning("実際にTwitterに投稿します。")
        # GitHub Actionsなどの非対話環境では自動的に続行
        import os
        if args.no_confirm or os.getenv('GITHUB_ACTIONS'):
            if args.no_confirm:
                logger.info("--no-confirmオプションが指定されました。自動的に続行します。")
            else:
                logger.info("GitHub Actions環境で実行中。自動的に続行します。")
            auto_continue = True
        else:
            print("続行しますか？ (y/N): ", end='', flush=True)
            try:
                response = input().strip().lower()
                auto_continue = (response == 'y')
            except (KeyboardInterrupt, EOFError):
                logger.info("\nキャンセルしました。")
                return
        
        if not auto_continue:
            logger.info("キャンセルしました。")
            return
        
        def post_specific_id(post_id: int, blog_url: str, twitter_handle: str, credentials: dict) -> bool:
            """指定post_idを投稿（失敗投稿の再投稿用）"""
            import sqlite3
            logger.info("=" * 60)
            logger.info(f"指定post_idで投稿します: post_id={post_id} @{twitter_handle}")
            logger.info("=" * 60)
            
            db = PostDatabase()
            conn = sqlite3.connect(db.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, title, link FROM posts WHERE id = ?", (post_id,))
            row = cur.fetchone()
            conn.close()
            
            if not row:
                logger.error(f"post_idが見つかりません: {post_id}")
                return False
            
            post_data = {"id": row[0], "title": row[1], "link": row[2]}
            page_url = post_data.get("link", "")
            if not page_url:
                logger.error("URLが取得できませんでした")
                return False
            
            logger.info(f"タイトル（DB）: {post_data.get('title', '')}")
            logger.info(f"URL: {page_url}")
            
            fetcher = BlogFetcher(page_url)
            page_content = fetcher.fetch_latest_post() or {
                'title': post_data.get('title', ''),
                'content': '',
                'link': page_url,
                'published_date': '',
                'author': '',
            }
            
            # アカウントキーとアカウント名を設定（診断情報を正しく残す）
            if twitter_handle == Config.TWITTER_365BOT_HANDLE:
                account_key = '365bot'
                account_name = '365botGary'
            else:
                account_key = 'pursahs'
                account_name = 'pursahsgospel'
            
            poster = TwitterPoster(credentials, account_key=account_key, account_name=account_name)
            tweet_text = poster.format_blog_post(
                title=page_content.get('title', ''),
                content=page_content.get('content', ''),
                link=page_content.get('link', page_url)
            )
            
            logger.info(f"投稿テキスト: {tweet_text}")
            result = poster.post_tweet_with_link(text=tweet_text, link=page_url)
            
            if result and result.get('success'):
                cycle_number = db.get_current_cycle_number(blog_url, twitter_handle)
                db.record_post(
                    post_id=post_data['id'],
                    blog_url=blog_url,
                    twitter_handle=twitter_handle,
                    cycle_number=cycle_number,
                    tweet_id=str(result.get('id', ''))
                )
                logger.info(f"✓ 投稿成功!")
                logger.info(f"  ツイートID: {result.get('id')}")
                logger.info(f"  URL: https://twitter.com/{twitter_handle}/status/{result.get('id')}")
                return True
            
            logger.error("投稿失敗")
            logger.error(f"  結果: {result}")
            return False
        
        success_count = 0
        
        if args.account in ['365bot', 'both']:
            logger.info("\n[365botGary]")
            credentials = Config.get_twitter_credentials_365bot()
            if credentials.get('api_key') and credentials.get('access_token'):
                ok = post_specific_id(args.post_id, Config.BLOG_365BOT_URL, Config.TWITTER_365BOT_HANDLE, credentials) if args.post_id else test_actual_post(Config.BLOG_365BOT_URL, Config.TWITTER_365BOT_HANDLE, credentials)
                if ok:
                    success_count += 1
            else:
                logger.error("認証情報が設定されていません")
        
        if args.account in ['pursahs', 'both']:
            logger.info("\n[pursahsgospel]")
            credentials = Config.get_twitter_credentials_pursahs()
            if credentials.get('api_key') and credentials.get('access_token'):
                ok = post_specific_id(args.post_id, Config.BLOG_PURSAHS_URL, Config.TWITTER_PURSAHS_HANDLE, credentials) if args.post_id else test_actual_post(Config.BLOG_PURSAHS_URL, Config.TWITTER_PURSAHS_HANDLE, credentials)
                if ok:
                    success_count += 1
            else:
                logger.error("認証情報が設定されていません")
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"テスト投稿完了: {success_count} 件成功")
        logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    main()


