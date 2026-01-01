"""
欠けている語録1と語録32を探す
"""
from index_extractor import IndexExtractor
import requests
from bs4 import BeautifulSoup
import re
import time

# URL抽出を実行
extractor = IndexExtractor()
urls = extractor.extract_pursahsgospel_urls()

print(f"抽出されたURL数: {len(urls)}件\n")

# すべてのURLから語録番号を抽出
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print("すべてのURLから語録番号を抽出中...")
url_to_goroku = {}
no_goroku_urls = []  # 語録番号が見つからなかったURL

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
        
        # 語録番号を探す
        goroku_num = None
        if title:
            # 全角数字
            match = re.search(r'語録([０-９]+)', title)
            if match:
                zenkaku = match.group(1)
                goroku_num = int(zenkaku.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
            else:
                # 半角数字
                match = re.search(r'語録(\d+)', title)
                if match:
                    goroku_num = int(match.group(1))
        
        if goroku_num:
            url_to_goroku[url] = goroku_num
            if goroku_num == 1 or goroku_num == 32:
                print(f"見つかった！ 語録{goroku_num}: {url}")
                print(f"  タイトル: {title[:80]}")
        else:
            no_goroku_urls.append((url, title))
        
        if i % 10 == 0:
            print(f"  処理中... {i}/{len(urls)}")
        
        time.sleep(0.3)  # サーバーに負荷をかけないように
        
    except Exception as e:
        print(f"  エラー ({url}): {e}")
        no_goroku_urls.append((url, None))
        continue

print(f"\n語録番号が見つからなかったURL数: {len(no_goroku_urls)}件")
if no_goroku_urls:
    print("\n語録番号が見つからなかったURL（最初の10件）:")
    for url, title in no_goroku_urls[:10]:
        print(f"  {url}")
        print(f"    タイトル: {title[:80] if title else 'N/A'}")
        print()

# 抽出された語録番号のリスト
extracted_numbers = sorted(url_to_goroku.values())
print(f"\n抽出された語録番号（{len(extracted_numbers)}件）:")
print(extracted_numbers)

