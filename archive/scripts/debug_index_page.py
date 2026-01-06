"""
索引ページのHTML構造を確認するデバッグスクリプト
"""
import requests
from bs4 import BeautifulSoup
import re

def debug_365botgary_index(index_num: int):
    """365botGaryの索引ページをデバッグ"""
    index_urls = {
        1: "http://notesofacim.blog.fc2.com/blog-entry-431.html",
        2: "http://notesofacim.blog.fc2.com/blog-entry-432.html",
        3: "http://notesofacim.blog.fc2.com/blog-entry-433.html",
        4: "http://notesofacim.blog.fc2.com/blog-entry-434.html",
    }
    
    url = index_urls.get(index_num)
    if not url:
        print(f"無効な索引番号: {index_num}")
        return
    
    print(f"\n{'='*60}")
    print(f"索引{index_num}のデバッグ: {url}")
    print(f"{'='*60}\n")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=30)
        response.encoding = response.apparent_encoding or 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # すべてのリンクを探す
        all_links = soup.find_all('a', href=True)
        blog_entry_links = []
        
        for link in all_links:
            href = link.get('href', '')
            if 'blog-entry-' in href:
                blog_entry_links.append((href, link.get_text(strip=True)))
        
        print(f"blog-entry-を含むリンク数: {len(blog_entry_links)}")
        print(f"\n最初の10件:")
        for i, (href, text) in enumerate(blog_entry_links[:10], 1):
            print(f"  {i}. {href[:80]} - {text[:50]}")
        
        print(f"\n最後の10件:")
        for i, (href, text) in enumerate(blog_entry_links[-10:], len(blog_entry_links)-9):
            print(f"  {i}. {href[:80]} - {text[:50]}")
        
        # HTMLの一部を表示（デバッグ用）
        print(f"\n\nHTML構造のサンプル（最初の1000文字）:")
        try:
            print(response.text[:1000])
        except UnicodeEncodeError:
            print(response.text[:1000].encode('utf-8', errors='ignore').decode('utf-8'))
        
    except Exception as e:
        print(f"エラー: {e}")


def debug_pursahsgospel_index():
    """pursahsgospelの索引ページをデバッグ"""
    base_url = "https://www.ameba.jp/profile/general/pursahs-gospel/"
    
    print(f"\n{'='*60}")
    print(f"pursahsgospel メインページのデバッグ: {base_url}")
    print(f"{'='*60}\n")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(base_url, timeout=30)
        response.encoding = response.apparent_encoding or 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 索引ページへのリンクを探す
        all_links = soup.find_all('a', href=True)
        index_links = []
        
        for link in all_links:
            link_text = link.get_text(strip=True)
            if '索引' in link_text:
                index_links.append((link.get('href', ''), link_text))
        
        print(f"索引ページへのリンク数: {len(index_links)}")
        for href, text in index_links:
            print(f"  - {href} - {text}")
        
        # 各索引ページを確認
        for href, text in index_links:
            if not href.startswith('http'):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            
            print(f"\n\n索引ページ: {href} ({text})")
            print("-" * 60)
            
            try:
                index_response = session.get(href, timeout=30)
                index_response.encoding = index_response.apparent_encoding or 'utf-8'
                index_response.raise_for_status()
                
                index_soup = BeautifulSoup(index_response.text, 'html.parser')
                
                # entry-を含むリンクを探す
                all_entry_links = index_soup.find_all('a', href=True)
                entry_links = []
                
                for link in all_entry_links:
                    link_href = link.get('href', '')
                    if 'entry-' in link_href:
                        entry_links.append((link_href, link.get_text(strip=True)))
                
                print(f"entry-を含むリンク数: {len(entry_links)}")
                print(f"\n最初の5件:")
                for i, (h, t) in enumerate(entry_links[:5], 1):
                    print(f"  {i}. {h[:80]} - {t[:50]}")
                
            except Exception as e:
                print(f"エラー: {e}")
        
    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "pursahs":
            debug_pursahsgospel_index()
        else:
            try:
                index_num = int(sys.argv[1])
                debug_365botgary_index(index_num)
            except ValueError:
                print("使用方法: python debug_index_page.py [1-4|pursahs]")
    else:
        print("使用方法: python debug_index_page.py [1-4|pursahs]")
        print("\n例:")
        print("  python debug_index_page.py 4  # 365botGaryの索引4をデバッグ")
        print("  python debug_index_page.py pursahs  # pursahsgospelをデバッグ")

