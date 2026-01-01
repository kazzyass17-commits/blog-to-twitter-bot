"""
抽出されたURLの実際のタイトルを取得して語録番号を確認
"""
from index_extractor import IndexExtractor
import requests
from bs4 import BeautifulSoup
import re

extractor = IndexExtractor()
urls = extractor.extract_pursahsgospel_urls()

print(f"抽出されたURL数: {len(urls)}件\n")

# 最初の10件の実際のタイトルを取得
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print("=== 最初の10件の実際のタイトル ===")
for i, url_data in enumerate(urls[:10], 1):
    url = url_data['link']
    extracted_title = url_data['title']
    
    try:
        response = session.get(url, timeout=30)
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # タイトルを取得（複数の方法で試す）
        title = None
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
        
        # 語録番号を探す
        goroku_num = None
        if title:
            # 全角数字
            match = re.search(r'語録([０-９]+)', title)
            if match:
                zenkaku = match.group(1)
                goroku_num = zenkaku.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
            else:
                # 半角数字
                match = re.search(r'語録(\d+)', title)
                if match:
                    goroku_num = match.group(1)
        
        print(f"{i}. URL: {url}")
        print(f"   抽出時タイトル: {extracted_title[:60]}")
        print(f"   実際のタイトル: {title[:80] if title else 'N/A'}")
        print(f"   語録番号: {goroku_num if goroku_num else '見つからず'}")
        print()
        
    except Exception as e:
        print(f"{i}. URL: {url}")
        print(f"   エラー: {e}")
        print()

