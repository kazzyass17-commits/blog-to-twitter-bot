"""
pursahsgospelの索引ページを分析
"""
from bs4 import BeautifulSoup
import re

def analyze_index(filename: str):
    """索引ページを分析"""
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # すべてのリンクを探す
    all_links = soup.find_all('a', href=True)
    entry_links = []
    
    for link in all_links:
        href = link.get('href', '')
        if 'entry-' in href:
            entry_links.append((href, link.get_text(strip=True)))
    
    print(f"\n{filename}:")
    print(f"entry-を含むリンク数: {len(entry_links)}")
    print(f"\n最初の10件:")
    for i, (href, text) in enumerate(entry_links[:10], 1):
        print(f"  {i}. {href[:80]} - {text[:50]}")
    
    print(f"\n最後の10件:")
    for i, (href, text) in enumerate(entry_links[-10:], len(entry_links)-9):
        print(f"  {i}. {href[:80]} - {text[:50]}")
    
    # 語録番号を含むリンクを探す
    goroku_links = []
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if re.search(r'語録\d+', text) and 'entry-' in href:
            goroku_links.append((href, text))
    
    print(f"\n語録番号を含むリンク数: {len(goroku_links)}")
    if goroku_links:
        print(f"\n最初の5件:")
        for i, (href, text) in enumerate(goroku_links[:5], 1):
            print(f"  {i}. {href[:80]} - {text[:50]}")

if __name__ == "__main__":
    analyze_index("pursahs_index1.html")
    analyze_index("pursahs_index2.html")





