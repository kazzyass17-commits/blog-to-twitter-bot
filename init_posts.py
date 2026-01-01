"""
投稿データベースを初期化して、ブログから全投稿を取得・保存するスクリプト
初回セットアップ時に1回だけ実行
"""
import logging
import sys
from database import PostDatabase
from blog_fetcher import BlogFetcher
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('init_posts.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def init_posts_for_blog(blog_url: str, blog_name: str):
    """
    ブログから全投稿を取得してデータベースに保存
    
    Args:
        blog_url: ブログURL
        blog_name: ブログ名（ログ用）
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"{blog_name} の投稿を初期化: {blog_url}")
    logger.info(f"{'='*60}")
    
    db = PostDatabase()
    fetcher = BlogFetcher(blog_url)
    
    # 全投稿を取得
    logger.info("ブログから全投稿を取得中...")
    posts = fetcher.fetch_all_posts(max_posts=500)
    
    if not posts:
        logger.error(f"投稿を取得できませんでした: {blog_url}")
        return
    
    logger.info(f"{len(posts)}件の投稿を取得しました")
    
    # データベースに保存
    saved_count = 0
    for i, post in enumerate(posts, 1):
        post_id = db.add_post(blog_url, post)
        if post_id:
            saved_count += 1
        if i % 10 == 0:
            logger.info(f"進捗: {i}/{len(posts)} 件処理完了")
    
    logger.info(f"\n{blog_name}: {saved_count}/{len(posts)} 件の投稿をデータベースに保存しました")
    
    # データベース内の投稿数を確認
    all_posts = db.get_all_posts(blog_url)
    logger.info(f"データベース内の総投稿数: {len(all_posts)} 件")


def main():
    """メイン関数"""
    logger.info("=" * 60)
    logger.info("投稿データベース初期化スクリプト")
    logger.info("=" * 60)
    
    # 365botGary のブログ
    init_posts_for_blog(
        blog_url=Config.BLOG_365BOT_URL,
        blog_name="365botGary (notesofacim.blog.fc2.com)"
    )
    
    # pursahsgospel のブログ
    init_posts_for_blog(
        blog_url=Config.BLOG_PURSAHS_URL,
        blog_name="pursahsgospel (Ameba)"
    )
    
    logger.info("\n" + "=" * 60)
    logger.info("初期化完了")
    logger.info("=" * 60)
    logger.info("\n次回からは main.py を実行してください。")


if __name__ == "__main__":
    main()


