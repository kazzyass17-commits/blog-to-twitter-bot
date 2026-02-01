"""blog_urlの値を確認"""
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('posts.db')
cur = conn.cursor()

# post_historyのblog_urlを確認
cur.execute('''
    SELECT DISTINCT blog_url FROM post_history 
    WHERE twitter_handle = '365botGary'
''')
history_urls = [row[0] for row in cur.fetchall()]

# postsのblog_urlを確認
cur.execute('SELECT DISTINCT blog_url FROM posts LIMIT 10')
post_urls = [row[0] for row in cur.fetchall()]

print("="*70)
print("blog_urlの確認")
print("="*70)

print(f"\npost_historyのblog_url（365botGary）:")
for url in history_urls:
    print(f"  {url}")

print(f"\npostsのblog_url（最初の10件）:")
for url in post_urls[:10]:
    print(f"  {url}")

# 365bot関連のpostsを確認
cur.execute('SELECT blog_url, COUNT(*) FROM posts GROUP BY blog_url')
all_urls = cur.fetchall()
print(f"\n全blog_urlと投稿数:")
for url, count in all_urls:
    print(f"  {url}: {count}件")

conn.close()
