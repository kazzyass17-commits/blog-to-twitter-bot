"""成功した投稿を確認"""
import sqlite3

db_path = "posts.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ツイートIDから投稿を検索
tweet_id = "2007267037748568194"

cursor.execute('''
    SELECT ph.posted_at, ph.tweet_id, ph.post_id, ph.twitter_handle, p.link, p.title
    FROM post_history ph
    JOIN posts p ON ph.post_id = p.id
    WHERE ph.tweet_id = ?
''', (tweet_id,))

row = cursor.fetchone()

if row:
    posted_at = row[0]
    tweet_id_found = row[1]
    post_id = row[2]
    twitter_handle = row[3]
    link = row[4]
    title = row[5]
    
    print("=" * 60)
    print("成功した投稿を確認")
    print("=" * 60)
    print(f"ツイートID: {tweet_id_found}")
    print(f"投稿日時: {posted_at}")
    print(f"アカウント: @{twitter_handle}")
    print(f"投稿ID: {post_id}")
    print(f"URL: {link}")
    print(f"URL長さ: {len(link)}文字")
    print(f"タイトル: {title}")
    print(f"\nこの投稿はURLを含んでいました: {link}")
    print(f"URLの長さは問題ありませんでした（{len(link)}文字）")
else:
    print(f"ツイートID {tweet_id} が見つかりませんでした")
    print("\nデータベース内のすべての投稿履歴を確認します...")
    cursor.execute('''
        SELECT ph.posted_at, ph.tweet_id, ph.post_id, ph.twitter_handle, p.link
        FROM post_history ph
        JOIN posts p ON ph.post_id = p.id
        ORDER BY ph.posted_at DESC
    ''')
    rows = cursor.fetchall()
    print(f"データベース内の投稿履歴: {len(rows)}件")
    for i, r in enumerate(rows[:5], 1):
        print(f"{i}. ツイートID: {r[1]}, URL: {r[4]}")

conn.close()







