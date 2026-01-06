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
    
    def __init__(self, credentials: Dict[str, str], account_key: str = None, account_name: str = None):
        """
        Args:
            credentials: Twitter API認証情報の辞書
            account_key: アカウントキー（'365bot' または 'pursahs'）
            account_name: アカウント名（表示用）
        """
        self.credentials = credentials
        self.account_key = account_key
        self.account_name = account_name
        self.client = self._create_client()
    
    def _create_client(self):
        """Tweepyクライアントを作成（API v2を使用）"""
        try:
            # Twitter API v2を使用（無料プランではAPI v1.1のupdate_statusにアクセスできないため）
            client = tweepy.Client(
                bearer_token=self.credentials.get('bearer_token'),
                consumer_key=self.credentials.get('api_key'),
                consumer_secret=self.credentials.get('api_secret'),
                access_token=self.credentials.get('access_token'),
                access_token_secret=self.credentials.get('access_token_secret'),
                wait_on_rate_limit=False  # レート制限時はエラーを返す（手動で処理）
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
            
            # ツイート投稿（API v2）
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
            
            # レート制限の情報を記録
            try:
                from rate_limit_checker import record_rate_limit_reason
                from datetime import datetime, timedelta
                
                # レスポンスヘッダーからレート制限情報を取得
                rate_limit_limit = None
                rate_limit_remaining = None
                reset_time = None
                
                if hasattr(e, 'response') and e.response is not None:
                    headers = e.response.headers if hasattr(e.response, 'headers') else {}
                    rate_limit_limit = int(headers.get('x-rate-limit-limit', 0)) if headers.get('x-rate-limit-limit') else None
                    rate_limit_remaining = int(headers.get('x-rate-limit-remaining', 0)) if headers.get('x-rate-limit-remaining') else None
                    reset_timestamp = headers.get('x-rate-limit-reset')
                    if reset_timestamp:
                        # x-rate-limit-resetはUTCタイムスタンプ（Unixエポック秒）
                        # UTCとして明示的に解釈
                        from datetime import timezone
                        reset_time = datetime.fromtimestamp(int(reset_timestamp), tz=timezone.utc)
                    else:
                        # reset_timeが取得できない場合は、エラーログに詳細を記録
                        logger.error(f"警告: 429エラーが発生しましたが、x-rate-limit-resetヘッダーが取得できませんでした。")
                        logger.error(f"  レスポンスヘッダー: {dict(headers) if headers else 'なし'}")
                        logger.error(f"  レスポンスオブジェクト: {e.response}")
                else:
                    # レスポンスオブジェクトが存在しない場合
                    logger.error(f"警告: 429エラーが発生しましたが、レスポンスオブジェクトが存在しません。")
                    logger.error(f"  エラーオブジェクト: {e}")
                
                # アカウントキーとアカウント名を使用（設定されていない場合はデフォルト）
                account_key = self.account_key or '365bot'
                account_name = self.account_name or '365botGary'
                
                # 待機終了時刻を計算（reset_timeのみ使用、取得できない場合は不明）
                if reset_time:
                    wait_until = reset_time
                else:
                    # reset_timeが取得できない場合は不明
                    wait_until = None
                
                record_rate_limit_reason(
                    account_key=account_key,
                    account_name=account_name,
                    api_endpoint='POST /2/tweets',
                    error_message=str(e),
                    reset_time=reset_time,
                    wait_until=wait_until,
                    rate_limit_limit=rate_limit_limit,
                    rate_limit_remaining=rate_limit_remaining
                )
            except Exception as record_error:
                logger.warning(f"レート制限情報の記録に失敗: {record_error}")
            
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
            
            # 403エラーの情報を記録
            try:
                from rate_limit_checker import record_rate_limit_reason
                from datetime import datetime, timedelta
                
                # レスポンスヘッダーからレート制限情報を取得（403でもヘッダーは返ってくる可能性がある）
                reset_time = None
                if hasattr(e, 'response') and e.response is not None:
                    headers = e.response.headers if hasattr(e.response, 'headers') else {}
                    reset_timestamp = headers.get('x-rate-limit-reset')
                    if reset_timestamp:
                        # x-rate-limit-resetはUTCタイムスタンプ（Unixエポック秒）
                        # UTCとして明示的に解釈
                        from datetime import timezone
                        reset_time = datetime.fromtimestamp(int(reset_timestamp), tz=timezone.utc)
                
                account_key = self.account_key or '365bot'
                account_name = self.account_name or '365botGary'
                
                # 待機終了時刻を計算（reset_timeのみ使用、取得できない場合は不明）
                if reset_time:
                    wait_until = reset_time
                else:
                    # reset_timeが取得できない場合は不明
                    wait_until = None
                
                error_details = str(e)
                if hasattr(e, 'response') and e.response is not None:
                    if hasattr(e.response, 'text'):
                        error_details = e.response.text[:500]
                
                record_rate_limit_reason(
                    account_key=account_key,
                    account_name=account_name,
                    api_endpoint='POST /2/tweets',
                    error_message=f"403 Forbidden: {error_details}",
                    reset_time=None,
                    wait_until=wait_until,
                    rate_limit_limit=None,
                    rate_limit_remaining=None
                )
            except Exception as record_error:
                logger.warning(f"403エラー情報の記録に失敗: {record_error}")
            
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"レスポンス本文: {e.response.text[:500]}")
            logger.error("\n考えられる原因:")
            logger.error("1. アプリの権限が「Read and write」に設定されていない")
            logger.error("2. 権限変更後にAccess Tokenを再生成していない")
            logger.error("3. アプリがX側の承認待ち（Pending approval）")
            logger.error("4. アプリが停止（SUSPENDED）されている")
            logger.error("5. 文字数制限を超えている可能性（188文字以内に調整済み）")
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
        # リンクと#ACIMを追加
        # 403エラーを回避するため、188文字（URL含む）に制限
        # TwitterはURLを23文字としてカウントするが、実際のAPI送信時は実際のURL長が使用される
        # そのため、最終的なテキスト（URL含む）が188文字以内になるようにする
        # 最終的な形式: text + 改行(1) + URL(実際の長さ) + 改行(1) + "#ACIM"(5) = 188文字以内
        hashtag = "\n#ACIM"  # 改行(1) + "#ACIM"(5) = 6文字
        
        # 最終的なテキスト: text + 改行(1) + URL(実際の長さ) + 改行(1) + "#ACIM"(5) = 188文字以内
        # そのため、text + 1 + len(link) + 1 + 5 <= 188
        # text <= 188 - 1 - len(link) - 1 - 5 = 181 - len(link)
        max_text_length = 188 - 1 - len(link) - 1 - len("#ACIM")  # 改行(1) + URL + 改行(1) + #ACIM
        
        if len(text) > max_text_length:
            text = text[:max_text_length - 3] + "..."
        
        tweet_text = f"{text}\n{link}{hashtag}"
        
        # 最終チェック: 188文字を超えないように（念のため）
        if len(tweet_text) > 188:
            # テキストをさらに切り詰める
            available_length = max_text_length - 3  # "..."を考慮
            if available_length > 0:
                text = text[:available_length] + "..."
                tweet_text = f"{text}\n{link}{hashtag}"
        
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
        
        # pursahsgospelの場合: コンテンツの先頭が「語録XX」で始まる場合、その後に改行を追加
        if 'ameblo.jp/pursahs-gospel' in link or 'ameba.jp/profile/general/pursahs-gospel' in link:
            # コンテンツの先頭が「語録XX」で始まる場合、その後に改行を追加
            match = re.match(r'^(語録\d+)', cleaned_content)
            if match:
                goroku_part = match.group(1)
                rest_content = cleaned_content[len(goroku_part):].lstrip()
                # 改行がなければ追加
                if not rest_content.startswith('\n'):
                    cleaned_content = f"{goroku_part}\n{rest_content}"
        
        # フォーマット: タイトル + "\n" + 本文 + "\n" + URL + "\n" + "#ACIM"
        # 最終的な形式: tweet_text + 改行(1) + URL(実際の長さ) + 改行(1) + "#ACIM"(5) = 188文字以内
        # pursahsgospelの場合: タイトルを含めない（本文のみ）
        # 365botGaryの場合: タイトルを含める
        max_total_length = 188  # Twitterカウント（URL含む）
        hashtag = "\n#ACIM"  # 改行(1) + "#ACIM"(5) = 6文字
        
        # pursahsgospelの場合: タイトルを含めない（本文のみ）
        is_pursahs = 'ameblo.jp/pursahs-gospel' in link or 'ameba.jp/profile/general/pursahs-gospel' in link
        is_365bot = 'notesofacim.blog.fc2.com' in link
        
        # 実際のURL長を使用（post_tweet_with_linkと同じロジック）
        # 最終的な形式: tweet_text + 改行(1) + URL(実際の長さ) + 改行(1) + "#ACIM"(5) = 188文字以内
        # そのため、tweet_text + 1 + len(link) + 1 + 5 <= 188
        # tweet_text <= 188 - 1 - len(link) - 1 - 5 = 181 - len(link)
        max_tweet_text_length = max_total_length - 1 - len(link) - 1 - len("#ACIM")  # 改行(1) + URL + 改行(1) + #ACIM
        
        if is_pursahs:
            # pursahsgospel: タイトルなし、本文のみ
            # tweet_text = content_preview
            # そのため、content_preview <= max_tweet_text_length
            max_text_length = max_tweet_text_length
            title_with_newline = ""
            title_length = 0
        elif is_365bot:
            # 365botGary: タイトルあり
            # tweet_text = normalized_title + "\n" + content_preview
            # そのため、len(normalized_title) + 1 + len(content_preview) <= max_tweet_text_length
            title_with_newline = f"{normalized_title}\n"
            title_length = len(title_with_newline)  # タイトル + 改行
            max_text_length = max_tweet_text_length - title_length  # タイトル改行を引く
        else:
            # その他の場合（通常は発生しない）
            title_with_newline = f"{normalized_title}\n"
            title_length = len(title_with_newline)
            max_text_length = max_tweet_text_length - title_length
        
        # 本文を切り詰める
        if len(cleaned_content) <= max_text_length:
            # 全部引用
            content_preview = cleaned_content
        else:
            # 本文を切り詰める（途中で切る。句読点で区切らない）
            content_preview = cleaned_content[:max_text_length]
        
        # タイトル + 改行 + 本文の形式で結合（pursahsgospelの場合はタイトルなし）
        if is_pursahs:
            tweet_text = content_preview
        else:
            tweet_text = f"{normalized_title}\n{content_preview}"
        
        # 最終チェック: max_tweet_text_lengthを超えないように（念のため）
        if len(tweet_text) > max_tweet_text_length:
            if is_pursahs:
                # pursahsgospel: 本文のみなので、本文を切り詰める
                content_preview = cleaned_content[:max_tweet_text_length]
                tweet_text = content_preview
            else:
                # 365botGary: タイトルは含める必要があるので、本文をさらに切り詰める
                available_for_content = max_tweet_text_length - title_length
                if available_for_content > 0:
                    # 本文を切り詰める（途中で切る。句読点で区切らない）
                    content_preview = cleaned_content[:available_for_content]
                    tweet_text = f"{normalized_title}\n{content_preview}"
                else:
                    # タイトルが長すぎる場合は、タイトルのみ（これは通常発生しない）
                    tweet_text = normalized_title
        
        return tweet_text


