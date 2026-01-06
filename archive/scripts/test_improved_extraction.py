"""
改善された語録番号抽出ロジックのテスト
"""
from index_extractor import IndexExtractor

extractor = IndexExtractor()
urls = extractor.extract_pursahsgospel_urls()

print(f"抽出されたURL数: {len(urls)}件\n")

# 最初の20件を表示
print("=== 最初の20件 ===")
for i, url_data in enumerate(urls[:20], 1):
    print(f"{i}. {url_data['link']}")
    print(f"   タイトル: {url_data['title'][:80]}")
    print()




