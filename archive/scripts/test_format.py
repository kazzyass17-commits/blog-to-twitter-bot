"""フォーマットのテスト"""
from twitter_poster import TwitterPoster
from config import Config

# 365botGaryのテスト
poster365 = TwitterPoster(Config.get_twitter_credentials_365bot())
title365 = "ACIM学習ガイド Day196（神の使い:P.318、ACIM:T-06.I.13-14:01）"
content365 = "同じ章で、彼はさらに次のように言っています。ー磔刑のメッセージは完璧に明晰である。愛だけを教えなさい。なぜなら、あなたは愛であるから、もし礫刑にべつの解釈をするなら、あなたはそれを本来、意図された平和への呼びかけではなくて、攻撃の武器に使うことになる。"
link365 = "http://notesofacim.blog.fc2.com/blog-entry-326.html"

result365 = poster365.format_blog_post(title365, content365, link365)
print("=== 365botGary ===")
print(f"元のタイトル: {title365}")
print(f"フォーマット後: {result365}")
print(f"文字数: {len(result365)}")
print(f"リンク含む文字数: {len(result365) + 1 + len(link365)}")
print(f"（実際のツイート形式: {result365} {link365}）")
print()

# pursahsgospelのテスト
posterPursahs = TwitterPoster(Config.get_twitter_credentials_pursahs())
titlePursahs = "語録１１０ | Pursah's Gospelのブログ"
contentPursahs = "Ｊは言った。「世界を見出し、豊かになった者に、この世界を捨てさせなさい」 J said, \"Let one who has found the world, and has become wealthy, renounce the world.\" この言葉は、私たちを引き止めているのはこの世界における自分たちの執着である、という考えのさらに別な表現である。"
linkPursahs = "https://ameblo.jp/pursahs-gospel/entry-11577211919.html"

resultPursahs = posterPursahs.format_blog_post(titlePursahs, contentPursahs, linkPursahs)
print("=== pursahsgospel ===")
print(f"元のタイトル: {titlePursahs}")
print(f"フォーマット後: {resultPursahs}")
print(f"文字数: {len(resultPursahs)}")
print(f"リンク含む文字数: {len(resultPursahs) + 1 + len(linkPursahs)}")
print(f"（実際のツイート形式: {resultPursahs} {linkPursahs}）")




