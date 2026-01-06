"""
索引ページのHTML構造を確認して、語録番号がどのようにマークアップされているか確認
"""
from bs4 import BeautifulSoup
import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# 索引1のページを取得
index1_url = "https://ameblo.jp/pursahs-gospel/entry-11576443530.html"
response = session.get(index1_url, timeout=30)
response.encoding = response.apparent_encoding or 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# entry-を含むリンクを探す
all_links = soup.find_all('a', href=True)
entry_links = []

for link in all_links:
    href = link.get('href', '')
    if 'entry-' in href:
        text = link.get_text(strip=True)
        # 親要素も確認
        parent = link.parent
        parent_text = parent.get_text(strip=True) if parent else ""
        
        entry_links.append({
            'href': href,
            'text': text,
            'parent_text': parent_text[:100] if parent_text else "",
        })

print(f"entry-を含むリンク数: {len(entry_links)}\n")

# 最初の30件を表示
print("=== 最初の30件 ===")
for i, link_data in enumerate(entry_links[:30], 1):
    print(f"{i}. HREF: {link_data['href'][:70]}")
    print(f"   TEXT: {link_data['text'][:80]}")
    print(f"   PARENT: {link_data['parent_text'][:80]}")
    print()

# 語録番号を含むリンクを探す
print("=== 語録番号を含むリンク ===")
for link_data in entry_links:
    text = link_data['text']
    parent = link_data['parent_text']
    
    # 全角数字
    if re.search(r'語録[０-９]+', text) or re.search(r'語録[０-９]+', parent):
        print(f"HREF: {link_data['href'][:70]}")
        print(f"TEXT: {text[:80]}")
        print(f"PARENT: {parent[:80]}")
        print()





