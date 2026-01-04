"""
429エラーの原因を分析
接続テストと投稿テストで使用されるAPI呼び出しを確認
"""
import logging
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

def analyze_api_calls():
    """API呼び出しを分析"""
    logger.info("=" * 60)
    logger.info("429エラーの原因分析")
    logger.info("=" * 60)
    
    logger.info("\n【接続テスト（test_twitter_connection.py）で使用されるAPI】")
    logger.info("1. get_me() - GET /2/users/me")
    logger.info("   - レート制限: 1時間あたり75回")
    logger.info("2. get_users_tweets() - GET /2/users/:id/tweets")
    logger.info("   - レート制限: 1時間あたり75回")
    
    logger.info("\n【投稿テスト（test_post.py）で使用されるAPI】")
    logger.info("1. post_tweet_with_link() → post_tweet() → create_tweet()")
    logger.info("   - POST /2/tweets")
    logger.info("   - レート制限: 1時間あたり300回")
    
    logger.info("\n【問題点】")
    logger.info("1. 接続テストを実行すると、get_me()とget_users_tweets()が呼び出される")
    logger.info("2. これらのAPI呼び出しもレート制限にカウントされる")
    logger.info("3. 接続テストの後に投稿テストを実行すると、レート制限に達する可能性がある")
    
    logger.info("\n【考えられる原因】")
    logger.info("1. 接続テストを複数回実行した")
    logger.info("2. 投稿テストを複数回実行した")
    logger.info("3. 接続テストと投稿テストを連続で実行した")
    logger.info("4. 以前の実行でレート制限に達していた")
    
    logger.info("\n【対処法】")
    logger.info("1. 接続テストは必要最小限に抑える")
    logger.info("2. 投稿テストの前に接続テストを実行しない")
    logger.info("3. レート制限が発生した場合は、待機時間を守る")
    logger.info("4. test_post_with_rate_limit_management.pyを使用する（レート制限管理機能付き）")
    
    logger.info("\n【確認事項】")
    logger.info("- 接続テストを何回実行したか？")
    logger.info("- 投稿テストを何回実行したか？")
    logger.info("- 接続テストと投稿テストを連続で実行したか？")
    logger.info("- 以前の実行でレート制限に達していたか？")
    
    logger.info("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_api_calls()







