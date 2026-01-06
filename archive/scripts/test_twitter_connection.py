"""
X (Twitter) APIへの接続テスト
認証情報が正しく設定されているか、APIに接続できるかを確認
"""
import tweepy
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_twitter_connection(credentials: dict, account_name: str):
    """
    Twitter APIへの接続をテスト
    
    Args:
        credentials: Twitter API認証情報
        account_name: アカウント名（ログ用）
    """
    logger.info("=" * 60)
    logger.info(f"{account_name} アカウントの接続テスト")
    logger.info("=" * 60)
    
    # 認証情報の確認
    logger.info("\n認証情報の確認:")
    has_api_key = bool(credentials.get('api_key'))
    has_api_secret = bool(credentials.get('api_secret'))
    has_access_token = bool(credentials.get('access_token'))
    has_access_token_secret = bool(credentials.get('access_token_secret'))
    has_bearer_token = bool(credentials.get('bearer_token'))
    
    logger.info(f"  API Key: {'✓ 設定済み' if has_api_key else '✗ 未設定'}")
    logger.info(f"  API Secret: {'✓ 設定済み' if has_api_secret else '✗ 未設定'}")
    logger.info(f"  Access Token: {'✓ 設定済み' if has_access_token else '✗ 未設定'}")
    logger.info(f"  Access Token Secret: {'✓ 設定済み' if has_access_token_secret else '✗ 未設定'}")
    logger.info(f"  Bearer Token: {'✓ 設定済み' if has_bearer_token else '✗ 未設定'}")
    
    if not (has_api_key and has_api_secret and has_access_token and has_access_token_secret):
        logger.error("\n✗ 認証情報が不足しています。.envファイルを確認してください。")
        return False
    
    # Tweepyクライアントの作成
    try:
        logger.info("\nTweepyクライアントを作成中...")
        client = tweepy.Client(
            bearer_token=credentials.get('bearer_token'),
            consumer_key=credentials.get('api_key'),
            consumer_secret=credentials.get('api_secret'),
            access_token=credentials.get('access_token'),
            access_token_secret=credentials.get('access_token_secret'),
            wait_on_rate_limit=True
        )
        logger.info("✓ クライアント作成成功")
    except Exception as e:
        logger.error(f"✗ クライアント作成失敗: {e}")
        return False
    
    # API接続テスト（自分のアカウント情報を取得）
    try:
        logger.info("\nAPI接続テスト中...")
        logger.info("使用するエンドポイント: GET /2/users/me")
        # より詳細なエラー情報を取得するため、user_fieldsを指定
        me = client.get_me(user_fields=['username', 'name', 'id'])
        
        if me and me.data:
            logger.info(f"✓ 接続成功！")
            logger.info(f"  ユーザー名: @{me.data.username}")
            logger.info(f"  表示名: {me.data.name}")
            logger.info(f"  ユーザーID: {me.data.id}")
            
            # 追加テスト: 最新ツイートを取得（API v2の動作確認）
            try:
                logger.info("\nAPI v2の動作確認中（最新ツイートを取得）...")
                tweets = client.get_users_tweets(
                    id=me.data.id,
                    max_results=5,  # min 5, max 100
                    tweet_fields=['created_at', 'public_metrics', 'text']
                )
                if tweets and tweets.data:
                    latest_tweet = tweets.data[0]
                    logger.info(f"✓ 最新ツイート取得成功")
                    logger.info(f"  ツイートID: {latest_tweet.id}")
                    logger.info(f"  投稿日時: {latest_tweet.created_at}")
                    logger.info(f"  テキスト: {latest_tweet.text[:50]}...")
                else:
                    logger.info("  ツイートがありません（新規アカウントの可能性）")
            except Exception as e:
                logger.warning(f"  ツイート取得テストでエラー（接続自体は成功）: {e}")
            
            return True
        else:
            logger.error("✗ API接続失敗: レスポンスが不正")
            return False
    except tweepy.Unauthorized as e:
        logger.error("✗ 認証エラー: API認証情報が無効です。")
        logger.error(f"  詳細: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"  レスポンス: {e.response}")
            if hasattr(e.response, 'text'):
                logger.error(f"  レスポンス本文: {e.response.text[:500]}")
        logger.error("  .envファイルの認証情報を確認してください。")
        return False
    except tweepy.Forbidden as e:
        logger.error("✗ アクセス拒否 (403 Forbidden): アプリの権限または状態に問題があります。")
        logger.error(f"  詳細: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"  レスポンス: {e.response}")
            if hasattr(e.response, 'text'):
                logger.error(f"  レスポンス本文: {e.response.text[:500]}")
        logger.error("\n  考えられる原因:")
        logger.error("  1. アプリの権限が「Read and write」に設定されていない")
        logger.error("  2. 権限変更後にAccess Tokenを再生成していない")
        logger.error("  3. アプリがX側の承認待ち（Pending approval）")
        logger.error("  4. アプリが停止（SUSPENDED）されている")
        logger.error("  5. API v2へのアクセス権限がない")
        return False
    except tweepy.TooManyRequests as e:
        logger.error("✗ レート制限: リクエストが多すぎます。しばらく待ってから再試行してください。")
        logger.error(f"  詳細: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ API接続エラー: {type(e).__name__}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"  レスポンス: {e.response}")
            if hasattr(e.response, 'text'):
                logger.error(f"  レスポンス本文: {e.response.text[:500]}")
        import traceback
        logger.error(f"  トレースバック:\n{traceback.format_exc()}")
        return False


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='X (Twitter) API接続テスト')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both', 
                       help='テストするアカウント')
    
    args = parser.parse_args()
    
    success_count = 0
    
    if args.account in ['365bot', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_365bot()
        if test_twitter_connection(credentials, "365botGary"):
            success_count += 1
    
    if args.account in ['pursahs', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_pursahs()
        if test_twitter_connection(credentials, "pursahsgospel"):
            success_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"接続テスト完了: {success_count} 件成功")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

