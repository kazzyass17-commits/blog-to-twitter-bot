"""
URL抽出のテストスクリプト
ローカルで実行して、索引ページから正しくURLが抽出されるか確認
"""
import logging
import sys
from index_extractor import IndexExtractor
from database import PostDatabase
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def test_365botgary_extraction():
    """365botGaryのURL抽出をテスト"""
    logger.info("\n" + "="*60)
    logger.info("365botGary URL抽出テスト")
    logger.info("="*60)
    
    extractor = IndexExtractor()
    urls = extractor.extract_365botgary_urls()
    
    logger.info(f"\n抽出されたURL数: {len(urls)}件")
    logger.info(f"期待値: 365件")
    
    if len(urls) < 365:
        logger.warning(f"⚠️ 不足しています: {365 - len(urls)}件")
    elif len(urls) > 365:
        logger.warning(f"⚠️ 多すぎます: {len(urls) - 365}件")
    else:
        logger.info("✓ 正確に365件抽出されました")
    
    # 最初の5件と最後の5件を表示
    if urls:
        logger.info("\n最初の5件:")
        for i, url_data in enumerate(urls[:5], 1):
            logger.info(f"  {i}. {url_data.get('link', '')} - {url_data.get('title', '')[:50]}")
        
        logger.info("\n最後の5件:")
        for i, url_data in enumerate(urls[-5:], len(urls)-4):
            logger.info(f"  {i}. {url_data.get('link', '')} - {url_data.get('title', '')[:50]}")
    
    # URLの重複チェック
    seen = set()
    duplicates = []
    for url_data in urls:
        link = url_data.get('link', '')
        if link in seen:
            duplicates.append(link)
        seen.add(link)
    
    if duplicates:
        logger.warning(f"\n重複URL: {len(duplicates)}件")
        for dup in duplicates[:5]:
            logger.warning(f"  - {dup}")
    else:
        logger.info("\n✓ 重複なし")
    
    return urls


def test_pursahsgospel_extraction():
    """pursahsgospelのURL抽出をテスト"""
    logger.info("\n" + "="*60)
    logger.info("pursahsgospel URL抽出テスト")
    logger.info("="*60)
    
    extractor = IndexExtractor()
    urls = extractor.extract_pursahsgospel_urls()
    
    logger.info(f"\n抽出されたURL数: {len(urls)}件")
    logger.info(f"期待値: 113件（語録1～113）")
    
    if len(urls) < 113:
        logger.warning(f"⚠️ 不足しています: {113 - len(urls)}件")
    elif len(urls) > 113:
        logger.warning(f"⚠️ 多すぎます: {len(urls) - 113}件")
    else:
        logger.info("✓ 正確に113件抽出されました")
    
    # 最初の5件と最後の5件を表示
    if urls:
        logger.info("\n最初の5件:")
        for i, url_data in enumerate(urls[:5], 1):
            logger.info(f"  {i}. {url_data.get('link', '')} - {url_data.get('title', '')[:50]}")
        
        logger.info("\n最後の5件:")
        for i, url_data in enumerate(urls[-5:], len(urls)-4):
            logger.info(f"  {i}. {url_data.get('link', '')} - {url_data.get('title', '')[:50]}")
    
    # URLの重複チェック
    seen = set()
    duplicates = []
    for url_data in urls:
        link = url_data.get('link', '')
        if link in seen:
            duplicates.append(link)
        seen.add(link)
    
    if duplicates:
        logger.warning(f"\n重複URL: {len(duplicates)}件")
        for dup in duplicates[:5]:
            logger.warning(f"  - {dup}")
    else:
        logger.info("\n✓ 重複なし")
    
    return urls


def test_database_save():
    """データベースへの保存をテスト"""
    logger.info("\n" + "="*60)
    logger.info("データベース保存テスト")
    logger.info("="*60)
    
    db = PostDatabase()
    
    # 365botGary
    extractor = IndexExtractor()
    urls_365 = extractor.extract_365botgary_urls()
    
    logger.info(f"\n365botGary: {len(urls_365)}件のURLを抽出")
    
    saved_365 = 0
    for url_data in urls_365:
        post_id = db.add_post(Config.BLOG_365BOT_URL, {
            'title': url_data.get('title', ''),
            'content': '',
            'link': url_data.get('link', ''),
            'published_date': '',
            'author': '',
        })
        if post_id:
            saved_365 += 1
    
    logger.info(f"365botGary: {saved_365}/{len(urls_365)}件をデータベースに保存")
    
    all_posts_365 = db.get_all_posts(Config.BLOG_365BOT_URL)
    logger.info(f"データベース内の365botGary URL数: {len(all_posts_365)}件")
    
    # pursahsgospel
    urls_pursahs = extractor.extract_pursahsgospel_urls()
    
    logger.info(f"\npursahsgospel: {len(urls_pursahs)}件のURLを抽出")
    
    saved_pursahs = 0
    for url_data in urls_pursahs:
        post_id = db.add_post(Config.BLOG_PURSAHS_URL, {
            'title': url_data.get('title', ''),
            'content': '',
            'link': url_data.get('link', ''),
            'published_date': '',
            'author': '',
        })
        if post_id:
            saved_pursahs += 1
    
    logger.info(f"pursahsgospel: {saved_pursahs}/{len(urls_pursahs)}件をデータベースに保存")
    
    all_posts_pursahs = db.get_all_posts(Config.BLOG_PURSAHS_URL)
    logger.info(f"データベース内のpursahsgospel URL数: {len(all_posts_pursahs)}件")
    
    logger.info("\n" + "="*60)
    logger.info("テスト完了")
    logger.info("="*60)


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='URL抽出テスト')
    parser.add_argument('--bot365', action='store_true', help='365botGaryのみテスト')
    parser.add_argument('--pursahs', action='store_true', help='pursahsgospelのみテスト')
    parser.add_argument('--db', action='store_true', help='データベース保存もテスト')
    
    args = parser.parse_args()
    
    if args.db:
        test_database_save()
    elif args.pursahs:
        test_pursahsgospel_extraction()
    elif args.bot365:
        test_365botgary_extraction()
    else:
        # 両方テスト
        test_365botgary_extraction()
        test_pursahsgospel_extraction()


if __name__ == "__main__":
    main()

