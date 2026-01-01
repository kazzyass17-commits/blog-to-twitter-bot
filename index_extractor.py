"""
索引ページから個別ページのURLを抽出するモジュール
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin, urlparse
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndexExtractor:
    """索引ページから個別ページのURLを抽出するクラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_365botgary_urls(self) -> List[Dict[str, str]]:
        """
        365botgaryの索引ページから個別ページのURLを抽出
        
        Returns:
            個別ページのURLとタイトルのリスト
        """
        urls = []
        seen_urls = set()  # 重複チェック用
        
        # 索引ページのURL（4つの索引）
        index_urls = [
            "http://notesofacim.blog.fc2.com/blog-entry-431.html",  # 索引1（Day001～Day100）
            "http://notesofacim.blog.fc2.com/blog-entry-432.html",  # 索引2（Day101～Day200）
            "http://notesofacim.blog.fc2.com/blog-entry-433.html",  # 索引3（Day201～Day300）
            "http://notesofacim.blog.fc2.com/blog-entry-434.html",  # 索引4（Day301～Day365）
        ]
        
        # 索引ページ自体のURLを除外するためのセット
        index_urls_set = set(index_urls)
        
        for index_url in index_urls:
            try:
                logger.info(f"索引ページからURLを抽出中: {index_url}")
                response = self.session.get(index_url, timeout=30)
                response.encoding = response.apparent_encoding or 'utf-8'
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # より包括的なリンク抽出
                # 1. blog-entry-で始まるリンクを探す（複数のパターンを試行）
                patterns = [
                    r'/blog-entry-\d+\.html',  # 標準パターン
                    r'blog-entry-\d+\.html',   # 相対パターン
                    r'http://notesofacim\.blog\.fc2\.com/blog-entry-\d+\.html',  # 絶対URLパターン
                ]
                
                all_links = []
                for pattern in patterns:
                    links = soup.find_all('a', href=re.compile(pattern))
                    all_links.extend(links)
                
                # 2. すべてのリンクをチェックして、blog-entry-を含むものを探す
                if not all_links:
                    all_page_links = soup.find_all('a', href=True)
                    for link in all_page_links:
                        href = link.get('href', '')
                        if 'blog-entry-' in href and '.html' in href:
                            all_links.append(link)
                
                page_url_count = 0
                for link in all_links:
                    href = link.get('href', '')
                    if not href:
                        continue
                    
                    # 相対URLを絶対URLに変換
                    if not href.startswith('http'):
                        href = urljoin(index_url, href)
                    
                    # 正規化（末尾のスラッシュやパラメータを除去）
                    href = href.split('?')[0].split('#')[0].rstrip('/')
                    
                    # 索引ページ自体を除外
                    if href in index_urls_set:
                        continue
                    
                    # blog-entry-を含むURLのみを対象
                    if 'blog-entry-' not in href:
                        continue
                    
                    # 重複チェック
                    if href in seen_urls:
                        continue
                    
                    seen_urls.add(href)
                    
                    # タイトルを取得
                    title = link.get_text(strip=True)
                    if not title:
                        title = link.get('title', '')
                    if not title:
                        # 親要素からタイトルを取得
                        parent = link.parent
                        if parent:
                            title = parent.get_text(strip=True)
                    
                    urls.append({
                        'link': href,
                        'title': title,
                        'published_date': '',
                        'author': '',
                        'content': ''  # 後で取得
                    })
                    page_url_count += 1
                
                logger.info(f"この索引ページから{page_url_count}件のURLを抽出")
                
            except Exception as e:
                logger.error(f"索引ページ取得エラー ({index_url}): {e}", exc_info=True)
                continue
        
        logger.info(f"合計{len(urls)}件のURLを抽出しました（重複除外後）")
        return urls
    
    def extract_pursahsgospel_urls(self) -> List[Dict[str, str]]:
        """
        pursahsgospelの索引ページから個別ページのURLを抽出
        
        Returns:
            個別ページのURLとタイトルのリスト
        """
        urls = []
        seen_urls = set()  # 重複チェック用
        
        base_url = "https://www.ameba.jp/profile/general/pursahs-gospel/"
        
        try:
            # メインページから索引ページのリンクを探す
            logger.info(f"メインページから索引を検索: {base_url}")
            response = self.session.get(base_url, timeout=30)
            response.encoding = response.apparent_encoding or 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 索引ページへのリンクを探す（「索引」を含むリンク）
            # テキストに「索引」を含むリンクを探す
            all_links = soup.find_all('a', href=True)
            index_links = []
            
            for link in all_links:
                link_text = link.get_text(strip=True)
                # 「索引」を含む、または「語録」を含むリンクも索引ページの可能性がある
                if '索引' in link_text or ('語録' in link_text and '索引' in link_text):
                    index_links.append(link)
            
            logger.info(f"{len(index_links)}個の索引ページリンクを発見")
            
            # 各索引ページから個別ページのURLを抽出
            for index_link in index_links:
                index_href = index_link.get('href', '')
                if not index_href.startswith('http'):
                    index_href = urljoin(base_url, index_href)
                
                try:
                    logger.info(f"索引ページからURLを抽出中: {index_href}")
                    index_response = self.session.get(index_href, timeout=30)
                    index_response.encoding = index_response.apparent_encoding or 'utf-8'
                    index_response.raise_for_status()
                    
                    index_soup = BeautifulSoup(index_response.text, 'html.parser')
                    
                    # より包括的なリンク抽出
                    # 1. entry-で始まるリンクを探す（複数のパターンを試行）
                    patterns = [
                        r'/entry-\d+\.html',  # 標準パターン
                        r'entry-\d+\.html',   # 相対パターン
                        r'ameblo\.jp/.*?/entry-\d+\.html',  # 絶対URLパターン
                    ]
                    
                    entry_links = []
                    for pattern in patterns:
                        links = index_soup.find_all('a', href=re.compile(pattern))
                        entry_links.extend(links)
                    
                    # 2. すべてのリンクをチェックして、entry-を含むものを探す
                    if not entry_links:
                        all_page_links = index_soup.find_all('a', href=True)
                        for link in all_page_links:
                            href = link.get('href', '')
                            link_text = link.get_text(strip=True)
                            # entry-を含む、または語録番号を含むリンク
                            if '/entry-' in href or (re.search(r'語録\d+', link_text) and 'entry-' in href):
                                entry_links.append(link)
                    
                    page_url_count = 0
                    for link in entry_links:
                        href = link.get('href', '')
                        if not href:
                            continue
                        
                        # 相対URLを絶対URLに変換
                        if not href.startswith('http'):
                            href = urljoin(index_href, href)
                        
                        # 正規化（末尾のスラッシュやパラメータを除去）
                        href = href.split('?')[0].split('#')[0].rstrip('/')
                        
                        # entry-を含むURLのみを対象
                        if '/entry-' not in href:
                            continue
                        
                        # 重複チェック
                        if href in seen_urls:
                            continue
                        
                        seen_urls.add(href)
                        
                        # タイトルを取得
                        title = link.get_text(strip=True)
                        if not title:
                            title = link.get('title', '')
                        if not title:
                            # 親要素からタイトルを取得
                            parent = link.parent
                            if parent:
                                title = parent.get_text(strip=True)
                        
                        urls.append({
                            'link': href,
                            'title': title,
                            'published_date': '',
                            'author': '',
                            'content': ''  # 後で取得
                        })
                        page_url_count += 1
                    
                    logger.info(f"この索引ページから{page_url_count}件のURLを抽出")
                    
                except Exception as e:
                    logger.error(f"索引ページ取得エラー ({index_href}): {e}", exc_info=True)
                    continue
            
            logger.info(f"合計{len(urls)}件のURLを抽出しました（重複除外後）")
            
        except Exception as e:
            logger.error(f"pursahsgospel URL抽出エラー: {e}", exc_info=True)
        
        return urls

