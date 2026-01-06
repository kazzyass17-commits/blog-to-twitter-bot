"""
より柔軟な語録番号抽出のテスト
「語録」と数字を分けて検索し、全角数字を半角に変換
"""
import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# 索引ページ1を取得
index1_url = "https://ameblo.jp/pursahs-gospel/entry-11576443530.html"
response = session.get(index1_url, timeout=30)
response.encoding = response.apparent_encoding or 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# すべてのリンクを取得
all_links = soup.find_all('a', href=True)

def extract_goroku_number(text):
    """
    テキストから語録番号を抽出（柔軟なパターンマッチング）
    """
    if not text:
        return None
    
    # パターン1: 「語録」+ 全角数字（連続または分離）
    # 「語録１」「語録 １」「語録(1)」「語録１」など
    patterns = [
        r'語録[　\s]*([０-９]+)',  # 語録の後に全角数字
        r'語録[　\s]*\([　\s]*([０-９]+)[　\s]*\)',  # 語録(１)
        r'語録[　\s]*\([Logion\s]*\)[　\s]*([０-９]+)',  # 語録(Logion) １
        r'語録[　\s]*\([Logion\s]*\)[　\s]*\([　\s]*([０-９]+)[　\s]*\)',  # 語録(Logion)(１)
        r'語録[　\s]*([0-9]+)',  # 語録の後に半角数字
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1)
            # 全角数字を半角数字に変換
            if any(c in num_str for c in '０１２３４５６７８９'):
                num_str = num_str.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
            try:
                return int(num_str)
            except ValueError:
                continue
    
    return None

# entry-を含むリンクから語録番号を抽出
entry_links_with_goroku = []

for link in all_links:
    href = link.get('href', '')
    if 'entry-' not in href:
        continue
    
    # リンクテキスト
    link_text = link.get_text(strip=True)
    
    # 親要素のテキストも確認
    parent = link.parent
    parent_text = parent.get_text(strip=True) if parent else ""
    
    # 語録番号を抽出
    goroku_num = extract_goroku_number(link_text)
    if not goroku_num:
        goroku_num = extract_goroku_number(parent_text)
    
    if goroku_num:
        entry_links_with_goroku.append({
            'href': href,
            'link_text': link_text[:60],
            'parent_text': parent_text[:80],
            'goroku_num': goroku_num
        })

# 語録番号でソート
entry_links_with_goroku.sort(key=lambda x: x['goroku_num'])

print(f"語録番号が抽出できたリンク数: {len(entry_links_with_goroku)}件\n")

print("=== 抽出された語録番号（最初の20件）===")
for item in entry_links_with_goroku[:20]:
    print(f"語録{item['goroku_num']}: {item['href']}")
    print(f"  リンクテキスト: {item['link_text']}")
    print(f"  親テキスト: {item['parent_text'][:60]}")
    print()

# 語録番号のリスト
goroku_numbers = sorted([item['goroku_num'] for item in entry_links_with_goroku])
print(f"抽出された語録番号: {goroku_numbers}")




