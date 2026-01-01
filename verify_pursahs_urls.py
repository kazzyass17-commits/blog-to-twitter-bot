"""
pursahsgospelのURL抽出結果を提供されたリストと照合するスクリプト
"""
import re
from index_extractor import IndexExtractor

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

# 全角数字を半角数字に変換して抽出
for line in goroku_text.strip().split('\n'):
    match = re.search(r'語録([０-９]+)', line)
    if match:
        # 全角数字を半角数字に変換
        zenkaku = match.group(1)
        hankaku = zenkaku.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        provided_goroku_numbers.add(int(hankaku))

print(f"提供されたリストの語録数: {len(provided_goroku_numbers)}件")
print(f"語録番号: {sorted(provided_goroku_numbers)}")

# URL抽出を実行
extractor = IndexExtractor()
urls = extractor.extract_pursahsgospel_urls()

print(f"\n抽出されたURL数: {len(urls)}件")

# 抽出されたURLのタイトルから語録番号を抽出
extracted_goroku_numbers = set()
for url_data in urls:
    title = url_data.get('title', '')
    # タイトルから語録番号を抽出
    match = re.search(r'語録([０-９]+)', title)
    if match:
        zenkaku = match.group(1)
        hankaku = zenkaku.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        extracted_goroku_numbers.add(int(hankaku))
    else:
        # 半角数字も試す
        match = re.search(r'語録(\d+)', title)
        if match:
            extracted_goroku_numbers.add(int(match.group(1)))

print(f"抽出されたタイトルから見つかった語録数: {len(extracted_goroku_numbers)}件")
print(f"語録番号: {sorted(extracted_goroku_numbers)}")

# 比較
missing = provided_goroku_numbers - extracted_goroku_numbers
extra = extracted_goroku_numbers - provided_goroku_numbers

print(f"\n=== 比較結果 ===")
print(f"提供リストにあって抽出にない語録: {sorted(missing) if missing else 'なし'} ({len(missing)}件)")
print(f"抽出にあって提供リストにない語録: {sorted(extra) if extra else 'なし'} ({len(extra)}件)")

# 一致率
common = provided_goroku_numbers & extracted_goroku_numbers
print(f"\n一致した語録: {len(common)}件 / {len(provided_goroku_numbers)}件 ({len(common)/len(provided_goroku_numbers)*100:.1f}%)")

# 抽出されたURLのタイトルを表示
print(f"\n=== 抽出されたURLのタイトル（最初の20件）===")
for i, url_data in enumerate(urls[:20], 1):
    title = url_data.get('title', '')
    link = url_data.get('link', '')
    print(f"{i}. {title[:60]} - {link[:60]}")


