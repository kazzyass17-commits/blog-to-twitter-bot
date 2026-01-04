"""
pursahsgospelアカウントのツイート取得で401エラーが出る原因を調査
"""
import tweepy
import logging
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def test_tweet_access():
    """ツイート取得のアクセステスト"""
    logger.info("=" * 60)
    logger.info("pursahsgospel ツイート取得アクセステスト")
    logger.info("=" * 60)
    
    credentials = Config.get_twitter_credentials_pursahs()
    
    # 認証情報の確認
    logger.info("\n認証情報の確認:")
    logger.info(f"  API Key: {'設定済み' if credentials.get('api_key') else '未設定'}")
    logger.info(f"  API Secret: {'設定済み' if credentials.get('api_secret') else '未設定'}")
    logger.info(f"  Access Token: {'設定済み' if credentials.get('access_token') else '未設定'}")
    logger.info(f"  Access Token Secret: {'設定済み' if credentials.get('access_token_secret') else '未設定'}")
    logger.info(f"  Bearer Token: {'設定済み' if credentials.get('bearer_token') else '未設定'}")
    
    try:
        # Tweepyクライアントの作成
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
        
        # ステップ1: 自分のアカウント情報を取得（これは成功している）
        logger.info("\n[ステップ1] 自分のアカウント情報を取得...")
        me = client.get_me(user_fields=['username', 'name', 'id'])
        if me and me.data:
            logger.info(f"✓ 成功: @{me.data.username} (ID: {me.data.id})")
            user_id = me.data.id
        else:
            logger.error("✗ アカウント情報の取得に失敗")
            return False
        
        # ステップ2: ツイート取得を試行（ここで401エラーが出ている）
        logger.info("\n[ステップ2] ツイート取得を試行...")
        logger.info(f"  エンドポイント: GET /2/users/:id/tweets")
        logger.info(f"  ユーザーID: {user_id}")
        
        try:
            tweets = client.get_users_tweets(
                id=user_id,
                max_results=5,
                tweet_fields=['created_at', 'public_metrics', 'text']
            )
            
            if tweets and tweets.data:
                logger.info(f"✓ ツイート取得成功: {len(tweets.data)}件")
                for i, tweet in enumerate(tweets.data[:3], 1):
                    logger.info(f"  ツイート{i}: {tweet.id} - {tweet.text[:50]}...")
            else:
                logger.info("  ツイートがありません（新規アカウントの可能性）")
            return True
            
        except tweepy.Unauthorized as e:
            logger.error("✗ 401 Unauthorized エラー")
            logger.error(f"  エラー詳細: {e}")
            logger.error(f"  エラータイプ: {type(e).__name__}")
            
            # レスポンスの詳細を確認
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"  レスポンスステータス: {e.response.status_code}")
                logger.error(f"  レスポンスヘッダー: {dict(e.response.headers)}")
                if hasattr(e.response, 'text'):
                    logger.error(f"  レスポンス本文: {e.response.text[:500]}")
            
            logger.error("\n考えられる原因:")
            logger.error("  1. アプリの権限が「Read」のみに設定されている")
            logger.error("  2. Access Tokenが「Read」権限で生成されている")
            logger.error("  3. ツイート取得エンドポイントへのアクセス権限が不足")
            logger.error("  4. Bearer Tokenが必要だが設定されていない")
            
            return False
            
        except tweepy.Forbidden as e:
            logger.error("✗ 403 Forbidden エラー")
            logger.error(f"  エラー詳細: {e}")
            return False
            
        except Exception as e:
            logger.error(f"✗ 予期しないエラー: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"  トレースバック:\n{traceback.format_exc()}")
            return False
            
    except Exception as e:
        logger.error(f"✗ クライアント作成エラー: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"  トレースバック:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    test_tweet_access()







