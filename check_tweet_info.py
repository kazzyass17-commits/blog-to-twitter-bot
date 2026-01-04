"""
ツイートIDから投稿情報を確認するスクリプト
"""
import sqlite3
from database import PostDatabase

def check_tweet_info(tweet_id: str):
    """ツイートIDから投稿情報を確認"""
    db = PostDatabase()
    
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # ツイートIDで投稿履歴を検索
    cursor.execute('''
        SELECT ph.*, p.title, p.content, p.link
        FROM post_history ph
        JOIN posts p ON ph.post_id = p.id
        WHERE ph.tweet_id = ?
    ''', (tweet_id,))
    
    row = cursor.fetchone()
    
    if row:
        print("=" * 60)
        print("投稿情報")
        print("=" * 60)
        print(f"ツイートID: {row['tweet_id']}")
        print(f"投稿日時: {row['posted_at']}")
        print(f"ブログURL: {row['blog_url']}")
        print(f"Twitterハンドル: {row['twitter_handle']}")
        print(f"サイクル番号: {row['cycle_number']}")
        print(f"")
        print(f"投稿タイトル: {row['title']}")
        print(f"投稿URL: {row['link']}")
        print(f"")
        print(f"コンテンツ（最初の200文字）: {row['content'][:200] if row['content'] else 'なし'}...")
        print(f"")
        print(f"ツイートURL: https://twitter.com/{row['twitter_handle']}/status/{row['tweet_id']}")
    else:
        print(f"ツイートID {tweet_id} の投稿情報が見つかりませんでした。")
        print("データベース内の最新の投稿履歴を確認します...")
        
        cursor.execute('''
            SELECT ph.*, p.title, p.link
            FROM post_history ph
            JOIN posts p ON ph.post_id = p.id
            WHERE ph.twitter_handle = '365botGary'
            ORDER BY ph.posted_at DESC
            LIMIT 5
        ''')
        
        rows = cursor.fetchall()
        if rows:
            print("")
            print("365botGaryの最新の投稿履歴（最新5件）:")
            for r in rows:
                print(f"  ツイートID: {r['tweet_id']}, 投稿日時: {r['posted_at']}, タイトル: {r['title'][:50]}...")
        else:
            print("投稿履歴が見つかりませんでした。")
    
    conn.close()

if __name__ == "__main__":
    tweet_id = "2007267037748568194"
    check_tweet_info(tweet_id)








