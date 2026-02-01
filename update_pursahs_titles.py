"""
pursahsgospelのタイトルを正しく更新するスクリプト
各ページにアクセスしてタイトルを取得し、データベースを更新
"""
import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_pursahs_titles.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_title_from_page(url: str) -> str:
    """ページからタイトルを取得"""
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get(url, timeout=30)
        response.encoding = response.apparent_encoding or 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # タイトルを取得（複数の方法を試す）
        new_title = None
        
        # 1. h1.entry-title クラス
        title_elem = soup.find('h1', class_='entry-title')
        if title_elem:
            new_title = title_elem.get_text(strip=True)
        
        # 2. h1.skin-entryTitle クラス
        if not new_title:
            title_elem = soup.find('h1', class_='skin-entryTitle')
            if title_elem:
                new_title = title_elem.get_text(strip=True)
        
        # 3. h2.entry_header クラス
        if not new_title:
            title_elem = soup.find('h2', class_='entry_header')
            if title_elem:
                new_title = title_elem.get_text(strip=True)
        
        # 4. og:title メタタグ
        if not new_title:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                new_title = og_title.get('content', '').strip()
        
        # 5. title タグ（最後の手段）
        if not new_title:
            title_tag = soup.find('title')
            if title_tag:
                new_title = title_tag.get_text(strip=True)
                # 「 | Pursah's Gospelのブログ」などを削除
                new_title = re.sub(r'\s*\|\s*Pursah\'?s Gospelのブログ\s*$', '', new_title)
                new_title = re.sub(r'\s*\|\s*パーサによるトマスの福音書\s*$', '', new_title)
        
        return new_title.strip() if new_title else ""
        
    except Exception as e:
        logger.error(f"タイトル取得エラー ({url}): {e}")
        return ""

def update_titles():
    """pursahsgospelのタイトルを更新"""
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    
    # pursahsgospelの全投稿を取得
    cursor.execute("""
        SELECT id, title, link 
        FROM posts 
        WHERE blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%' 
        ORDER BY id
    """)
    rows = cursor.fetchall()
    
    logger.info(f"修正対象: {len(rows)}件")
    logger.info("=" * 60)
    
    updated = 0
    skipped = 0
    errors = 0
    
    for i, row in enumerate(rows, 1):
        post_id, old_title, link = row
        
        try:
            # タイトルに「語録」が含まれている場合はスキップ（既に正しい可能性が高い）
            if '語録' in old_title and '原書' not in old_title:
                logger.debug(f"ID:{post_id:3d} | スキップ（既に語録タイトル）: {old_title[:40]}...")
                skipped += 1
                continue
            
            # ページからタイトルを取得
            new_title = fetch_title_from_page(link)
            
            if new_title and new_title != old_title:
                # タイトルを更新
                cursor.execute("UPDATE posts SET title = ? WHERE id = ?", (new_title, post_id))
                logger.info(f"ID:{post_id:3d} | {old_title[:30]}... → {new_title[:50]}...")
                updated += 1
            elif new_title:
                logger.debug(f"ID:{post_id:3d} | 変更なし: {old_title[:40]}...")
            else:
                logger.warning(f"ID:{post_id:3d} | タイトル取得失敗: {link}")
                errors += 1
            
            # レート制限対策（0.5秒待機）
            if i < len(rows):
                time.sleep(0.5)
            
            # 進捗表示（10件ごと）
            if i % 10 == 0:
                logger.info(f"進捗: {i}/{len(rows)} 件処理完了（更新: {updated}件, スキップ: {skipped}件, エラー: {errors}件）")
        
        except Exception as e:
            logger.error(f"ID:{post_id:3d} | エラー: {e}")
            errors += 1
    
    conn.commit()
    conn.close()
    
    logger.info("=" * 60)
    logger.info(f"更新完了: 更新 {updated}件, スキップ {skipped}件, エラー {errors}件")
    
    # 語録投稿数を確認
    conn = sqlite3.connect('posts.db')
    cur = conn.cursor()
    goroku_rows = cur.execute("""
        SELECT COUNT(*) FROM posts 
        WHERE (blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%') 
        AND title LIKE '%語録%' 
        AND title NOT LIKE '%原書%'
    """).fetchone()
    logger.info(f"語録投稿数（原書除外）: {goroku_rows[0]} 件")
    conn.close()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("pursahsgospel タイトル更新スクリプト")
    logger.info("=" * 60)
    update_titles()
