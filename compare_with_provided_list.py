"""
抽出されたURLの実際のタイトルから語録番号を抽出して、提供されたリストと照合
"""
from index_extractor import IndexExtractor
import requests
from bs4 import BeautifulSoup
import re
import time

# 提供された語録リストから番号を抽出
provided_goroku_numbers = set()
goroku_text = """語録１
語録２
語録３
語録４
語録５
語録６
語録８
語録９
語録１１
語録１３
語録１７
語録１８
語録２０
語録２２
語録２３
語録２４
語録２６
語録２８
語録３１
語録３２
語録３４
語録３６
語録３７
語録４０
語録４１
語録４２
語録４５
語録４７
語録４８
語録４９
語録５１
語録５２
語録５４
語録５６
語録５７
語録５８
語録５９
語録６１
語録６２
語録６３
語録６６
語録６７
語録７０
語録７２
語録７５
語録７６
語録７９
語録８０
語録８５
語録８６
語録８７
語録８８
語録８９
語録９０
語録９１
語録９２
語録９４
語録９５
語録９６
語録９７
語録９９
語録１００
語録１０３
語録１０６
語録１０８
語録１０９
語録１１０
語録１１１
語録１１３"""

for line in goroku_text.strip().split('\n'):
    match = re.search(r'語録([０-９]+)', line)
    if match:
        zenkaku = match.group(1)
        hankaku = zenkaku.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        provided_goroku_numbers.add(int(hankaku))

print(f"提供されたリストの語録数: {len(provided_goroku_numbers)}件")
print(f"語録番号: {sorted(provided_goroku_numbers)}\n")

# URL抽出を実行
print("URL抽出中...")
extractor = IndexExtractor()
urls = extractor.extract_pursahsgospel_urls()
print(f"抽出されたURL数: {len(urls)}件\n")

# 実際のページタイトルから語録番号を抽出
print("実際のページタイトルから語録番号を抽出中...")
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

extracted_goroku_numbers = set()
url_to_goroku = {}  # URL -> 語録番号のマッピング

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
        
        # 語録番号を探す（全角数字を3桁まで検出して半角に変換）
        goroku_num = None
        if title:
            # パターン1: 「語録」+ 全角数字（1-3桁）
            match = re.search(r'語録[　\s\(\)]*(?:\([Logion\s]*\))?[　\s]*([０-９]{1,3})', title)
            if match:
                zenkaku = match.group(1)
                goroku_num = int(zenkaku.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
            else:
                # パターン2: 「語録」+ 半角数字（1-3桁）
                match = re.search(r'語録[　\s\(\)]*(?:\([Logion\s]*\))?[　\s]*([0-9]{1,3})', title)
                if match:
                    goroku_num = int(match.group(1))
        
        if goroku_num:
            extracted_goroku_numbers.add(goroku_num)
            url_to_goroku[url] = goroku_num
        
        if i % 10 == 0:
            print(f"  処理中... {i}/{len(urls)}")
        
        time.sleep(0.5)  # サーバーに負荷をかけないように
        
    except Exception as e:
        print(f"  エラー ({url}): {e}")
        continue

print(f"\n抽出された語録数: {len(extracted_goroku_numbers)}件")
print(f"語録番号: {sorted(extracted_goroku_numbers)}\n")

# 比較
missing = provided_goroku_numbers - extracted_goroku_numbers
extra = extracted_goroku_numbers - provided_goroku_numbers
common = provided_goroku_numbers & extracted_goroku_numbers

print(f"=== 比較結果 ===")
print(f"一致した語録: {len(common)}件 / {len(provided_goroku_numbers)}件 ({len(common)/len(provided_goroku_numbers)*100:.1f}%)")
print(f"提供リストにあって抽出にない語録: {sorted(missing) if missing else 'なし'} ({len(missing)}件)")
print(f"抽出にあって提供リストにない語録: {sorted(extra) if extra else 'なし'} ({len(extra)}件)")

if missing:
    print(f"\n見つからなかった語録の詳細:")
    for num in sorted(missing):
        print(f"  語録{num}")

