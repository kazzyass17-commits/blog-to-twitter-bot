"""
365botGaryのブログ（http://notesofacim.blog.fc2.com/）を1つのPDFにまとめる
"""
import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging
import time
import re
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ブログのインデックスページ（365日分が4つのインデックスページに分かれている）
INDEX_URLS = [
    "http://notesofacim.blog.fc2.com/blog-entry-431.html",  # Day001～Day100
    "http://notesofacim.blog.fc2.com/blog-entry-432.html",  # Day101～Day200
    "http://notesofacim.blog.fc2.com/blog-entry-433.html",  # Day201～Day300
    "http://notesofacim.blog.fc2.com/blog-entry-430.html",  # Day301～Day365
]


def extract_all_post_urls() -> list[str]:
    """全インデックスページから個別投稿のURLを抽出（既存のindex_extractor.pyのロジックを使用）"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    urls = []
    seen_urls = set()
    
    # 索引ページ自体のURLを除外
    index_urls_set = set(INDEX_URLS)
    index_urls_set.add("http://notesofacim.blog.fc2.com/blog-entry-434.html")
    
    for index_url in INDEX_URLS:
        try:
            logger.info(f"索引ページからURLを抽出中: {index_url}")
            response = session.get(index_url, timeout=30)
            response.encoding = response.apparent_encoding or 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # すべてのリンクを取得
            all_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'blog-entry-' in href and '.html' in href:
                    all_links.append(link)
            
            # テーブルやリスト内のリンクも探す
            if len(all_links) < 50:
                for element in soup.find_all(['td', 'li', 'div', 'p']):
                    links_in_element = element.find_all('a', href=True)
                    for link in links_in_element:
                        href = link.get('href', '')
                        link_text = link.get_text(strip=True)
                        if ('blog-entry-' in href and '.html' in href) or \
                           (re.search(r'Day\d+', link_text) and 'blog-entry-' in href):
                            if link not in all_links:
                                all_links.append(link)
            
            # URLを正規化して追加
            for link in all_links:
                href = link.get('href', '')
                if not href:
                    continue
                
                # 絶対URLに変換
                full_url = urljoin(index_url, href)
                
                # 正規化（パラメータを除去）
                parsed = urlparse(full_url)
                normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
                # 索引ページ自体は除外
                if normalized_url in index_urls_set:
                    continue
                
                # 重複チェック
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    urls.append(normalized_url)
            
            logger.info(f"この索引ページから {len([u for u in urls if index_url.split('/')[-1].split('.')[0] in u])} 件のURLを抽出")
            time.sleep(1)  # サーバーへの負荷を軽減
            
        except Exception as e:
            logger.error(f"URL抽出エラー ({index_url}): {e}")
    
    logger.info(f"合計 {len(urls)} 件のURLを抽出しました")
    return urls


def fetch_post_content(url: str) -> dict:
    """個別投稿ページからコンテンツを取得"""
    logger.info(f"コンテンツを取得: {url}")
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # エンコーディングを適切に処理
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # タイトルを取得（複数の方法を試す）
        title_elem = None
        # 方法1: h2.entry_headerを探す（実際のHTMLではentry_headerクラス）
        title_elem = soup.find('h2', class_='entry_header')
        if not title_elem:
            # 方法2: h2タグでentry_headerクラスを含むものを探す
            for h2 in soup.find_all('h2'):
                if h2.get('class') and 'entry_header' in h2.get('class'):
                    title_elem = h2
                    break
        if not title_elem:
            # 方法3: h2.entry_titleを探す（フォールバック）
            title_elem = soup.find('h2', class_='entry_title')
        if not title_elem:
            # 方法4: h1を探す
            title_elem = soup.find('h1')
        if not title_elem:
            # 方法5: titleタグを探す
            title_elem = soup.find('title')
        
        title = title_elem.get_text(strip=True) if title_elem else "タイトルなし"
        
        # 「ACIM学習ガイド」や「ACIM学習ノート」を削除（前後から）
        # ただし、（）は残す（例：Day246（神の使者:P.359、ACIM:T-01.II.05:04-05））
        title = re.sub(r'^ACIM学習(ガイド|ノート)\s*[-|]?\s*', '', title)
        title = re.sub(r'\s*[-|]?\s*ACIM学習(ガイド|ノート)$', '', title)
        title = re.sub(r'ACIM学習(ガイド|ノート)', '', title)
        title = title.replace('神の使い', '神の使者')
        title = title.strip()
        
        # コンテンツを取得（entry_bodyクラスを探す）
        content_elem = soup.find('div', class_='entry_body')
        if not content_elem:
            # フォールバック: メインコンテンツエリアを探す
            for div in soup.find_all('div'):
                if div.get('class') and 'entry_body' in div.get('class'):
                    content_elem = div
                    break
        if not content_elem:
            content_elem = soup.find('div', class_='entry') or soup.find('article') or soup.find('main')
        
        content = ""
        if content_elem:
            # 本文をそのまま取得（HTMLタグは除去するが、改行は保持）
            # <br>タグを改行に変換
            for br in content_elem.find_all('br'):
                br.replace_with('\n')
            
            # <p>タグの後に改行を追加（段落区切り）
            for p in content_elem.find_all('p'):
                if p.string:
                    p.string = p.string + '\n\n'
                else:
                    # 子要素がある場合は、最後の子要素の後に改行を追加
                    if p.contents:
                        p.append('\n\n')
            
            # テキストを取得（HTMLタグを除去、改行を保持）
            # separator='\n'で改行を保持
            content = content_elem.get_text(separator='\n', strip=False)
            
            # Tweetセクションを削除（コンテンツの最後から）
            # 「Tweet」という文字列が見つかった位置から後を削除
            tweet_pos = content.find('Tweet')
            if tweet_pos >= 0:
                content = content[:tweet_pos]
            
            # 連続する空白行を整理（最大2つの連続改行まで）
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # 先頭と末尾の空白を削除
            content = content.strip()
        
        return {
            'title': title,
            'content': content,
            'url': url
        }
        
    except Exception as e:
        logger.error(f"コンテンツ取得エラー ({url}): {e}")
        return {
            'title': "エラー",
            'content': f"コンテンツを取得できませんでした: {url}\nエラー: {e}",
            'url': url
        }


def setup_japanese_font():
    """日本語フォントを設定"""
    try:
        # TTCファイルを直接使用（reportlabはTTCファイルをサポート）
        font_paths = [
            "C:/Windows/Fonts/msgothic.ttc",  # MS ゴシック（TTC）
            "C:/Windows/Fonts/msmincho.ttc",  # MS 明朝（TTC）
            "C:/Windows/Fonts/meiryo.ttc",    # メイリオ（TTC）
            # 個別のTTFファイルも試す
            "C:/Windows/Fonts/msgothic.ttf",
            "C:/Windows/Fonts/msmincho.ttf",
            "C:/Windows/Fonts/meiryo.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # TTCファイルもTTFファイルも同じように登録
                    pdfmetrics.registerFont(TTFont('JapaneseFont', font_path))
                    logger.info(f"日本語フォントを登録しました: {font_path}")
                    return 'JapaneseFont'
                except Exception as e:
                    logger.debug(f"フォント登録失敗 ({font_path}): {e}")
                    # エラーの詳細をログに記録
                    import traceback
                    logger.debug(f"トレースバック: {traceback.format_exc()}")
                    continue
        
        logger.warning("日本語フォントが見つかりません。デフォルトフォントを使用します。")
        return 'Helvetica'
    except Exception as e:
        logger.warning(f"フォント設定エラー: {e}")
        import traceback
        logger.warning(f"トレースバック: {traceback.format_exc()}")
        return 'Helvetica'


def generate_pdf(all_posts: list[dict], output_filename: str = "神の使者365日の言葉.pdf"):
    """全投稿を1つのPDFにまとめる"""
    logger.info(f"PDFを生成中: {output_filename}")
    
    # 日本語フォントを設定
    japanese_font = setup_japanese_font()
    
    # PDFドキュメントを作成
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # スタイルを設定
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=japanese_font,
        fontSize=16,
        textColor='#000000',
        spaceAfter=12,
        spaceBefore=0,
        alignment=TA_LEFT,
        leading=20
    )
    
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['BodyText'],
        fontName=japanese_font,
        fontSize=11,
        textColor='#000000',
        spaceAfter=8,
        spaceBefore=0,
        alignment=TA_LEFT,
        leading=18  # 行間を広げる
    )
    
    url_style = ParagraphStyle(
        'CustomURL',
        parent=styles['BodyText'],
        fontName=japanese_font,
        fontSize=9,
        textColor='#666666',
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    # コンテンツを構築
    story = []
    
    # 各投稿を追加（表紙なし）
    for i, post in enumerate(all_posts, 1):
        logger.info(f"投稿 {i}/{len(all_posts)}: {post['title'][:50]}...")
        
        # タイトル
        title = post.get('title', 'タイトルなし')
        if not title or title == 'タイトルなし':
            # タイトルが取得できていない場合は、URLから推測
            url = post.get('url', '')
            match = re.search(r'blog-entry-(\d+)', url)
            if match:
                title = f"Day{int(match.group(1))}"
        
        # HTMLエスケープ
        title_escaped = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(title_escaped, title_style))
        story.append(Spacer(1, 8*mm))  # タイトルと本文の間にスペース
        
        # コンテンツ
        content = post.get('content', '')
        if content:
            # 段落に分割（2つの連続改行で区切る）
            paragraphs = content.split('\n\n')
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # 段落内の改行を<br/>タグに変換（reportlabのParagraphは<br/>を認識）
                # まず、&をエスケープ（<br/>の変換前に）
                para = para.replace('&', '&amp;')
                # 次に、改行を<br/>に変換
                para = para.replace('\n', '<br/>')
                # 最後に、<と>をエスケープ（<br/>は除外）
                # <br/>を一時的に置き換えてからエスケープ
                para = para.replace('<br/>', '___BR___')
                para = para.replace('<', '&lt;').replace('>', '&gt;')
                para = para.replace('___BR___', '<br/>')
                
                story.append(Paragraph(para, content_style))
                story.append(Spacer(1, 4*mm))  # 段落間のスペース
        else:
            story.append(Paragraph("コンテンツがありません。", content_style))
        
        # 投稿の区切り（最後の投稿以外）
        if i < len(all_posts):
            story.append(Spacer(1, 10*mm))  # 投稿間のスペース
            story.append(PageBreak())
    
    # PDFを生成
    doc.build(story)
    logger.info(f"PDFを生成しました: {output_filename}")


def main(test_mode: bool = False, test_count: int = 10):
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("365botGaryのブログを1つのPDFにまとめます")
    if test_mode:
        logger.info(f"テストモード: {test_count}件のみ処理します")
    logger.info("=" * 60)
    
    # 1. 全投稿のURLを取得
    all_urls = extract_all_post_urls()
    
    if not all_urls:
        logger.error("URLを取得できませんでした。")
        return
    
    logger.info(f"合計 {len(all_urls)} 件の投稿URLを取得しました")
    
    # 2. 各投稿のコンテンツを取得
    all_posts = []
    for i, url in enumerate(all_urls, 1):
        logger.info(f"進捗: {i}/{len(all_urls)}")
        post_data = fetch_post_content(url)
        all_posts.append(post_data)
        time.sleep(1)  # サーバーへの負荷を軽減
    
    # 2.5. Day番号でソート（Day1から順に）
    def extract_day_number(post):
        """タイトルからDay番号を抽出"""
        title = post.get('title', '')
        # Day番号を抽出（Day046、Day46などに対応）
        match = re.search(r'Day0*(\d+)', title, re.IGNORECASE)
        if match:
            day_num = int(match.group(1))
            logger.debug(f"タイトル '{title}' からDay番号 {day_num} を抽出")
            return day_num
        # Day番号が見つからない場合は、URLからエントリ番号を取得
        url = post.get('url', '')
        match = re.search(r'blog-entry-(\d+)', url)
        if match:
            logger.warning(f"タイトルからDay番号を抽出できませんでした: {title}, URL: {url}")
            return 9999  # ソートできない場合は最後に
        logger.warning(f"Day番号を抽出できませんでした: {title}, URL: {url}")
        return 9999  # ソートできない場合は最後に
    
    all_posts.sort(key=extract_day_number)
    
    # ソート結果を確認（最初の5件をログに出力）
    logger.info(f"Day番号でソートしました（Day1から順に）")
    for i, post in enumerate(all_posts[:5], 1):
        title = post.get('title', 'タイトルなし')
        day_match = re.search(r'Day0*(\d+)', title, re.IGNORECASE)
        day_num = int(day_match.group(1)) if day_match else '?'
        logger.info(f"  順序 {i}: Day{day_num} - {title[:50]}...")
    
    # テストモードの場合は、指定された開始Dayからtest_count件のみ使用
    if test_mode:
        # Day011から始まるように、Day011を探す
        start_day = 11
        start_index = None
        for i, post in enumerate(all_posts):
            title = post.get('title', '')
            day_match = re.search(r'Day0*(\d+)', title, re.IGNORECASE)
            if day_match:
                day_num = int(day_match.group(1))
                if day_num == start_day:
                    start_index = i
                    break
        
        if start_index is not None:
            all_posts = all_posts[start_index:start_index + test_count]
            logger.info(f"テストモード: Day{start_day}から{len(all_posts)}件のみ処理します")
        else:
            logger.warning(f"Day{start_day}が見つかりませんでした。Day1から{test_count}件を処理します。")
            all_posts = all_posts[:test_count]
    
    # 2.6. データをJSONファイルに保存（比較用）
    json_filename = "神の使者365日の言葉_data.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    logger.info(f"データをJSONファイルに保存しました: {json_filename}")
    
    # 3. PDFを生成（テストモードでも同じファイル名で上書き）
    output_filename = "神の使者365日の言葉.pdf"
    generate_pdf(all_posts, output_filename)
    
    logger.info("=" * 60)
    logger.info(f"完了！PDFファイル: {output_filename}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='365botGaryのブログをPDFにまとめる')
    parser.add_argument('--test', action='store_true', help='テストモード（10件のみ処理）')
    parser.add_argument('--test-count', type=int, default=10, help='テストモードで処理する件数（デフォルト: 10）')
    
    args = parser.parse_args()
    
    main(test_mode=args.test, test_count=args.test_count)

