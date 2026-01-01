"""
X (Twitter) 投稿モジュール
"""
import tweepy
import logging
from typing import Dict, Optional
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterPoster:
    """X (Twitter) に投稿するクラス"""
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Args:
            credentials: Twitter API認証情報の辞書
        """
        self.credentials = credentials
        self.client = self._create_client()
    
    def _create_client(self) -> tweepy.Client:
        """Tweepyクライアントを作成"""
        try:
            # Twitter API v2を使用
            client = tweepy.Client(
                bearer_token=self.credentials.get('bearer_token'),
                consumer_key=self.credentials.get('api_key'),
                consumer_secret=self.credentials.get('api_secret'),
                access_token=self.credentials.get('access_token'),
                access_token_secret=self.credentials.get('access_token_secret'),
                wait_on_rate_limit=True
            )
            return client
        except Exception as e:
            logger.error(f"Twitterクライアント作成エラー: {e}")
            raise
    
    def post_tweet(self, text: str) -> Optional[Dict]:
        """
        ツイートを投稿
        
        Args:
            text: 投稿するテキスト（最大280文字）
        
        Returns:
            投稿結果の辞書、またはNone（エラー時）
        """
        try:
            # 文字数制限チェック
            if len(text) > Config.MAX_POST_LENGTH:
                text = text[:Config.MAX_POST_LENGTH - 3] + "..."
            
            logger.info(f"ツイート投稿中: {text[:50]}...")
            
            # ツイート投稿
            response = self.client.create_tweet(text=text)
            
            if response and response.data:
                tweet_id = response.data.get('id')
                logger.info(f"ツイート投稿成功: ID={tweet_id}")
                return {
                    'id': tweet_id,
                    'text': text,
                    'success': True
                }
            else:
                logger.error("ツイート投稿失敗: レスポンスが不正")
                return None
                
        except tweepy.TooManyRequests:
            logger.error("レート制限に達しました。しばらく待ってから再試行してください。")
            return None
        except tweepy.Unauthorized:
            logger.error("認証エラー: API認証情報を確認してください。")
            return None
        except Exception as e:
            logger.error(f"ツイート投稿エラー: {e}")
            return None
    
    def post_tweet_with_link(self, text: str, link: str) -> Optional[Dict]:
        """
        リンク付きツイートを投稿
        
        Args:
            text: 投稿するテキスト
            link: リンクURL
        
        Returns:
            投稿結果の辞書、またはNone（エラー時）
        """
        # リンクを追加（23文字としてカウント）
        max_text_length = Config.MAX_POST_LENGTH - 24  # リンク + スペース
        
        if len(text) > max_text_length:
            text = text[:max_text_length - 3] + "..."
        
        tweet_text = f"{text}\n{link}"
        
        return self.post_tweet(tweet_text)
    
    def format_blog_post(self, title: str, content: str, link: str) -> str:
        """
        ブログ投稿をツイート用にフォーマット
        
        Args:
            title: ブログタイトル
            content: ブログコンテンツ（抜粋）
            link: ブログリンク
        
        Returns:
            フォーマットされたツイートテキスト
        """
        # タイトルとコンテンツからツイートを作成
        # リンクは23文字としてカウント
        available_length = Config.MAX_POST_LENGTH - 24  # リンク + 改行
        
        # タイトルを優先
        if len(title) <= available_length:
            tweet_text = title
        else:
            # タイトルが長すぎる場合は短縮
            tweet_text = title[:available_length - 3] + "..."
        
        # コンテンツを追加できる場合は追加
        remaining_length = available_length - len(tweet_text) - 1  # スペース分
        
        if remaining_length > 20 and content:
            content_preview = content[:remaining_length - 3]
            tweet_text = f"{title}\n{content_preview}..."
        else:
            tweet_text = title
        
        return tweet_text


