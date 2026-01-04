"""
過去の投稿履歴を確認するスクリプト
"""
import sqlite3
from datetime import datetime
import sys
import io

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_post_history():
    """過去の投稿履歴を確認"""
    try:
        conn = sqlite3.connect('posts.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 最新10件の投稿履歴を取得
        cursor.execute('''
            SELECT ph.tweet_id, ph.blog_url, ph.twitter_handle, ph.posted_at, ph.cycle_number,
                   p.title
            FROM post_history ph
            LEFT JOIN posts p ON ph.post_id = p.id
            ORDER BY ph.posted_at DESC
            LIMIT 10
        ''')
        
        rows = cursor.fetchall()
        
        print("=" * 60)
        print("過去の投稿履歴（最新10件）")
        print("=" * 60)
        print(f"確認時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if rows:
            for i, row in enumerate(rows, 1):
                print(f"[{i}]")
                print(f"  ツイートID: {row['tweet_id']}")
                print(f"  ブログURL: {row['blog_url']}")
                print(f"  Twitterハンドル: {row['twitter_handle']}")
                print(f"  投稿日時: {row['posted_at']}")
                print(f"  サイクル番号: {row['cycle_number']}")
                if row['title']:
                    print(f"  タイトル: {row['title'][:50]}...")
                print()
        else:
            print("投稿履歴がありません。")
        
        # アカウント別の統計
        print("=" * 60)
        print("アカウント別の投稿統計")
        print("=" * 60)
        
        cursor.execute('''
            SELECT twitter_handle, COUNT(*) as count, MAX(posted_at) as last_post
            FROM post_history
            GROUP BY twitter_handle
        ''')
        
        stats = cursor.fetchall()
        for stat in stats:
            print(f"{stat['twitter_handle']}:")
            print(f"  投稿回数: {stat['count']} 回")
            if stat['last_post']:
                print(f"  最終投稿: {stat['last_post']}")
            print()
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    check_post_history()







