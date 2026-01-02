import requests
from bs4 import BeautifulSoup

url = 'http://notesofacim.blog.fc2.com/blog-entry-89.html'
r = requests.get(url)
r.encoding = r.apparent_encoding or 'utf-8'
soup = BeautifulSoup(r.text, 'html.parser')

print("=== h2タグの検索 ===")
h2_tags = soup.find_all('h2')
print(f'Found h2 tags: {len(h2_tags)}')
for i, h2 in enumerate(h2_tags[:5]):
    print(f'h2[{i}]: class={h2.get("class")}, text={h2.get_text(strip=True)[:80]}')

print("\n=== entry_titleクラスの検索 ===")
entry_title = soup.find('h2', class_='entry_title')
print(f'entry_title (class_): {entry_title}')

print("\n=== クラス名で検索 ===")
for h2 in soup.find_all('h2'):
    classes = h2.get('class', [])
    if 'entry_title' in classes:
        print(f'Found entry_title: {h2.get_text(strip=True)}')

print("\n=== entry_bodyクラスの検索 ===")
entry_body = soup.find('div', class_='entry_body')
print(f'entry_body found: {entry_body is not None}')
if entry_body:
    text = entry_body.get_text()
    print(f'entry_body text length: {len(text)}')
    # Tweetセクションを探す
    if 'Tweet' in text:
        tweet_pos = text.find('Tweet')
        print(f'Tweet found at position: {tweet_pos}')
        print(f'Text before Tweet: {text[:tweet_pos][-100:]}')
        print(f'Text after Tweet: {text[tweet_pos:tweet_pos+200]}')

