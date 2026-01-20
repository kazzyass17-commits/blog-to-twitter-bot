"""
X (Twitter) 投稿モジュール
"""
import tweepy
import logging
from typing import Dict, Optional
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _sanitize_x_headers(headers: dict) -> Dict[str, str]:
    """
    返ってきたレスポンスヘッダーから、調査に必要なものだけを抽出する。
    Set-Cookie 等の不要/巨大/機微なものは保存しない。
    """
    if not headers:
        return {}
    keep = [
        "x-transaction-id",
        "x-access-level",
        "x-rate-limit-limit",
        "x-rate-limit-remaining",
        "x-rate-limit-reset",
        "x-app-limit-24hour-limit",
        "x-app-limit-24hour-remaining",
        "x-app-limit-24hour-reset",
        "x-user-limit-24hour-limit",
        "x-user-limit-24hour-remaining",
        "x-user-limit-24hour-reset",
        "api-version",
        "cf-ray",
        "CF-RAY",
        "Date",
        "Server",
        "Content-Type",
    ]
    out: Dict[str, str] = {}
    for k in keep:
        v = headers.get(k)
        if v is not None:
            out[k] = str(v)
    return out

def _extract_response_details(exc: Exception) -> Dict[str, object]:
    """
    Tweepy例外からレスポンス情報を可能な範囲で抽出する。
    """
    resp = getattr(exc, "response", None)
    headers = None
    status_code = None
    text = None
    if resp is not None:
        headers = getattr(resp, "headers", None)
        status_code = getattr(resp, "status_code", None)
        text = getattr(resp, "text", None)
    headers_s = _sanitize_x_headers(dict(headers) if headers else {})
    transaction_id = headers_s.get("x-transaction-id")
    return {
        "status_code": status_code,
        "headers": headers_s,
        "transaction_id": transaction_id,
        "response_text": (text[:500] if isinstance(text, str) else None),
    }

def _looks_like_length_error(message: str) -> bool:
    """
    文字数超過/本文が長すぎる系のエラー文言をざっくり判定。
    ※403/400でも発生し得る。ユーザー要望により「文字数由来なら待機しない」判定に使用。
    """
    if not message:
        return False
    m = message.lower()
    patterns = [
        "too long",
        "tweet needs to be a bit shorter",
        "text is too long",
        "exceeds",
        "character limit",
        "over 280",
        "too many characters",
    ]
    return any(p in m for p in patterns)


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
            # TweepyのResponseは通常ヘッダーを露出しないため、内部requestをラップして直近ヘッダーを保持する
            try:
                original_request = getattr(client, "request", None)
                if callable(original_request):
                    def _wrapped_request(method, route, params=None, json=None, user_auth=False):  # type: ignore[no-redef]
                        resp = original_request(method, route, params=params, json=json, user_auth=user_auth)
                        try:
                            client._last_response_headers = dict(getattr(resp, "headers", {}) or {})
                        except Exception:
                            client._last_response_headers = {}
                        return resp
                    client.request = _wrapped_request  # type: ignore[assignment]
            except Exception:
                # 取得できない環境/バージョンでも投稿自体は継続
                pass
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
                headers_s = {}
                # 成功時もヘッダー（必要なものだけ）をログ出力し、結果に含める
                try:
                    raw_headers = getattr(self.client, "_last_response_headers", None) or {}
                    headers_s = _sanitize_x_headers(raw_headers if isinstance(raw_headers, dict) else {})
                    if headers_s:
                        logger.info(f"レスポンスヘッダー(抜粋): {headers_s}")
                except Exception:
                    headers_s = {}
                return {
                    'id': tweet_id,
                    'text': text,
                    'success': True,
                    'headers': headers_s,
                }
            else:
                logger.error("ツイート投稿失敗: レスポンスが不正")
                return {
                    "success": False,
                    "status": None,
                    "reason": "invalid_response",
                    "error_message": "invalid_response",
                    "transaction_id": None,
                    "headers": {},
                }
                
        except tweepy.TooManyRequests as e:
            # 429は簡潔に記録・返却（冗長な定型メッセージを削除）
            det = _extract_response_details(e)
            headers_s = det.get("headers") or {}
            transaction_id = det.get("transaction_id")
            err_msg = det.get("response_text") or str(e)
            reason = "length_error" if _looks_like_length_error(err_msg) else "429 Too Many Requests"
            try:
                from rate_limit_checker import record_rate_limit_reason
                record_rate_limit_reason(
                    account_key=self.account_key or '365bot',
                    account_name=self.account_name or '365botGary',
                    api_endpoint='POST /2/tweets',
                    error_message=str(e),
                    reason=reason,
                    reset_time=None,
                    wait_until=None,
                    rate_limit_limit=None,
                    rate_limit_remaining=None
                )
            except Exception:
                pass
            return {
                "success": False,
                "status": det.get("status_code") or 429,
                "reason": reason,
                "error_message": err_msg,
                "transaction_id": transaction_id,
                "headers": headers_s,
            }
        except tweepy.Unauthorized as e:
            logger.error("認証エラー: API認証情報を確認してください。")
            logger.error(f"詳細: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"レスポンス本文: {e.response.text[:500]}")
            det = _extract_response_details(e)
            return {
                "success": False,
                "status": det.get("status_code") or 401,
                "reason": "401 Unauthorized",
                "error_message": det.get("response_text") or str(e),
                "transaction_id": det.get("transaction_id"),
                "headers": det.get("headers") or {},
            }
        except tweepy.Forbidden as e:
            # 403: 定型原因メッセージは出さず、ヘッダーとtxnのみ記録して返す
            det = _extract_response_details(e)
            headers_s = det.get("headers") or {}
            transaction_id = det.get("transaction_id")
            err_msg = det.get("response_text") or str(e)
            try:
                from rate_limit_checker import record_rate_limit_reason
                record_rate_limit_reason(
                    account_key=self.account_key or '365bot',
                    account_name=self.account_name or '365botGary',
                    api_endpoint='POST /2/tweets',
                    error_message=f"403 Forbidden: {err_msg}",
                    reset_time=None,
                    wait_until=None,
                    reason='403 Forbidden',
                    rate_limit_limit=None,
                    rate_limit_remaining=None
                )
            except Exception:
                pass
            return {
                "success": False,
                "status": det.get("status_code") or 403,
                "reason": ("length_error" if _looks_like_length_error(err_msg) else "403 Forbidden"),
                "error_message": err_msg,
                "transaction_id": transaction_id,
                "headers": headers_s,
            }
        except Exception as e:
            logger.error(f"ツイート投稿エラー: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"レスポンス本文: {e.response.text[:500]}")
            import traceback
            logger.error(f"トレースバック:\n{traceback.format_exc()}")
            return {
                "success": False,
                "status": None,
                "reason": type(e).__name__,
                "error_message": str(e)[:500],
                "transaction_id": None,
                "headers": {},
            }
    
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
        
        # タイトルに「| パーサによるトマスの福音書」などのサブタイトルが含まれている場合は除去
        if title:
            title = re.sub(r"\s*\|.*", "", title)
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
            # 語録番号パターン: 「語録XX」「語録 (Logion) XX」など（全角・半角数字対応）
            goroku_pattern = r'語録(?:\s*\([^)]+\)\s*)?[０-９0-9]+'
            
            # 「ブログトップ...語録XX | Pursah's Gospelのブログ 語録XX」などのパターンを除去
            cleaned_content = re.sub(rf'ブログトップ.*?{goroku_pattern}\s*\|\s*Pursah\'?s Gospelのブログ\s*{goroku_pattern}', '', cleaned_content, flags=re.DOTALL)
            # 「ブログトップ...語録XX | パーサによるトマスの福音書 語録XX」などのパターンを除去
            cleaned_content = re.sub(rf'ブログトップ.*?{goroku_pattern}\s*\|\s*パーサによるトマスの福音書\s*{goroku_pattern}', '', cleaned_content, flags=re.DOTALL)
            # 「語録XX | Pursah's Gospelのブログ 語録XX」のパターンを除去
            cleaned_content = re.sub(rf'{goroku_pattern}\s*\|\s*Pursah\'?s Gospelのブログ\s*{goroku_pattern}', '', cleaned_content, flags=re.DOTALL)
            # 「語録XX | パーサによるトマスの福音書 語録XX」のパターンを除去
            cleaned_content = re.sub(rf'{goroku_pattern}\s*\|\s*パーサによるトマスの福音書\s*{goroku_pattern}', '', cleaned_content, flags=re.DOTALL)
            # 残っている「ブログトップ...語録XX」のパターンを除去（最も広いパターン）
            cleaned_content = re.sub(rf'ブログトップ.*?{goroku_pattern}', '', cleaned_content, flags=re.DOTALL)
            # コンテンツの先頭に残っている重複した語録番号を除去
            cleaned_content = re.sub(rf'^{goroku_pattern}\s*{goroku_pattern}', '', cleaned_content, flags=re.MULTILINE)
        
        cleaned_content = cleaned_content.strip()
        
        # pursahsgospelの場合: コンテンツの先頭が「語録XX」で始まる場合、その後に改行を追加
        if 'ameblo.jp/pursahs-gospel' in link or 'ameba.jp/profile/general/pursahs-gospel' in link:
            # コンテンツの先頭が「語録XX」または「語録 (Logion) XX」で始まる場合、その後に改行を追加
            # 語録番号パターン: 全角・半角数字対応
            goroku_head_pattern = r'^(語録(?:\s*\([^)]+\)\s*)?[０-９0-9]+)'
            match = re.match(goroku_head_pattern, cleaned_content)
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


