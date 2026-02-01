"""語録111の403エラー時の単語削除をテスト"""
import re

def trim_first_word(text: str) -> str:
    # 先頭に「…」がなければ付与（既にあれば増やさない）
    has_leading_ellipsis = text.startswith("…")
    body = text[1:] if has_leading_ellipsis else text
    # 語録番号が先頭にある場合は保持し、その後の先頭1語を削る
    goroku_match = re.match(r"\s*(語録(?:\s*\([^)]+\)\s*)?[０-９0-9]+)\s*(.*)", body)
    if goroku_match:
        goroku = goroku_match.group(1)
        rest = goroku_match.group(2).lstrip()
        # 最初の単語を削除（英語・日本語両対応）
        # パターン1: 英語の単語のみ（例: "J said," -> "J"を削除して"said,"が残る）
        # パターン2: 日本語の単語（例: "Jは、" -> "Jは、"全体を削除）
        # 最初の単語を削除（英語・日本語両対応）
        # パターン1: 「Ｊは言った。」のような場合、「Ｊは」だけを削除
        # パターン2: 「J said,」のような場合、「J」だけを削除
        # パターン3: 「said,」のような場合、「said,」を削除
        
        # まず「Ｊは」または「Jは」のパターンをチェック
        if rest.startswith('Ｊは') or rest.startswith('Jは'):
            # 「Ｊは」または「Jは」を削除
            trimmed_rest = rest[2:].lstrip()
            first_word = rest[:2]
            print(f"削除された最初の単語: '{first_word}'")
        else:
            # 空白で区切られる単語を探す
            m2 = re.match(r"\s*([^\s]+)\s+(.*)", rest)
            if m2:
                first_word = m2.group(1)
                trimmed_rest = m2.group(2)
                # 1文字の英語の場合は、そのまま削除（「J」->「said,」）
                if len(first_word) == 1 and first_word.isalpha() and trimmed_rest:
                    pass
                print(f"削除された最初の単語: '{first_word}'")
            else:
                # 空白がない場合、最初の文字列を削除
                # 「said,」のような場合は、句読点までを含めて1単語として扱う
                m3 = re.match(r'^([A-Za-z]+[、，,。.]?|[^\s、，,。.]+[、，,。.]?|.)', rest)
                if m3:
                    first_word = m3.group(1)
                    trimmed_rest = rest[len(first_word):]
                    print(f"削除された最初の単語（空白なし）: '{first_word}'")
                else:
                    # それでもマッチしない場合、最初の2文字を削除（フォールバック）
                    trimmed_rest = rest[2:] if len(rest) > 2 else ""
                    print(f"パターンマッチなし、最初の2文字を削除")
        trimmed_rest = trimmed_rest.lstrip()
        if trimmed_rest:
            if not trimmed_rest.startswith("…"):
                trimmed_rest = f"…{trimmed_rest}"
            return f"{goroku}\n{trimmed_rest}"
        return goroku
    # 語録番号がない場合
    # まず「Ｊは」または「Jは」のパターンをチェック
    if body.startswith('Ｊは') or body.startswith('Jは'):
        # 「Ｊは」または「Jは」を削除
        trimmed = body[2:].lstrip()
        first_word = body[:2]
        print(f"削除された最初の単語: '{first_word}'")
    else:
        # 空白で区切られる単語を探す
        m = re.match(r"\s*([^\s]+)\s+(.*)", body)
        if m:
            first_word = m.group(1)
            trimmed = m.group(2)
            print(f"削除された最初の単語: '{first_word}'")
        else:
            # 空白がない場合、最初の文字列を削除
            m3 = re.match(r'^([A-Za-z]+[、，,。.]?|[^\s、，,。.]+[、，,。.]?|.)', body)
            if m3:
                first_word = m3.group(1)
                trimmed = body[len(first_word):]
                print(f"削除された最初の単語（空白なし）: '{first_word}'")
            else:
                trimmed = body[2:] if len(body) > 2 else ""
                print(f"パターンマッチなし、最初の2文字を削除")
    trimmed = trimmed.lstrip()
    return ("…" if not has_leading_ellipsis else "…") + trimmed if trimmed else ("…" if not has_leading_ellipsis else body)

# 語録111の実際のテキスト
original_text = '語録１１１\nＪは言った。「天と地はあなたがたの前で巻き上げられ、生きている人とともに生きている者は誰でも死を見ることがないだろう。わたしはこう言わなかったか。『誰でも自分自身を見出す者にとっては、世界は価値がない』と」'

print("=" * 60)
print("語録111の403エラー時の単語削除テスト")
print("=" * 60)

print(f"\n元のテキスト:")
print(original_text[:100] + "...")

print("\n" + "-" * 60)
print("1回目の403エラー（最初の1単語削除）:")
print("-" * 60)
result1 = trim_first_word(original_text)
print(f"\n結果:")
print(result1[:150] + "...")

print("\n" + "-" * 60)
print("2回目の403エラー（さらに1単語削除）:")
print("-" * 60)
result2 = trim_first_word(result1)
print(f"\n結果:")
print(result2[:150] + "...")

print("\n" + "=" * 60)
print("期待される結果:")
print("=" * 60)
print("1回目: 語録１１１\n…言った。「天と地は...」")
print("2回目: 語録１１１\n…「天と地は...」")
