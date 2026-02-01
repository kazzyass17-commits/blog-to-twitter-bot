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
                    # すべてのリンクをチェックして、entry-を含むものを探す
                    all_page_links = index_soup.find_all('a', href=True)
                    entry_links = []
                    
                    # 索引ページ自体のURLを除外するためのセット
                    index_page_urls = set()
                    for il in index_links:
                        il_href = il.get('href', '')
                        if not il_href.startswith('http'):
                            il_href = urljoin(base_url, il_href)
                        index_page_urls.add(il_href.split('?')[0].split('#')[0].rstrip('/'))
                    
                    for link in all_page_links:
                        href = link.get('href', '')
                        if not href:
                            continue
                        
                        link_text = link.get_text(strip=True)
                        
                        # entry-を含むリンクを探す
                        if 'entry-' in href:
                            entry_links.append(link)
                    
                    page_url_count = 0
                    for link in entry_links:
                        href = link.get('href', '')
                        if not href:
                            continue
                        
                        # リンクテキストを取得（ナビゲーションリンクの除外に使用）
                        link_text = link.get_text(strip=True)
                        
                        # 相対URLを絶対URLに変換
                        if not href.startswith('http'):
                            href = urljoin(index_href, href)
                        
                        # 正規化（末尾のスラッシュやパラメータを除去）
                        href = href.split('?')[0].split('#')[0].rstrip('/')
                        
                        # s.ameblo.jpをameblo.jpに統一
                        if 's.ameblo.jp' in href:
                            href = href.replace('s.ameblo.jp', 'ameblo.jp')
                        
                        # httpをhttpsに統一
                        if href.startswith('http://ameblo.jp'):
                            href = href.replace('http://', 'https://')
                        
                        # entry-を含むURLのみを対象
                        if '/entry-' not in href:
                            continue
                        
                        # 索引ページ自体を除外
                        if href in index_page_urls:
                            continue
                        
                        # リンクテキストから語録番号を抽出（柔軟なパターンマッチング）
                        # 「語録」と数字を分けて検索し、全角数字を半角に変換
                        def extract_goroku_number_from_text(text):
                            """テキストから語録番号を抽出（全角数字を3桁まで検出して半角に変換）"""
                            if not text:
                                return None
                            # パターン: 「語録」+ 全角数字（1-3桁）または半角数字
                            patterns = [
                                r'語録[　\s]*([０-９]{1,3})',  # 語録の後に全角数字（1-3桁）
                                r'語録[　\s]*\([Logion\s]*\)[　\s]*([０-９]{1,3})',  # 語録(Logion) １
                                r'語録[　\s]*\([　\s]*([０-９]{1,3})[　\s]*\)',  # 語録(１)
                                r'語録[　\s]*([0-9]{1,3})',  # 語録の後に半角数字（1-3桁）
                            ]
                            for pattern in patterns:
                                match = re.search(pattern, text)
                                if match:
                                    num_str = match.group(1)
                                    # 全角数字を半角数字に変換（3桁まで対応）
                                    if any(c in num_str for c in '０１２３４５６７８９'):
                                        num_str = num_str.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
                                    try:
                                        return int(num_str)
                                    except ValueError:
                                        continue
                            return None
                        
                        # リンクテキストから語録番号を抽出
                        goroku_num = extract_goroku_number_from_text(link_text)
                        
                        # リンクテキストに語録番号がない場合、親要素の直近のテキストを確認
                        # （ただし、親要素全体ではなく、リンクの前後を確認）
                        if not goroku_num:
                            parent = link.parent
                            if parent:
                                # 親要素のテキストを取得するが、リンク前後のみを確認
                                # リンクの前のテキストを取得
                                prev_sibling = link.previous_sibling
                                if prev_sibling and hasattr(prev_sibling, 'string'):
                                    prev_text = str(prev_sibling.string) if prev_sibling.string else ''
                                    goroku_num = extract_goroku_number_from_text(prev_text)
                                
                                # それでも見つからなければ、親要素のテキストから検索
                                if not goroku_num:
                                    parent_text = parent.get_text(strip=True)
                                    # リンクテキストの位置を基準に、その前後の短い範囲を抽出
                                    link_pos = parent_text.find(link_text)
                                    if link_pos >= 0:
                                        # リンクテキストの前50文字と後50文字を確認
                                        start = max(0, link_pos - 50)
                                        end = min(len(parent_text), link_pos + len(link_text) + 50)
                                        context_text = parent_text[start:end]
                                        goroku_num = extract_goroku_number_from_text(context_text)
                        
                        # 「次へ」「戻る」「索引」などのナビゲーションリンクを除外
                        # ただし、語録番号が抽出できた場合は語録ページとして扱う
                        link_text_lower = link_text.lower()
                        if any(nav in link_text_lower for nav in ['次へ', '戻る', '前へ', '索引', 'top', 'home']):
                            # 語録番号が抽出できない場合は除外
                            if not goroku_num:
                                continue
                        
                        # 重複チェック
                        if href in seen_urls:
                            continue
                        
                        seen_urls.add(href)
                        
                        # タイトルを取得（link_textを優先）
                        title = link_text
                        if not title:
                            title = link.get('title', '')
                        if not title:
                            # 親要素からタイトルを取得（ただし、全体ではなくリンク周辺のみ）
                            parent = link.parent
                            if parent:
                                # リンクテキストを含む部分のみを取得
                                parent_full_text = parent.get_text(strip=True)
                                link_pos = parent_full_text.find(link_text)
                                if link_pos >= 0:
                                    # リンクテキストの前後100文字のみを使用
                                    start = max(0, link_pos - 100)
                                    end = min(len(parent_full_text), link_pos + len(link_text) + 100)
                                    title = parent_full_text[start:end].strip()
                                else:
                                    title = parent_full_text[:200].strip()  # 最初の200文字のみ
                        
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
