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
                
        except tweepy.TooManyRequests as e:
            logger.error("レート制限に達しました。しばらく待ってから再試行してください。")
            logger.error(f"詳細: {e}")
            return None
        except tweepy.Unauthorized as e:
            logger.error("認証エラー: API認証情報を確認してください。")
            logger.error(f"詳細: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"レスポンス本文: {e.response.text[:500]}")
            return None
        except tweepy.Forbidden as e:
            logger.error("アクセス拒否 (403 Forbidden): 書き込み権限がありません。")
            logger.error(f"詳細: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"レスポンス本文: {e.response.text[:500]}")
            logger.error("\n考えられる原因:")
            logger.error("1. アプリの権限が「Read and write」に設定されていない")
            logger.error("2. 権限変更後にAccess Tokenを再生成していない")
            logger.error("3. アプリがX側の承認待ち（Pending approval）")
            logger.error("4. アプリが停止（SUSPENDED）されている")
            return None
        except Exception as e:
            logger.error(f"ツイート投稿エラー: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"レスポンス本文: {e.response.text[:500]}")
            import traceback
            logger.error(f"トレースバック:\n{traceback.format_exc()}")
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
            フォーマットされたツイートテキスト（リンクは含まない）
        """
        import re
        
        # タイトルの正規化
        normalized_title = title
        
        # 365botGaryの場合: 「ACIM学習ガイド 」や「ACIM学習ノート 」を削除、「神の使い」を「神の使者」に修正
        if 'notesofacim.blog.fc2.com' in link:
            # 「ACIM学習ガイド 」または「ACIM学習ノート 」を削除
            normalized_title = re.sub(r'^ACIM学習(ガイド|ノート)\s+', '', normalized_title)
            # 「神の使い」を「神の使者」に修正
            normalized_title = normalized_title.replace('神の使い', '神の使者')
        
        # pursahsgospelの場合: 「 | Pursah's Gospelのブログ」を削除
        elif 'ameblo.jp/pursahs-gospel' in link or 'ameba.jp/profile/general/pursahs-gospel' in link:
            # 「 | Pursah's Gospelのブログ」を削除
            normalized_title = re.sub(r'\s*\|\s*Pursah\'?s Gospelのブログ\s*$', '', normalized_title)
        
        # コンテンツから不要な文字を除去（ナビゲーション要素など）
        cleaned_content = content.strip()
        
        # pursahsgospelの場合: コンテンツ内のタイトルパターンを除去
        if 'ameblo.jp/pursahs-gospel' in link or 'ameba.jp/profile/general/pursahs-gospel' in link:
            # 「ブログトップリスト画像リスト語録XX | Pursah's Gospelのブログ 語録XX」などのパターンを除去
            cleaned_content = re.sub(r'ブログトップ.*?語録\d+\s*\|\s*Pursah\'?s Gospelのブログ\s*語録\d+', '', cleaned_content, flags=re.DOTALL)
            # 「語録XX | Pursah's Gospelのブログ 語録XX」のパターンを除去
            cleaned_content = re.sub(r'語録\d+\s*\|\s*Pursah\'?s Gospelのブログ\s*語録\d+', '', cleaned_content, flags=re.DOTALL)
            # コンテンツの先頭の「語録XX | Pursah's Gospelのブログ 語録XX」を除去
            cleaned_content = re.sub(r'^語録\d+\s*\|\s*Pursah\'?s Gospelのブログ\s*語録\d+', '', cleaned_content, flags=re.MULTILINE)
            # 残っている「ブログトップリスト画像リスト語録XX」のパターンを除去
            cleaned_content = re.sub(r'ブログトップ.*?語録\d+', '', cleaned_content, flags=re.DOTALL)
            # コンテンツの先頭に残っている「語録XX」のみのパターンを除去（重複した語録番号）
            cleaned_content = re.sub(r'^語録\d+\s*語録\d+', '', cleaned_content, flags=re.MULTILINE)
        
        cleaned_content = cleaned_content.strip()
        
        # フォーマット: タイトル + " " + 本文 + "\n" + URL
        # URLは23文字としてカウント、改行1つで1文字、スペース1つで1文字
        max_text_length = Config.MAX_POST_LENGTH - 23 - 1  # URL(23) + 改行(1)
        
        # タイトル + スペース + 本文 + "\n" + URL の形式で構築
        # まず、タイトル + スペースの長さを計算
        title_with_space = normalized_title + " "
        available_for_content = max_text_length - len(title_with_space)
        
        # 本文が利用可能な長さに収まる場合
        if len(cleaned_content) <= available_for_content:
            # 全部引用
            tweet_text = title_with_space + cleaned_content
        else:
            # 本文を切り詰める
            content_preview = cleaned_content[:available_for_content]
            # 最後の文字が途中で切れないように調整（単語境界で切る）
            if available_for_content > 0:
                # 最後の50文字以内に句読点があればそこで切る
                last_part = content_preview[-50:] if len(content_preview) > 50 else content_preview
                for punct in ['。', '.', '、', ',', '！', '!', '？', '?', '\n']:
                    if punct in last_part:
                        content_preview = content_preview[:content_preview.rfind(punct) + 1]
                        break
            
            tweet_text = title_with_space + content_preview
        
        # 最終チェック: 280文字を超えないように（念のため）
        if len(tweet_text) > max_text_length:
            tweet_text = tweet_text[:max_text_length]
        
        return tweet_text


