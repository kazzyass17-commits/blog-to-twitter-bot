"""URLの文字数カウントを確認"""
from config import Config

url1 = "http://notesofacim.blog.fc2.com/blog-entry-326.html"
url2 = "https://ameblo.jp/pursahs-gospel/entry-11577211919.html"

print(f"MAX_POST_LENGTH: {Config.MAX_POST_LENGTH}")
print(f"\n実際のURLの長さ:")
print(f"  URL1: {len(url1)} 文字 - {url1}")
print(f"  URL2: {len(url2)} 文字 - {url2}")

print(f"\nTwitterでのURLのカウント: 23文字（実際の長さに関わらず）")
print(f"\n利用可能なテキスト長:")
print(f"  URL(23) + 改行(1) = 24文字")
print(f"  利用可能: {Config.MAX_POST_LENGTH - 23 - 1} 文字")

