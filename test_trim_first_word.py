"""trim_first_word関数のテスト"""
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
        # まず空白で区切られる単語を探す
        m2 = re.match(r"\s*([^\s]+)\s+(.*)", rest)
        if m2:
            first_word = m2.group(1)
            trimmed_rest = m2.group(2)
            # 「Jは、」のような場合、句読点までを1単語として扱う
            # ただし、「J said,」のような場合は「J」だけを削除
            if len(first_word) == 1 and first_word.isalpha() and trimmed_rest:
                # 1文字の英語の場合は、そのまま削除（「J」->「said,」）
                pass
            elif 'は、' in first_word or 'は,' in first_word or first_word.endswith('、') or first_word.endswith(','):
                # 「Jは、」のような場合は、そのまま削除
                pass
            print(f"削除された最初の単語: '{first_word}'")
        else:
            # 空白がない場合、最初の文字列を削除
            # 「Jは、」のような場合は、句読点までを含めて1単語として扱う
            # パターン1: 英語の1文字+日本語の文字+句読点（例: "Jは、"）
            # パターン2: 英語の単語+句読点（例: "said,"）
            # パターン3: その他の文字列
            m3 = re.match(r'^([A-Za-z][^\s、，,。.]*[、，,。.]?|[A-Za-z]+|[^\s、，,。.]+[、，,。.]?|.)', rest)
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
    m = re.match(r"\s*([^\s]+)\s+(.*)", body)
    if m:
        first_word = m.group(1)
        trimmed = m.group(2)
        print(f"削除された最初の単語: '{first_word}'")
    else:
        # 空白がない場合、最初の文字列を削除
        # 「Jは、」のような場合は、句読点までを含めて1単語として扱う
        m3 = re.match(r'^([A-Za-z][^\s、，,。.]*[、，,。.]?|[A-Za-z]+|[^\s、，,。.]+[、，,。.]?|.)', body)
        if m3:
            first_word = m3.group(1)
            trimmed = body[len(first_word):]
            print(f"削除された最初の単語（空白なし）: '{first_word}'")
        else:
            trimmed = body[2:] if len(body) > 2 else ""
            print(f"パターンマッチなし、最初の2文字を削除")
    trimmed = trimmed.lstrip()
    return ("…" if not has_leading_ellipsis else "…") + trimmed if trimmed else ("…" if not has_leading_ellipsis else body)

# テストケース
test_cases = [
    '語録１１１\nJ said, "Let one who has found the world, and has become rich, renounce the world."',
    '語録１１１\nJは、「天と地はあなたがたの前で巻き上げられ、生きている人とともに生きている者は誰でも死を見ることがないだろう。',
    '語録１１１\nsaid, "Let one who has found the world, and has become rich, renounce the world."',
]

print("テスト開始:")
print("=" * 60)
for i, test_text in enumerate(test_cases, 1):
    print(f"\nテストケース {i}:")
    print(f"元のテキスト: {test_text[:80]}...")
    print("削除処理:")
    result = trim_first_word(test_text)
    print(f"結果: {result[:80]}...")
    print("-" * 60)
