"""pursahsgospelのタイトルを正しく修正"""
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

conn = sqlite3.connect('posts.db')
cursor = conn.cursor()

# pursahsgospelの全投稿を取得
cursor.execute("SELECT id, title, link FROM posts WHERE blog_url LIKE '%pursahs%' OR blog_url LIKE '%ameblo%' ORDER BY id")
rows = cursor.fetchall()

print(f"修正対象: {len(rows)}件")
print()

updated = 0
for row in rows:
    post_id, old_title, link = row
    
    try:
        # ページからタイトルを取得
        response = requests.get(link, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # タイトルを取得（複数の方法を試す）
        new_title = None
        
        # 1. entry-title クラス
        title_elem = soup.find('h1', class_='entry-title')
        if title_elem:
            new_title = title_elem.get_text(strip=True)
        
        # 2. skin-entryTitle クラス
        if not new_title:
            title_elem = soup.find('h1', class_='skin-entryTitle')
            if title_elem:
                new_title = title_elem.get_text(strip=True)
        
        # 3. og:title メタタグ
        if not new_title:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                new_title = og_title.get('content', '').strip()
        
        # 4. title タグ
        if not new_title:
            title_tag = soup.find('title')
            if title_tag:
                new_title = title_tag.get_text(strip=True)
        
        if new_title and new_title != old_title:
            # タイトルを更新
            cursor.execute("UPDATE posts SET title = ? WHERE id = ?", (new_title, post_id))
            print(f"ID:{post_id:3d} | {old_title[:30]}... → {new_title[:30]}...")
            updated += 1
        else:
            print(f"ID:{post_id:3d} | 変更なし: {old_title[:40]}...")
        
        time.sleep(0.3)  # レート制限対策
        
    except Exception as e:
        print(f"ID:{post_id:3d} | エラー: {e}")

conn.commit()
conn.close()

print()
print(f"更新完了: {updated}件")

