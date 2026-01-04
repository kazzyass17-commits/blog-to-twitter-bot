"""
pursahsgospelアカウントで実際にツイート投稿をテスト
ツイート取得で401エラーが出ても、投稿ができれば問題ない
"""
import tweepy
import logging
from config import Config
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def test_actual_post():
    """実際にツイートを投稿してテスト"""
    logger.info("=" * 60)
    logger.info("pursahsgospel ツイート投稿テスト")
    logger.info("=" * 60)
    
    credentials = Config.get_twitter_credentials_pursahs()
    
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
        
        # ステップ1: 自分のアカウント情報を取得
        logger.info("\n[ステップ1] 自分のアカウント情報を取得...")
        me = client.get_me(user_fields=['username', 'name', 'id'])
        if me and me.data:
            logger.info(f"✓ 成功: @{me.data.username} (ID: {me.data.id})")
        else:
            logger.error("✗ アカウント情報の取得に失敗")
            return False
        
        # ステップ2: テストツイートを投稿
        logger.info("\n[ステップ2] テストツイートを投稿...")
        test_text = f"テスト投稿 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        logger.info(f"  投稿内容: {test_text}")
        
        try:
            response = client.create_tweet(text=test_text)
            if response and response.data:
                tweet_id = response.data['id']
                logger.info(f"✓ ツイート投稿成功！")
                logger.info(f"  ツイートID: {tweet_id}")
                logger.info(f"  ツイートURL: https://x.com/pursahsgospel/status/{tweet_id}")
                logger.info("\n結論: ツイート投稿機能は正常に動作しています。")
                logger.info("  ツイート取得で401エラーが出ても、投稿機能には影響ありません。")
                return True
            else:
                logger.error("✗ ツイート投稿失敗: レスポンスが不正")
                return False
                
        except tweepy.Unauthorized as e:
            logger.error("✗ 401 Unauthorized エラー（投稿）")
            logger.error(f"  エラー詳細: {e}")
            logger.error("  考えられる原因:")
            logger.error("    1. Access Tokenが無効")
            logger.error("    2. アプリの権限が正しく設定されていない")
            logger.error("    3. Access Tokenが再生成されていない")
            return False
            
        except tweepy.Forbidden as e:
            logger.error("✗ 403 Forbidden エラー（投稿）")
            logger.error(f"  エラー詳細: {e}")
            logger.error("  考えられる原因:")
            logger.error("    1. アプリの権限が「Read and write」に設定されていない")
            logger.error("    2. 権限変更後にAccess Tokenを再生成していない")
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
    test_actual_post()







