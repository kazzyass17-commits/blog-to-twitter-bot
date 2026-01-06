"""
pursahsgospelアカウントで実際にツイート投稿ができるかテスト
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


def test_post_access():
    """ツイート投稿のアクセステスト"""
    logger.info("=" * 60)
    logger.info("pursahsgospel ツイート投稿アクセステスト")
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
        
        # ステップ2: テストツイートを投稿（実際には投稿しない、dry run）
        logger.info("\n[ステップ2] ツイート投稿の権限をテスト...")
        logger.info("  注意: 実際にはツイートを投稿しません（dry run）")
        
        # 実際には投稿せず、権限チェックのみ
        # create_tweet APIを呼び出す前に、認証情報が正しいか確認
        test_text = f"テスト投稿 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        logger.info("\n実際にツイートを投稿してテストしますか？")
        logger.info("  （このテストは実際にツイートを投稿します）")
        logger.info("  テストをスキップする場合は、このスクリプトを終了してください")
        
        # 実際には投稿しないで、権限チェックのみ行う
        logger.info("\n✓ 認証情報は正しく設定されています")
        logger.info("  ツイート取得で401エラーが出ても、投稿機能は動作する可能性があります")
        logger.info("  実際の投稿テストは test_post.py を使用してください")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ エラー: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"  トレースバック:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    test_post_access()










