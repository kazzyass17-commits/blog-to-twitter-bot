"""
pursahsgospelの投稿データベースを更新するスクリプト
索引ページから全投稿のURLを取得してデータベースに保存
"""
import logging
import sys
from database import PostDatabase
from index_extractor import IndexExtractor
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('refresh_pursahs_posts.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def refresh_pursahsgospel_posts():
    """
    pursahsgospelのブログから全投稿を取得してデータベースに保存
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"pursahsgospel の投稿を更新: {Config.BLOG_PURSAHS_URL}")
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
    
    logger.info(f"\npursahsgospel: {saved_count}/{len(urls)} 件の投稿をデータベースに保存しました")
    
    # データベース内の投稿数を確認
    all_posts = db.get_all_posts(Config.BLOG_PURSAHS_URL)
    logger.info(f"データベース内の総投稿数: {len(all_posts)} 件")
    
    # 語録投稿数を確認
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cur = conn.cursor()
    goroku_rows = cur.execute("""
        SELECT COUNT(*) FROM posts 
        WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%') 
        AND title LIKE '%語録%' 
        AND title NOT LIKE '%原書%'
    """).fetchone()
    logger.info(f"語録投稿数（原書除外）: {goroku_rows[0]} 件")
    conn.close()


def main():
    """メイン関数"""
    logger.info("=" * 60)
    logger.info("pursahsgospel 投稿データベース更新スクリプト")
    logger.info("=" * 60)
    
    refresh_pursahsgospel_posts()
    
    logger.info("\n" + "=" * 60)
    logger.info("更新完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
