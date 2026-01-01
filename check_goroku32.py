"""語録32のURL抽出を確認"""
from index_extractor import IndexExtractor
import requests
from bs4 import BeautifulSoup
import re

extractor = IndexExtractor()
urls = extractor.extract_pursahsgospel_urls()

print(f"抽出されたURL数: {len(urls)}件\n")

# 実際のページタイトルから語録番号を抽出
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

extracted_goroku_numbers = set()
goroku_32_urls = []

for i, url_data in enumerate(urls, 1):
    url = url_data['link']
    
    try:
        response = session.get(url, timeout=30)
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # タイトルを取得
        title = None
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        # 語録番号を抽出
        goroku_num = None
        if title:
            # 全角数字（1-3桁）
            match = re.search(r'語録([０-９]{1,3})', title)
            if match:
                zenkaku = match.group(1)
                goroku_num = int(zenkaku.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
        
        if goroku_num:
            extracted_goroku_numbers.add(goroku_num)
            if goroku_num == 32:
                goroku_32_urls.append(url)
                print(f"✓ 語録32を発見: {url}")
                print(f"  タイトル: {title[:80]}")
        
        if i % 10 == 0:
            print(f"  処理中... {i}/{len(urls)}")
        
    except Exception as e:
        print(f"  エラー ({url}): {e}")
        continue

print(f"\n抽出された語録数: {len(extracted_goroku_numbers)}件")
print(f"語録番号: {sorted(extracted_goroku_numbers)}")

if 32 in extracted_goroku_numbers:
    print(f"\n[OK] 語録32が正しく抽出されました！")
    print(f"語録32のURL数: {len(goroku_32_urls)}件")
    for url in goroku_32_urls:
        print(f"  - {url}")
else:
    print(f"\n[NG] 語録32が見つかりませんでした")

