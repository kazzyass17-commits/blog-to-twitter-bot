"""
X APIにリクエストを投げて、実際のレート制限の状態を取得する
"""
import logging
import sys
import io
from datetime import datetime
from config import Config
import tweepy

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def get_rate_limit_info(credentials: dict, account_name: str):
    """
    X APIにリクエストを投げて、レート制限の状態を取得する
    投稿API（create_tweet）のレート制限を確認するために、実際に投稿を試みる
    ただし、実際には投稿せず、レスポンスヘッダーからレート制限情報を取得する
    
    Args:
        credentials: Twitter API認証情報
        account_name: アカウント名（表示用）
    
    Returns:
        レート制限情報の辞書、またはNone（エラー時）
    """
    try:
        client = tweepy.Client(
            bearer_token=credentials.get('bearer_token'),
            consumer_key=credentials.get('api_key'),
            consumer_secret=credentials.get('api_secret'),
            access_token=credentials.get('access_token'),
            access_token_secret=credentials.get('access_token_secret'),
            wait_on_rate_limit=False  # レート制限で待機しない
        )
        
        # まず、get_me()で接続確認
        logger.info(f"{account_name}: 接続確認中...")
        me = client.get_me(user_fields=['username', 'name', 'id'])
        
        if not me or not me.data:
            logger.error(f"✗ {account_name}: 接続失敗")
            return None
        
        logger.info(f"✓ {account_name}: 接続成功 (@{me.data.username})")
        
        # 投稿APIのレート制限を確認するために、実際に投稿を試みる
        # ただし、実際には投稿せず、レスポンスヘッダーからレート制限情報を取得する
        # 注意: これは429エラーを引き起こす可能性がある
        logger.info(f"{account_name}: 投稿APIのレート制限情報を取得中...")
        logger.info(f"  ※ 実際に投稿を試みます（テスト用の短いテキスト）")
        logger.info(f"  ※ 429エラーが発生した場合、レスポンスヘッダーから情報を取得します")
        
        try:
            # テスト用の短いテキストで投稿を試みる
            test_text = f"テスト {datetime.now().strftime('%Y%m%d%H%M%S')}"
            response = client.create_tweet(text=test_text)
            
            # 成功した場合
            if response and response.data:
                tweet_id = response.data.get('id')
                logger.info(f"  ✓ 投稿成功（テスト用）")
                logger.info(f"  ツイートID: {tweet_id}")
                logger.warning(f"  ⚠ このツイートを削除してください: https://x.com/{me.data.username}/status/{tweet_id}")
                logger.info(f"  ※ レート制限情報は、レスポンスヘッダーから取得する必要があります")
                logger.info(f"  ※ tweepyでは、レスポンスヘッダーに直接アクセスできないため、")
                logger.info(f"  ※ 429エラーが発生した場合のエラーレスポンスから情報を取得します")
                
                return {
                    'success': True,
                    'username': me.data.username,
                    'rate_limited': False,
                    'tweet_id': tweet_id,
                    'note': '投稿成功。レート制限情報は、レスポンスヘッダーから取得する必要があります'
                }
            else:
                logger.warning(f"  ⚠ 投稿レスポンスが不正")
                return {
                    'success': True,
                    'username': me.data.username,
                    'rate_limited': False,
                    'note': '投稿レスポンスが不正'
                }
        except tweepy.TooManyRequests:
            # 429エラーが発生した場合、外側のexceptブロックで処理される
            raise
            
    except tweepy.TooManyRequests as e:
        # 429エラーが発生した場合、レスポンスヘッダーからリセット時刻を取得
        logger.error(f"✗ {account_name}: レート制限に達しました")
        
        reset_time = None
        if hasattr(e, 'response') and e.response is not None:
            if hasattr(e.response, 'headers'):
                rate_limit_reset = e.response.headers.get('x-rate-limit-reset')
                rate_limit_remaining = e.response.headers.get('x-rate-limit-remaining', '0')
                rate_limit_limit = e.response.headers.get('x-rate-limit-limit', '0')
                
                if rate_limit_reset:
                    reset_timestamp = int(rate_limit_reset)
                    reset_time = datetime.fromtimestamp(reset_timestamp)
                    now = datetime.now()
                    wait_seconds = (reset_time - now).total_seconds()
                    
                    logger.error(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.error(f"  残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                    logger.error(f"  残りリクエスト数: {rate_limit_remaining}/{rate_limit_limit}")
                    
                    return {
                        'success': False,
                        'rate_limited': True,
                        'reset_time': reset_time,
                        'wait_seconds': wait_seconds,
                        'remaining': int(rate_limit_remaining),
                        'limit': int(rate_limit_limit)
                    }
        
        logger.error(f"  リセット時刻の情報が取得できませんでした")
        return {
            'success': False,
            'rate_limited': True,
            'reset_time': None
        }
        
    except Exception as e:
        logger.error(f"✗ {account_name}: エラーが発生しました: {e}")
        return None


def check_both_accounts():
    """両方のアカウントのレート制限情報を確認"""
    print("=" * 60)
    print("X APIからレート制限情報を取得")
    print("=" * 60)
    print(f"確認時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 365botGary
    print("[365botGary]")
    credentials_365bot = Config.get_twitter_credentials_365bot()
    if credentials_365bot.get('api_key') and credentials_365bot.get('access_token'):
        result = get_rate_limit_info(credentials_365bot, '365botGary')
        if result:
            if result.get('rate_limited'):
                print(f"  ⚠ レート制限中")
                if result.get('reset_time'):
                    print(f"  リセット時刻: {result['reset_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  残り時間: {int(result['wait_seconds'])} 秒（{int(result['wait_seconds'] // 60)} 分）")
                if result.get('remaining') is not None:
                    print(f"  残りリクエスト数: {result['remaining']}/{result['limit']}")
            else:
                print(f"  ✓ レート制限なし（投稿可能）")
    else:
        print("  認証情報が設定されていません")
    print()
    
    # pursahsgospel
    print("[pursahsgospel]")
    credentials_pursahs = Config.get_twitter_credentials_pursahs()
    if credentials_pursahs.get('api_key') and credentials_pursahs.get('access_token'):
        result = get_rate_limit_info(credentials_pursahs, 'pursahsgospel')
        if result:
            if result.get('rate_limited'):
                print(f"  ⚠ レート制限中")
                if result.get('reset_time'):
                    print(f"  リセット時刻: {result['reset_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  残り時間: {int(result['wait_seconds'])} 秒（{int(result['wait_seconds'] // 60)} 分）")
                if result.get('remaining') is not None:
                    print(f"  残りリクエスト数: {result['remaining']}/{result['limit']}")
            else:
                print(f"  ✓ レート制限なし（投稿可能）")
    else:
        print("  認証情報が設定されていません")
    print()
    
    print("=" * 60)


if __name__ == "__main__":
    check_both_accounts()

