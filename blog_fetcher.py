"""
ブログコンテンツ取得モジュール
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import feedparser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlogFetcher:
    """ブログコンテンツを取得するクラス"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_latest_post(self) -> Optional[Dict[str, str]]:
        """
        最新の投稿を取得
        
        Returns:
            投稿情報の辞書（title, content, link, published_date）またはNone
        """
        try:
            # RSSフィードを試行
            rss_urls = self._get_rss_urls()
            for rss_url in rss_urls:
                post = self._fetch_from_rss(rss_url)
                if post:
                    return post
            
            # RSSが取得できない場合は、HTMLから直接取得
            return self._fetch_from_html()
            
        except Exception as e:
            logger.error(f"ブログ取得エラー: {e}")
            return None
    
    def _get_rss_urls(self) -> List[str]:
        """RSSフィードのURLを生成"""
        parsed = urlparse(self.base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # FC2ブログの場合
        if 'fc2.com' in self.base_url:
            # FC2ブログのRSS URLパターン
            blog_id = self.base_url.split('/')[-2] if self.base_url.endswith('/') else self.base_url.split('/')[-1]
            return [
                f"{self.base_url}?xml",
                f"{self.base_url}rss.xml",
                f"{self.base_url}index.rdf",
            ]
        
        # Amebaブログの場合
        elif 'ameba.jp' in self.base_url:
            return [
                f"{self.base_url}rss20.xml",
                f"{self.base_url}?xml",
            ]
        
        # その他の場合
        return [
            f"{self.base_url}rss.xml",
            f"{self.base_url}feed",
            f"{self.base_url}?feed=rss2",
        ]
    
    def _fetch_from_rss(self, rss_url: str) -> Optional[Dict[str, str]]:
        """RSSフィードから最新投稿を取得"""
        try:
            logger.info(f"RSS取得を試行: {rss_url}")
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                entry = feed.entries[0]  # 最新のエントリ
                return {
                    'title': entry.get('title', ''),
                    'content': self._clean_html(entry.get('summary', '') or entry.get('description', '')),
                    'link': entry.get('link', ''),
                    'published_date': entry.get('published', ''),
                    'author': entry.get('author', ''),
                }
        except Exception as e:
            logger.debug(f"RSS取得失敗 ({rss_url}): {e}")
            return None
    
    def fetch_all_posts(self, max_posts: int = 100) -> List[Dict[str, str]]:
        """
        ブログから全投稿を取得
        
        Args:
            max_posts: 取得する最大投稿数
        
        Returns:
            投稿情報のリスト
        """
        posts = []
        try:
            # RSSフィードから取得を試行
            rss_urls = self._get_rss_urls()
            for rss_url in rss_urls:
                try:
                    logger.info(f"RSSから全投稿取得を試行: {rss_url}")
                    feed = feedparser.parse(rss_url)
                    
                    if feed.entries:
                        for entry in feed.entries[:max_posts]:
                            post = {
                                'title': entry.get('title', ''),
                                'content': self._clean_html(entry.get('summary', '') or entry.get('description', '')),
                                'link': entry.get('link', ''),
                                'published_date': entry.get('published', ''),
                                'author': entry.get('author', ''),
                            }
                            # 重複チェック
                            if not any(p.get('link') == post.get('link') for p in posts):
                                posts.append(post)
                        
                        if posts:
                            logger.info(f"RSSから{len(posts)}件の投稿を取得")
                            return posts
                except Exception as e:
                    logger.debug(f"RSS取得失敗 ({rss_url}): {e}")
                    continue
            
            # RSSが取得できない場合は、HTMLから複数ページを取得
            logger.info("HTMLから投稿を取得します（制限: 最新数件のみ）")
            html_posts = self._fetch_multiple_from_html(max_posts)
            if html_posts:
                return html_posts
            
        except Exception as e:
            logger.error(f"全投稿取得エラー: {e}")
        
        return posts
    
    def _fetch_multiple_from_html(self, max_posts: int = 20) -> List[Dict[str, str]]:
        """HTMLから複数の投稿を取得（ページネーション対応は難しいため、最初のページのみ）"""
        posts = []
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.encoding = response.apparent_encoding or 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # FC2ブログの場合
            if 'fc2.com' in self.base_url:
                entries = soup.find_all(['article', 'div'], class_=lambda x: x and ('entry' in x.lower() or 'post' in x.lower()))
                if not entries:
                    entries = soup.find_all('div', id=lambda x: x and 'entry' in x.lower())
                
                for entry in entries[:max_posts]:
                    post = self._parse_fc2_entry(entry)
                    if post:
                        posts.append(post)
            
            # Amebaブログの場合
            elif 'ameba.jp' in self.base_url:
                entries = soup.find_all(['article', 'div'], class_=lambda x: x and ('entry' in x.lower() or 'article' in x.lower() or 'post' in x.lower()))
                if not entries:
                    entries = soup.find_all('div', id=lambda x: x and ('entry' in x.lower() or 'article' in x.lower()))
                
                for entry in entries[:max_posts]:
                    post = self._parse_ameba_entry(entry)
                    if post:
                        posts.append(post)
            
        except Exception as e:
            logger.error(f"HTMLから複数取得エラー: {e}")
        
        return posts
    
    def _parse_fc2_entry(self, entry) -> Optional[Dict[str, str]]:
        """FC2ブログのエントリを解析"""
        try:
            title_elem = entry.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in x.lower())
            if not title_elem:
                title_elem = entry.find('a', href=lambda x: x and '/blog-entry-' in str(x))
            
            title = title_elem.get_text(strip=True) if title_elem else ""
            link = title_elem.get('href', '') if title_elem and title_elem.name == 'a' else ''
            
            if not link or not title:
                return None
            
            if link and not link.startswith('http'):
                link = urljoin(self.base_url, link)
            
            content_elem = entry.find(['div', 'p'], class_=lambda x: x and ('content' in x.lower() or 'entry' in x.lower() or 'text' in x.lower()))
            if not content_elem:
                content_elem = entry.find('div', id=lambda x: x and 'entry_body' in x.lower())
            
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            return {
                'title': title,
                'content': content[:500] if content else "",
                'link': link,
                'published_date': '',
                'author': '',
            }
        except Exception as e:
            logger.debug(f"FC2エントリ解析エラー: {e}")
            return None
    
    def _parse_ameba_entry(self, entry) -> Optional[Dict[str, str]]:
        """Amebaブログのエントリを解析"""
        try:
            title_elem = entry.find(['h2', 'h3', 'h4', 'a'], class_=lambda x: x and 'title' in x.lower())
            if not title_elem:
                title_elem = entry.find('a')
            
            title = title_elem.get_text(strip=True) if title_elem else ""
            link = title_elem.get('href', '') if title_elem and title_elem.name == 'a' else ''
            
            if not link or not title:
                return None
            
            if link and not link.startswith('http'):
                link = urljoin(self.base_url, link)
            
            content_elem = entry.find(['div', 'p', 'section'], class_=lambda x: x and ('content' in x.lower() or 'text' in x.lower() or 'body' in x.lower()))
            if not content_elem:
                content_elem = entry.find('div', class_='skin-entryBody')
            
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            return {
                'title': title,
                'content': content[:500] if content else "",
                'link': link,
                'published_date': '',
                'author': '',
            }
        except Exception as e:
            logger.debug(f"Amebaエントリ解析エラー: {e}")
            return None
    
    def _fetch_from_html(self) -> Optional[Dict[str, str]]:
        """HTMLから直接最新投稿を取得"""
        try:
            logger.info(f"HTMLから取得を試行: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.encoding = response.apparent_encoding or 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 個別ページの場合（blog-entry-やentry-を含むURL）
            if '/blog-entry-' in self.base_url or '/entry-' in self.base_url:
                return self._parse_single_page(soup)
            
            # FC2ブログの場合
            if 'fc2.com' in self.base_url:
                return self._parse_fc2_blog(soup)
            
            # Amebaブログの場合
            elif 'ameba.jp' in self.base_url:
                return self._parse_ameba_blog(soup)
            
            # その他の場合、一般的なブログ構造を試行
            return self._parse_generic_blog(soup)
            
        except Exception as e:
            logger.error(f"HTML取得エラー: {e}")
            return None
    
    def _parse_single_page(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """個別ページを解析"""
        try:
            # FC2ブログの個別ページ
            if 'fc2.com' in self.base_url and '/blog-entry-' in self.base_url:
                # タイトル取得
                title_elem = soup.find(['h1', 'h2', 'h3'], class_=lambda x: x and 'title' in x.lower())
                if not title_elem:
                    title_elem = soup.find('title')
                
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # コンテンツ取得（複数の方法で試す）
                content_elem = None
                
                # 方法1: classにentry_bodyを含むdiv
                content_elem = soup.find('div', class_='entry_body')
                
                # 方法2: classにentry_bodyを含むdiv（他の方法）
                if not content_elem:
                    for div in soup.find_all('div', class_=True):
                        classes = ' '.join(div.get('class', []))
                        if 'entry_body' in classes.lower():
                            content_elem = div
                            break
                
                # 方法3: classにcontentを含むdiv（idがeで始まるもの）
                if not content_elem:
                    content_elem = soup.find('div', class_='content', id=lambda x: x and str(x).startswith('e'))
                
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                return {
                    'title': title,
                    'content': content[:500] if content else "",
                    'link': self.base_url,
                    'published_date': '',
                    'author': '',
                }
            
            # Amebaブログの個別ページ
            elif 'ameba.jp' in self.base_url and '/entry-' in self.base_url:
                # タイトル取得
                title_elem = soup.find(['h1', 'h2', 'h3'], class_=lambda x: x and 'title' in x.lower())
                if not title_elem:
                    title_elem = soup.find('title')
                
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # コンテンツ取得
                content_elem = soup.find(['div', 'article', 'section'], class_=lambda x: x and ('entry' in x.lower() or 'content' in x.lower() or 'body' in x.lower() or 'text' in x.lower()))
                if not content_elem:
                    content_elem = soup.find('div', class_='skin-entryBody')
                
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                return {
                    'title': title,
                    'content': content[:500] if content else "",
                    'link': self.base_url,
                    'published_date': '',
                    'author': '',
                }
            
            # その他の個別ページ
            else:
                title_elem = soup.find(['h1', 'title'])
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                content_elem = soup.find(['article', 'main', 'div'], class_=lambda x: x and ('content' in x.lower() or 'entry' in x.lower() or 'post' in x.lower()))
                if not content_elem:
                    content_elem = soup.find('main') or soup.find('article')
                
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                return {
                    'title': title,
                    'content': content[:500] if content else "",
                    'link': self.base_url,
                    'published_date': '',
                    'author': '',
                }
        except Exception as e:
            logger.error(f"個別ページ解析エラー: {e}")
            return None
    
    def _parse_fc2_blog(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """FC2ブログのHTMLを解析"""
        try:
            # FC2ブログの記事エントリを探す
            entries = soup.find_all(['article', 'div'], class_=lambda x: x and ('entry' in x.lower() or 'post' in x.lower()))
            
            if not entries:
                # 別のパターンを試行
                entries = soup.find_all('div', id=lambda x: x and 'entry' in x.lower())
            
            if entries:
                entry = entries[0]
                
                # タイトル取得
                title_elem = entry.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in x.lower())
                if not title_elem:
                    title_elem = entry.find('a', href=lambda x: x and '/blog-entry-' in str(x))
                
                title = title_elem.get_text(strip=True) if title_elem else "タイトルなし"
                link = title_elem.get('href', '') if title_elem and title_elem.name == 'a' else ''
                
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)
                
                # コンテンツ取得
                content_elem = entry.find(['div', 'p'], class_=lambda x: x and ('content' in x.lower() or 'entry' in x.lower() or 'text' in x.lower()))
                if not content_elem:
                    content_elem = entry.find('div', id=lambda x: x and 'entry_body' in x.lower())
                
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                return {
                    'title': title,
                    'content': content[:500] if content else "",  # 最初の500文字
                    'link': link or self.base_url,
                    'published_date': '',
                    'author': '',
                }
        except Exception as e:
            logger.error(f"FC2ブログ解析エラー: {e}")
        
        return None
    
    def _parse_ameba_blog(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """AmebaブログのHTMLを解析"""
        try:
            # Amebaブログの記事エントリを探す
            entries = soup.find_all(['article', 'div'], class_=lambda x: x and ('entry' in x.lower() or 'article' in x.lower() or 'post' in x.lower()))
            
            if not entries:
                entries = soup.find_all('div', id=lambda x: x and ('entry' in x.lower() or 'article' in x.lower()))
            
            if entries:
                entry = entries[0]
                
                # タイトル取得
                title_elem = entry.find(['h2', 'h3', 'h4', 'a'], class_=lambda x: x and 'title' in x.lower())
                if not title_elem:
                    title_elem = entry.find('a')
                
                title = title_elem.get_text(strip=True) if title_elem else "タイトルなし"
                link = title_elem.get('href', '') if title_elem and title_elem.name == 'a' else ''
                
                if link and not link.startswith('http'):
                    link = urljoin(self.base_url, link)
                
                # コンテンツ取得
                content_elem = entry.find(['div', 'p', 'section'], class_=lambda x: x and ('content' in x.lower() or 'text' in x.lower() or 'body' in x.lower()))
                if not content_elem:
                    content_elem = entry.find('div', class_='skin-entryBody')
                
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                return {
                    'title': title,
                    'content': content[:500] if content else "",
                    'link': link or self.base_url,
                    'published_date': '',
                    'author': '',
                }
        except Exception as e:
            logger.error(f"Amebaブログ解析エラー: {e}")
        
        return None
    
    def _parse_generic_blog(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """一般的なブログ構造を解析"""
        try:
            # 記事エントリを探す
            entries = soup.find_all(['article', 'div'], class_=lambda x: x and ('entry' in x.lower() or 'post' in x.lower() or 'article' in x.lower()))
            
            if entries:
                entry = entries[0]
                
                # タイトルとリンク
                title_elem = entry.find(['h1', 'h2', 'h3', 'a'])
                title = title_elem.get_text(strip=True) if title_elem else "タイトルなし"
                link = title_elem.get('href', '') if title_elem and title_elem.name == 'a' else self.base_url
                
                # コンテンツ
                content_elem = entry.find(['div', 'p', 'section'])
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                return {
                    'title': title,
                    'content': content[:500] if content else "",
                    'link': link,
                    'published_date': '',
                    'author': '',
                }
        except Exception as e:
            logger.error(f"一般的なブログ解析エラー: {e}")
        
        return None
    
    def _clean_html(self, html: str) -> str:
        """HTMLタグを削除してテキストのみを抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(strip=True)

