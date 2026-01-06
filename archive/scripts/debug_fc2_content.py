"""FC2ブログのコンテンツ取得をデバッグ"""
from bs4 import BeautifulSoup
import requests

url = "http://notesofacim.blog.fc2.com/blog-entry-305.html"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

response = session.get(url, timeout=30)
response.encoding = response.apparent_encoding or 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# タイトルを探す
title_elem = soup.find(['h1', 'h2', 'h3'], class_=lambda x: x and 'title' in x.lower())
if not title_elem:
    title_elem = soup.find('title')
print(f"Title: {title_elem.get_text(strip=True) if title_elem else 'Not found'}")

# コンテンツを探す（複数の方法で試す）
print("\n=== Content search ===")

# 方法1: entry_body
content_elem = soup.find('div', id=lambda x: x and 'entry_body' in x.lower())
if content_elem:
    print(f"Found by id=entry_body: {len(content_elem.get_text(strip=True))} chars")
else:
    print("Not found by id=entry_body")

# 方法2: classにentryを含むdiv
content_elems = soup.find_all('div', class_=lambda x: x and 'entry' in x.lower())
print(f"Found {len(content_elems)} divs with 'entry' in class")
for i, elem in enumerate(content_elems[:5], 1):
    text = elem.get_text(strip=True)
    print(f"  {i}. Class: {elem.get('class')}, Length: {len(text)} chars, Preview: {text[:100]}")

# 方法3: 記事本文を探す（main content area）
main_content = soup.find('div', class_=lambda x: x and ('main' in x.lower() or 'content' in x.lower()))
if main_content:
    print(f"\nFound main content: {len(main_content.get_text(strip=True))} chars")

# 方法4: 記事本文を探す（articleタグ）
article = soup.find('article')
if article:
    print(f"Found article tag: {len(article.get_text(strip=True))} chars")

# 方法5: すべてのdivを確認（最も長いテキストを持つdivを探す）
all_divs = soup.find_all('div')
divs_with_text = [(div, len(div.get_text(strip=True))) for div in all_divs if div.get_text(strip=True)]
divs_with_text.sort(key=lambda x: x[1], reverse=True)
print(f"\nTop 5 divs by text length:")
for i, (div, length) in enumerate(divs_with_text[:5], 1):
    classes = div.get('class', [])
    div_id = div.get('id', '')
    preview = div.get_text(strip=True)[:100]
    print(f"  {i}. Length: {length}, ID: {div_id}, Classes: {classes}, Preview: {preview}")




