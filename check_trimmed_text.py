"""403エラー時のテキスト削除を確認"""
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
        m2 = re.match(r"\s*([^\s]+)\s+(.*)", rest)
        if m2:
            first_word = m2.group(1)
            trimmed_rest = m2.group(2)
            print(f"削除された最初の単語: '{first_word}'")
            print(f"削除後の残り: '{trimmed_rest[:50]}...'")
            trimmed_rest = trimmed_rest.lstrip()
            if trimmed_rest:
                if not trimmed_rest.startswith("…"):
                    trimmed_rest = f"…{trimmed_rest}"
                return f"{goroku}\n{trimmed_rest}"
        else:
            trimmed_rest = rest[2:] if len(rest) > 2 else ""
            print(f"パターンマッチなし、最初の2文字を削除")
            trimmed_rest = trimmed_rest.lstrip()
            if trimmed_rest:
                if not trimmed_rest.startswith("…"):
                    trimmed_rest = f"…{trimmed_rest}"
                return f"{goroku}\n{trimmed_rest}"
        return goroku
    m = re.match(r"\s*([^\s]+)\s+(.*)", body)
    if m:
        first_word = m.group(1)
        trimmed = m.group(2)
        print(f"削除された最初の単語: '{first_word}'")
        print(f"削除後の残り: '{trimmed[:50]}...'")
    else:
        trimmed = body[2:] if len(body) > 2 else ""
        print(f"パターンマッチなし、最初の2文字を削除")
    trimmed = trimmed.lstrip()
    return ("…" if not has_leading_ellipsis else "…") + trimmed if trimmed else ("…" if not has_leading_ellipsis else body)

# テスト: ログから見た実際のテキスト
# 元のテキスト（推測）: "語録１１１\nsaid, \"Let one who has found the world, and..."
# 削除後: "語録１１１\n…said, \"The Heav"

test_text = "語録１１１\nsaid, \"Let one who has found the world, and has become rich, renounce the world.\""
print("元のテキスト:")
print(test_text)
print("\n削除処理:")
result = trim_first_word(test_text)
print(f"\n結果:")
print(result)
