"""
投稿データベース管理モジュール
SQLiteを使用して投稿データと投稿履歴を管理
"""
import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostDatabase:
    """投稿データベース管理クラス"""
    
    def __init__(self, db_path: str = "posts.db"):
        """
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """データベーステーブルを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 投稿テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blog_url TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                link TEXT NOT NULL UNIQUE,
                published_date TEXT,
                author TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 投稿履歴テーブル（どの投稿をいつ投稿したか）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                blog_url TEXT NOT NULL,
                twitter_handle TEXT NOT NULL,
                tweet_id TEXT,
                posted_at TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        ''')
        
        # サイクル管理テーブル（1巡の管理）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blog_url TEXT NOT NULL,
                twitter_handle TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                UNIQUE(blog_url, twitter_handle, cycle_number)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"データベースを初期化しました: {self.db_path}")
    
    def add_post(self, blog_url: str, post_data: Dict[str, str]) -> Optional[int]:
        """
        投稿をデータベースに追加（重複チェック付き）
        
        Args:
            blog_url: ブログURL
            post_data: 投稿データ（title, content, link, published_date, author）
        
        Returns:
            投稿ID、または既に存在する場合はNone
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 既存チェック
            cursor.execute('SELECT id FROM posts WHERE link = ?', (post_data.get('link'),))
            existing = cursor.fetchone()
            if existing:
                logger.debug(f"既存の投稿です（スキップ）: {post_data.get('link')}")
                return existing[0]
            
            # 新規追加
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO posts (blog_url, title, content, link, published_date, author, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                blog_url,
                post_data.get('title', ''),
                post_data.get('content', ''),
                post_data.get('link', ''),
                post_data.get('published_date', ''),
                post_data.get('author', ''),
                now,
                now
            ))
            
            post_id = cursor.lastrowid
            conn.commit()
            logger.info(f"投稿を追加しました: ID={post_id}, {post_data.get('title', '')[:50]}")
            return post_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"投稿の追加に失敗（重複）: {post_data.get('link')}")
            return None
        finally:
            conn.close()
    
    def get_all_posts(self, blog_url: str) -> List[Dict]:
        """
        ブログの全投稿を取得
        
        Args:
            blog_url: ブログURL
        
        Returns:
            投稿データのリスト
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM posts WHERE blog_url = ? ORDER BY published_date DESC, id DESC', (blog_url,))
        rows = cursor.fetchall()
        
        posts = [dict(row) for row in rows]
        conn.close()
        return posts
    
    def get_current_cycle_number(self, blog_url: str, twitter_handle: str) -> int:
        """
        現在のサイクル番号を取得
        
        Args:
            blog_url: ブログURL
            twitter_handle: Twitterハンドル
        
        Returns:
            現在のサイクル番号（未開始の場合は0）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT MAX(cycle_number) FROM cycles 
            WHERE blog_url = ? AND twitter_handle = ?
        ''', (blog_url, twitter_handle))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result[0] is not None else 0
    
    def start_new_cycle(self, blog_url: str, twitter_handle: str) -> int:
        """
        新しいサイクルを開始
        
        Args:
            blog_url: ブログURL
            twitter_handle: Twitterハンドル
        
        Returns:
            新しいサイクル番号
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cycle_number = self.get_current_cycle_number(blog_url, twitter_handle) + 1
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO cycles (blog_url, twitter_handle, cycle_number, started_at)
            VALUES (?, ?, ?, ?)
        ''', (blog_url, twitter_handle, cycle_number, now))
        
        conn.commit()
        conn.close()
        logger.info(f"新しいサイクルを開始: {blog_url} -> @{twitter_handle}, サイクル#{cycle_number}")
        return cycle_number
    
    def get_unposted_posts_in_cycle(
        self, 
        blog_url: str, 
        twitter_handle: str, 
        cycle_number: int
    ) -> List[Dict]:
        """
        現在のサイクルで未投稿の投稿を取得
        
        Args:
            blog_url: ブログURL
            twitter_handle: Twitterハンドル
            cycle_number: サイクル番号
        
        Returns:
            未投稿の投稿データのリスト
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # このサイクルで既に投稿された投稿IDを取得
        cursor.execute('''
            SELECT DISTINCT post_id FROM post_history 
            WHERE blog_url = ? AND twitter_handle = ? AND cycle_number = ?
        ''', (blog_url, twitter_handle, cycle_number))
        
        posted_ids = [row[0] for row in cursor.fetchall()]
        
        # 未投稿の投稿を取得
        if posted_ids:
            placeholders = ','.join('?' * len(posted_ids))
            cursor.execute(f'''
                SELECT * FROM posts 
                WHERE blog_url = ? AND id NOT IN ({placeholders})
                ORDER BY published_date DESC, id DESC
            ''', [blog_url] + posted_ids)
        else:
            cursor.execute('''
                SELECT * FROM posts 
                WHERE blog_url = ?
                ORDER BY published_date DESC, id DESC
            ''', (blog_url,))
        
        rows = cursor.fetchall()
        posts = [dict(row) for row in rows]
        conn.close()
        
        return posts
    
    def record_post(self, post_id: int, blog_url: str, twitter_handle: str, 
                   cycle_number: int, tweet_id: Optional[str] = None) -> bool:
        """
        投稿履歴を記録
        
        Args:
            post_id: 投稿ID
            blog_url: ブログURL
            twitter_handle: Twitterハンドル
            cycle_number: サイクル番号
            tweet_id: ツイートID（オプション）
        
        Returns:
            成功した場合True
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO post_history (post_id, blog_url, twitter_handle, tweet_id, posted_at, cycle_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (post_id, blog_url, twitter_handle, tweet_id, now, cycle_number))
            
            conn.commit()
            logger.info(f"投稿履歴を記録: post_id={post_id}, @{twitter_handle}, cycle#{cycle_number}")
            return True
        except Exception as e:
            logger.error(f"投稿履歴の記録エラー: {e}")
            return False
        finally:
            conn.close()
    
    def check_cycle_complete(self, blog_url: str, twitter_handle: str, cycle_number: int) -> bool:
        """
        サイクルが完了したかチェック（全ての投稿が投稿済みか）
        
        Args:
            blog_url: ブログURL
            twitter_handle: Twitterハンドル
            cycle_number: サイクル番号
        
        Returns:
            サイクルが完了している場合True
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 全投稿数
        cursor.execute('SELECT COUNT(*) FROM posts WHERE blog_url = ?', (blog_url,))
        total_posts = cursor.fetchone()[0]
        
        # 投稿済み数
        cursor.execute('''
            SELECT COUNT(DISTINCT post_id) FROM post_history 
            WHERE blog_url = ? AND twitter_handle = ? AND cycle_number = ?
        ''', (blog_url, twitter_handle, cycle_number))
        
        posted_count = cursor.fetchone()[0]
        conn.close()
        
        is_complete = total_posts > 0 and posted_count >= total_posts
        
        if is_complete:
            logger.info(f"サイクル完了: {blog_url} -> @{twitter_handle}, サイクル#{cycle_number} ({posted_count}/{total_posts})")
            
            # サイクルの完了時刻を記録
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute('''
                UPDATE cycles SET completed_at = ? 
                WHERE blog_url = ? AND twitter_handle = ? AND cycle_number = ?
            ''', (now, blog_url, twitter_handle, cycle_number))
            conn.commit()
            conn.close()
        
        return is_complete
    
    def get_random_unposted_post(
        self, 
        blog_url: str, 
        twitter_handle: str,
        filter_day_only: bool = True
    ) -> Optional[Dict]:
        """
        未投稿の投稿をランダムに1件取得
        
        Args:
            blog_url: ブログURL
            twitter_handle: Twitterハンドル
            filter_day_only: Trueの場合、Day001～Day365の投稿のみを対象とする
        
        Returns:
            投稿データ、または未投稿がない場合None
        """
        import random
        import re
        
        cycle_number = self.get_current_cycle_number(blog_url, twitter_handle)
        
        # サイクルが未開始または完了している場合は新しいサイクルを開始
        if cycle_number == 0:
            cycle_number = self.start_new_cycle(blog_url, twitter_handle)
        else:
            # 現在のサイクルが完了しているかチェック
            if self.check_cycle_complete(blog_url, twitter_handle, cycle_number):
                cycle_number = self.start_new_cycle(blog_url, twitter_handle)
        
        # 未投稿の投稿を取得
        unposted_posts = self.get_unposted_posts_in_cycle(blog_url, twitter_handle, cycle_number)
        
        if not unposted_posts:
            logger.warning(f"未投稿の投稿がありません: {blog_url} -> @{twitter_handle}")
            return None
        
        # Day001～Day365の投稿のみをフィルタリング（365botGaryの場合）
        if filter_day_only and 'notesofacim.blog.fc2.com' in blog_url:
            # Day001～Day365のパターンに一致する投稿のみを選択
            day_pattern = re.compile(r'Day(\d{3})')
            filtered_posts = []
            for post in unposted_posts:
                title = post.get('title', '')
                match = day_pattern.search(title)
                if match:
                    day_num = int(match.group(1))
                    if 1 <= day_num <= 365:
                        filtered_posts.append(post)
            
            if filtered_posts:
                unposted_posts = filtered_posts
            else:
                logger.warning(f"Day001～Day365の未投稿がありません: {blog_url} -> @{twitter_handle}")
                return None
        
        # ランダムに1件選択
        selected_post = random.choice(unposted_posts)
        logger.info(f"投稿を選択: {selected_post.get('title', '')[:50]} (ID: {selected_post['id']})")
        return selected_post


