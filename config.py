"""
設定管理モジュール
"""
import os
from dotenv import load_dotenv
from typing import Dict, Optional

# .envファイルを読み込み
load_dotenv()


class Config:
    """アプリケーション設定クラス"""
    
    # Twitter API認証情報（デフォルトアカウント）
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_TOKEN_SECRET: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    # 365botGaryアカウント用（別アカウントの場合）
    TWITTER_365BOT_API_KEY: Optional[str] = os.getenv("TWITTER_365BOT_API_KEY")
    TWITTER_365BOT_API_SECRET: Optional[str] = os.getenv("TWITTER_365BOT_API_SECRET")
    TWITTER_365BOT_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_365BOT_ACCESS_TOKEN")
    TWITTER_365BOT_ACCESS_TOKEN_SECRET: Optional[str] = os.getenv("TWITTER_365BOT_ACCESS_TOKEN_SECRET")
    
    # pursahsgospelアカウント用（別アカウントの場合）
    TWITTER_PURSAHS_API_KEY: Optional[str] = os.getenv("TWITTER_PURSAHS_API_KEY")
    TWITTER_PURSAHS_API_SECRET: Optional[str] = os.getenv("TWITTER_PURSAHS_API_SECRET")
    TWITTER_PURSAHS_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_PURSAHS_ACCESS_TOKEN")
    TWITTER_PURSAHS_ACCESS_TOKEN_SECRET: Optional[str] = os.getenv("TWITTER_PURSAHS_ACCESS_TOKEN_SECRET")
    TWITTER_PURSAHS_BEARER_TOKEN: Optional[str] = os.getenv("TWITTER_PURSAHS_BEARER_TOKEN")
    
    # ブログURL
    BLOG_365BOT_URL: str = os.getenv("BLOG_365BOT_URL", "http://notesofacim.blog.fc2.com/")
    TWITTER_365BOT_HANDLE: str = os.getenv("TWITTER_365BOT_HANDLE", "365botGary")
    
    BLOG_PURSAHS_URL: str = os.getenv("BLOG_PURSAHS_URL", "https://www.ameba.jp/profile/general/pursahs-gospel/")
    TWITTER_PURSAHS_HANDLE: str = os.getenv("TWITTER_PURSAHS_HANDLE", "pursahsgospel")
    
    # 投稿設定
    POST_INTERVAL_HOURS: int = int(os.getenv("POST_INTERVAL_HOURS", "24"))
    MAX_POST_LENGTH: int = int(os.getenv("MAX_POST_LENGTH", "280"))
    
    @classmethod
    def get_twitter_credentials_365bot(cls) -> Dict[str, str]:
        """365botGaryアカウント用のTwitter認証情報を取得"""
        if cls.TWITTER_365BOT_API_KEY:
            return {
                "api_key": cls.TWITTER_365BOT_API_KEY,
                "api_secret": cls.TWITTER_365BOT_API_SECRET or "",
                "access_token": cls.TWITTER_365BOT_ACCESS_TOKEN or "",
                "access_token_secret": cls.TWITTER_365BOT_ACCESS_TOKEN_SECRET or "",
                "bearer_token": cls.TWITTER_365BOT_BEARER_TOKEN or cls.TWITTER_BEARER_TOKEN or "",
            }
        # デフォルト認証情報を使用
        return {
            "api_key": cls.TWITTER_API_KEY,
            "api_secret": cls.TWITTER_API_SECRET,
            "access_token": cls.TWITTER_ACCESS_TOKEN,
            "access_token_secret": cls.TWITTER_ACCESS_TOKEN_SECRET,
            "bearer_token": cls.TWITTER_BEARER_TOKEN or "",
        }
    
    @classmethod
    def get_twitter_credentials_pursahs(cls) -> Dict[str, str]:
        """pursahsgospelアカウント用のTwitter認証情報を取得"""
        if cls.TWITTER_PURSAHS_API_KEY:
            return {
                "api_key": cls.TWITTER_PURSAHS_API_KEY,
                "api_secret": cls.TWITTER_PURSAHS_API_SECRET or "",
                "access_token": cls.TWITTER_PURSAHS_ACCESS_TOKEN or "",
                "access_token_secret": cls.TWITTER_PURSAHS_ACCESS_TOKEN_SECRET or "",
                "bearer_token": cls.TWITTER_PURSAHS_BEARER_TOKEN or cls.TWITTER_BEARER_TOKEN or "",
            }
        # デフォルト認証情報を使用
        return {
            "api_key": cls.TWITTER_API_KEY,
            "api_secret": cls.TWITTER_API_SECRET,
            "access_token": cls.TWITTER_ACCESS_TOKEN,
            "access_token_secret": cls.TWITTER_ACCESS_TOKEN_SECRET,
            "bearer_token": cls.TWITTER_BEARER_TOKEN or "",
        }


