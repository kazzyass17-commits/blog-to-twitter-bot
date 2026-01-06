"""
X APIのレスポンスヘッダーからレート制限情報を取得するスクリプト
実際のレート制限の状態を確認する
"""
import tweepy
import logging
from datetime import datetime
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_rate_limit_headers(credentials: dict, account_name: str):
    """
    X APIのレスポンスヘッダーからレート制限情報を取得
    
    Args:
        credentials: Twitter API認証情報
        account_name: アカウント名（ログ用）
    """
    logger.info("=" * 60)
    logger.info(f"{account_name} アカウントのレート制限情報確認")
    logger.info("=" * 60)
    
    try:
        # Tweepyクライアントの作成
        logger.info("\nTweepyクライアントを作成中...")
        client = tweepy.Client(
            bearer_token=credentials.get('bearer_token'),
            consumer_key=credentials.get('api_key'),
            consumer_secret=credentials.get('api_secret'),
            access_token=credentials.get('access_token'),
            access_token_secret=credentials.get('access_token_secret'),
            wait_on_rate_limit=False
        )
        logger.info("✓ クライアント作成成功")
        
        # get_meでレート制限情報を取得（読み取り専用API）
        logger.info("\n[ステップ1] GET /2/users/me でレート制限情報を取得...")
        try:
            me = client.get_me(user_fields=['username', 'name', 'id'])
            if me and me.data:
                logger.info(f"✓ 接続成功: @{me.data.username}")
                
                # レスポンスヘッダーを確認
                logger.info("\nレスポンスオブジェクトの属性を確認:")
                logger.info(f"  meの型: {type(me)}")
                logger.info(f"  meの属性: {dir(me)}")
                
                # tweepyのレスポンスオブジェクトからヘッダーを取得
                if hasattr(me, 'response') and me.response is not None:
                    logger.info(f"  me.responseの型: {type(me.response)}")
                    logger.info(f"  me.responseの属性: {dir(me.response)}")
                    if hasattr(me.response, 'headers'):
                        headers = me.response.headers
                        logger.info("\nレスポンスヘッダー（GET /2/users/me）:")
                        logger.info(f"  x-rate-limit-limit: {headers.get('x-rate-limit-limit', 'N/A')}")
                        logger.info(f"  x-rate-limit-remaining: {headers.get('x-rate-limit-remaining', 'N/A')}")
                        logger.info(f"  x-rate-limit-reset: {headers.get('x-rate-limit-reset', 'N/A')}")
                        
                        reset_timestamp = headers.get('x-rate-limit-reset')
                        if reset_timestamp:
                            reset_time = datetime.fromtimestamp(int(reset_timestamp))
                            logger.info(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logger.warning("  me.responseが存在しません")
        except Exception as e:
            logger.error(f"✗ get_meエラー: {e}")
        
        # create_tweetを試行してレート制限情報を取得
        logger.info("\n[ステップ2] POST /2/tweets でレート制限情報を取得...")
        logger.info("警告: このスクリプトはcreate_tweetを呼び出します")
        logger.info("警告: 429エラーが発生する可能性があり、そのリクエストもカウントされる可能性があります")
        logger.info("警告: 実際にツイートが投稿される可能性もあります")
        logger.info("警告: リセット時刻が過ぎてから実行することを推奨します")
        
        import sys
        response = input("\n続行しますか？ (y/N): ").strip().lower()
        if response != 'y':
            logger.info("キャンセルしました")
            return
        
        test_text = "テスト投稿（レート制限確認用）"
        try:
            response = client.create_tweet(text=test_text)
            if response and response.data:
                logger.info(f"✓ ツイート投稿成功: ID={response.data.get('id')}")
                
                # レスポンスオブジェクトの構造を確認
                logger.info("\nレスポンスオブジェクトの属性を確認:")
                logger.info(f"  responseの型: {type(response)}")
                logger.info(f"  responseの属性: {[attr for attr in dir(response) if not attr.startswith('_')]}")
                
                # tweepyのレスポンスオブジェクトからヘッダーを取得
                if hasattr(response, 'response') and response.response is not None:
                    logger.info(f"  response.responseの型: {type(response.response)}")
                    logger.info(f"  response.responseの属性: {[attr for attr in dir(response.response) if not attr.startswith('_')]}")
                    if hasattr(response.response, 'headers'):
                        headers = response.response.headers
                        logger.info("\nレスポンスヘッダー（POST /2/tweets）:")
                        logger.info(f"  x-rate-limit-limit: {headers.get('x-rate-limit-limit', 'N/A')}")
                        logger.info(f"  x-rate-limit-remaining: {headers.get('x-rate-limit-remaining', 'N/A')}")
                        logger.info(f"  x-rate-limit-reset: {headers.get('x-rate-limit-reset', 'N/A')}")
                        
                        limit = headers.get('x-rate-limit-limit')
                        remaining = headers.get('x-rate-limit-remaining')
                        reset_timestamp = headers.get('x-rate-limit-reset')
                        
                        if limit and remaining:
                            logger.info(f"\nレート制限の状態:")
                            logger.info(f"  上限: {limit} リクエスト")
                            logger.info(f"  残り: {remaining} リクエスト")
                            logger.info(f"  使用済み: {int(limit) - int(remaining)} リクエスト")
                            logger.info(f"  15分間のウィンドウ内で {int(limit) - int(remaining)} リクエストがカウントされています")
                        
                        if reset_timestamp:
                            reset_time = datetime.fromtimestamp(int(reset_timestamp))
                            logger.info(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            now = datetime.now()
                            if reset_time > now:
                                wait_seconds = (reset_time - now).total_seconds()
                                logger.info(f"  リセットまで: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                    else:
                        logger.warning("  response.response.headersが存在しません")
                else:
                    logger.warning("  response.responseが存在しません")
        except tweepy.TooManyRequests as e:
            logger.error("✗ 429 Too Many Requests エラー")
            logger.error(f"  詳細: {e}")
            
            # エラーレスポンスからヘッダーを取得
            if hasattr(e, 'response') and e.response is not None:
                if hasattr(e.response, 'headers'):
                    headers = e.response.headers
                    logger.info("\nエラーレスポンスヘッダー（POST /2/tweets）:")
                    logger.info(f"  x-rate-limit-limit: {headers.get('x-rate-limit-limit', 'N/A')}")
                    logger.info(f"  x-rate-limit-remaining: {headers.get('x-rate-limit-remaining', 'N/A')}")
                    logger.info(f"  x-rate-limit-reset: {headers.get('x-rate-limit-reset', 'N/A')}")
                    
                    limit = headers.get('x-rate-limit-limit')
                    remaining = headers.get('x-rate-limit-remaining')
                    reset_timestamp = headers.get('x-rate-limit-reset')
                    
                    if limit and remaining:
                        logger.info(f"\nレート制限の状態:")
                        logger.info(f"  上限: {limit} リクエスト")
                        logger.info(f"  残り: {remaining} リクエスト")
                        logger.info(f"  使用済み: {int(limit) - int(remaining)} リクエスト")
                        logger.info(f"  15分間のウィンドウ内で {int(limit) - int(remaining)} リクエストがカウントされています")
                    
                    if reset_timestamp:
                        reset_time = datetime.fromtimestamp(int(reset_timestamp))
                        logger.info(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        now = datetime.now()
                        if reset_time > now:
                            wait_seconds = (reset_time - now).total_seconds()
                            logger.info(f"  リセットまで: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
        except Exception as e:
            logger.error(f"✗ エラー: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"  トレースバック:\n{traceback.format_exc()}")
            
    except Exception as e:
        logger.error(f"✗ エラー: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"  トレースバック:\n{traceback.format_exc()}")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='X APIのレート制限情報を確認')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='pursahs', 
                       help='確認するアカウント')
    
    args = parser.parse_args()
    
    if args.account in ['365bot', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_365bot()
        check_rate_limit_headers(credentials, "365botGary")
    
    if args.account in ['pursahs', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_pursahs()
        check_rate_limit_headers(credentials, "pursahsgospel")


if __name__ == "__main__":
    main()

