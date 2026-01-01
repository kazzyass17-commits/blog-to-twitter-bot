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
        
        # 索引ページのURL（4つの索引）
        index_urls = [
            "http://notesofacim.blog.fc2.com/blog-entry-431.html",  # 索引1（Day001～Day100）
            "http://notesofacim.blog.fc2.com/blog-entry-432.html",  # 索引2（Day101～Day200）
            "http://notesofacim.blog.fc2.com/blog-entry-433.html",  # 索引3（Day201～Day300）
            "http://notesofacim.blog.fc2.com/blog-entry-434.html",  # 索引4（Day301～Day365）
        ]
        
        for index_url in index_urls:
            try:
                logger.info(f"索引ページからURLを抽出中: {index_url}")
                response = self.session.get(index_url, timeout=30)
                response.encoding = response.apparent_encoding or 'utf-8'
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # FC2ブログの索引ページからリンクを抽出
                # blog-entry-で始まるリンクを探す
                links = soup.find_all('a', href=re.compile(r'/blog-entry-\d+\.html'))
                
                for link in links:
                    href = link.get('href', '')
                    if href:
                        # 相対URLを絶対URLに変換
                        if not href.startswith('http'):
                            href = urljoin(index_url, href)
                        
                        # タイトルを取得
                        title = link.get_text(strip=True)
                        if not title:
                            title = link.get('title', '')
                        
                        # 重複チェック
                        if not any(u.get('link') == href for u in urls):
                            urls.append({
                                'link': href,
                                'title': title,
                                'published_date': '',
                                'author': '',
                                'content': ''  # 後で取得
                            })
                
                logger.info(f"索引ページから{len([u for u in urls if index_url in str(u)])}件のURLを抽出")
                
            except Exception as e:
                logger.error(f"索引ページ取得エラー ({index_url}): {e}")
                continue
        
        logger.info(f"合計{len(urls)}件のURLを抽出しました")
        return urls
    
    def extract_pursahsgospel_urls(self) -> List[Dict[str, str]]:
        """
        pursahsgospelの索引ページから個別ページのURLを抽出
        
        Returns:
            個別ページのURLとタイトルのリスト
        """
        urls = []
        
        # 索引ページのURL（2つの索引）
        # 実際のURLを確認する必要がありますが、一般的なパターンで試行
        base_url = "https://www.ameba.jp/profile/general/pursahs-gospel/"
        
        # 索引ページを探す（実際のURL構造に合わせて調整が必要）
        index_urls = [
            f"{base_url}",  # メインページから索引を探す
        ]
        
        try:
            # まずメインページから索引ページのリンクを探す
            response = self.session.get(base_url, timeout=30)
            response.encoding = response.apparent_encoding or 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 索引ページへのリンクを探す（「索引」を含むリンク）
            index_links = soup.find_all('a', href=True, string=re.compile(r'索引'))
            
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
                    
                    # 語録へのリンクを抽出（entry-で始まるリンク）
                    entry_links = index_soup.find_all('a', href=re.compile(r'/entry-\d+\.html'))
                    
                    for link in entry_links:
                        href = link.get('href', '')
                        if href:
                            # 相対URLを絶対URLに変換
                            if not href.startswith('http'):
                                href = urljoin(index_href, href)
                            
                            # タイトルを取得
                            title = link.get_text(strip=True)
                            if not title:
                                title = link.get('title', '')
                            
                            # 重複チェック
                            if not any(u.get('link') == href for u in urls):
                                urls.append({
                                    'link': href,
                                    'title': title,
                                    'published_date': '',
                                    'author': '',
                                    'content': ''  # 後で取得
                                })
                    
                except Exception as e:
                    logger.error(f"索引ページ取得エラー ({index_href}): {e}")
                    continue
            
            logger.info(f"合計{len(urls)}件のURLを抽出しました")
            
        except Exception as e:
            logger.error(f"pursahsgospel URL抽出エラー: {e}")
        
        return urls

