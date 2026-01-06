"""
索引ページから個別ページのURLを取得してデータベースに保存するスクリプト
初回セットアップ時に1回だけ実行
"""
import logging
import sys
from database import PostDatabase
from index_extractor import IndexExtractor
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


def init_365botgary_from_index():
    """365botgaryの索引ページからURLを取得してデータベースに保存"""
    logger.info(f"\n{'='*60}")
    logger.info("365botgary のURLを索引ページから取得")
    logger.info(f"{'='*60}")
    
    db = PostDatabase()
    extractor = IndexExtractor()
    
    # 索引ページからURLを抽出
    logger.info("索引ページから個別ページのURLを抽出中...")
    urls = extractor.extract_365botgary_urls()
    
    if not urls:
        logger.error("URLを取得できませんでした")
        return
    
    logger.info(f"{len(urls)}件のURLを抽出しました")
    
    # データベースに保存
    saved_count = 0
    for i, url_data in enumerate(urls, 1):
        # URLのみを保存（タイトルやコンテンツは後で取得）
        post_id = db.add_post(Config.BLOG_365BOT_URL, {
            'title': url_data.get('title', ''),
            'content': '',
            'link': url_data.get('link', ''),
            'published_date': '',
            'author': '',
        })
        if post_id:
            saved_count += 1
        if i % 50 == 0:
            logger.info(f"進捗: {i}/{len(urls)} 件処理完了")
    
    logger.info(f"\n365botgary: {saved_count}/{len(urls)} 件のURLをデータベースに保存しました")
    
    # データベース内のURL数を確認
    all_posts = db.get_all_posts(Config.BLOG_365BOT_URL)
    logger.info(f"データベース内の総URL数: {len(all_posts)} 件")


def init_pursahsgospel_from_index():
    """pursahsgospelの索引ページからURLを取得してデータベースに保存"""
    logger.info(f"\n{'='*60}")
    logger.info("pursahsgospel のURLを索引ページから取得")
    logger.info(f"{'='*60}")
    
    db = PostDatabase()
    extractor = IndexExtractor()
    
    # 索引ページからURLを抽出
    logger.info("索引ページから個別ページのURLを抽出中...")
    urls = extractor.extract_pursahsgospel_urls()
    
    if not urls:
        logger.error("URLを取得できませんでした")
        return
    
    logger.info(f"{len(urls)}件のURLを抽出しました")
    
    # データベースに保存
    saved_count = 0
    for i, url_data in enumerate(urls, 1):
        post_id = db.add_post(Config.BLOG_PURSAHS_URL, {
            'title': url_data.get('title', ''),
            'content': '',
            'link': url_data.get('link', ''),
            'published_date': '',
            'author': '',
        })
        if post_id:
            saved_count += 1
        if i % 20 == 0:
            logger.info(f"進捗: {i}/{len(urls)} 件処理完了")
    
    logger.info(f"\npursahsgospel: {saved_count}/{len(urls)} 件のURLをデータベースに保存しました")
    
    # データベース内のURL数を確認
    all_posts = db.get_all_posts(Config.BLOG_PURSAHS_URL)
    logger.info(f"データベース内の総URL数: {len(all_posts)} 件")


def main():
    """メイン関数"""
    logger.info("=" * 60)
    logger.info("索引ページからURL取得スクリプト")
    logger.info("=" * 60)
    
    # 365botgary の処理
    init_365botgary_from_index()
    
    # pursahsgospel の処理
    init_pursahsgospel_from_index()
    
    logger.info("\n" + "=" * 60)
    logger.info("初期化完了")
    logger.info("=" * 60)
    logger.info("\n次回からは main.py を実行してください。")


if __name__ == "__main__":
    main()

