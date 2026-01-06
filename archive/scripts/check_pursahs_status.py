"""
pursahsgospelアカウントの投稿状況を確認するスクリプト
"""
import sqlite3
from datetime import datetime
from config import Config

def check_pursahs_status():
    """pursahsgospelアカウントの投稿状況を確認"""
    print("=" * 60)
    print("pursahsgospelアカウントの投稿状況確認")
    print("=" * 60)
    
    # データベースの投稿履歴を確認
    db_path = "posts.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # pursahsgospelの投稿履歴を取得
    cursor.execute('''
        SELECT ph.*, p.title, p.link
        FROM post_history ph
        JOIN posts p ON ph.post_id = p.id
        WHERE ph.twitter_handle = 'pursahsgospel'
        ORDER BY ph.posted_at DESC
        LIMIT 10
    ''')
    
    rows = cursor.fetchall()
    
    print(f"\n投稿履歴: {len(rows)} 件")
    if rows:
        print("\n最新の投稿履歴:")
        for row in rows:
            print(f"  ツイートID: {row['tweet_id']}, 投稿日時: {row['posted_at']}, タイトル: {row['title'][:50]}...")
    else:
        print("  投稿履歴がありません。")
    
    # 未投稿の投稿数を確認
    cursor.execute('''
        SELECT COUNT(*) as count
        FROM posts p
        WHERE p.blog_url = ?
        AND NOT EXISTS (
            SELECT 1 FROM post_history ph
            WHERE ph.post_id = p.id
            AND ph.twitter_handle = 'pursahsgospel'
        )
    ''', (Config.BLOG_PURSAHS_URL,))
    
    unposted_count = cursor.fetchone()['count']
    print(f"\n未投稿の投稿数: {unposted_count} 件")
    
    # 認証情報の確認
    print("\n" + "=" * 60)
    print("認証情報の確認")
    print("=" * 60)
    credentials = Config.get_twitter_credentials_pursahs()
    
    print(f"API Key: {'設定済み' if credentials.get('api_key') else '未設定'}")
    print(f"API Secret: {'設定済み' if credentials.get('api_secret') else '未設定'}")
    print(f"Access Token: {'設定済み' if credentials.get('access_token') else '未設定'}")
    print(f"Access Token Secret: {'設定済み' if credentials.get('access_token_secret') else '未設定'}")
    print(f"Bearer Token: {'設定済み' if credentials.get('bearer_token') else '未設定'}")
    
    # エラーログの確認（簡易版）
    print("\n" + "=" * 60)
    print("推奨される確認事項")
    print("=" * 60)
    print("1. 接続テストを実行: python test_twitter_connection.py --account pursahs")
    print("2. 実際の投稿テストを実行: python test_post.py --account pursahs")
    print("3. ログファイルを確認: bot.log, bot_pursahs.log")
    
    conn.close()

if __name__ == "__main__":
    check_pursahs_status()

