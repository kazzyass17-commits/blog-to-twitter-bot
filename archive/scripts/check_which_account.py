"""
取得した認証情報がどのアカウントに接続できるか確認するスクリプト
"""
import tweepy
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数から認証情報を取得（手動で設定）
API_KEY = "4qdM8ReQ1cz5cqhuKR1FLA1BI"
API_SECRET = "OKAN0JK4o4adTG22czDpK3O3TropljlV7AVsWfuKpdcb4u9Rzo"
ACCESS_TOKEN = "2420551951-XTDbsbeBFgHTj3EthyQfP0sfO9o77BwzXS2Py5h"
ACCESS_TOKEN_SECRET = "FgCmmWUWydSHr4vZRuWPAezMMgCZJi1B6SVPxoeUvIRiB"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAJGu6gEAAAAAVcqxSpKkusd%2FjphkF%2BqUgfBAWWY%3D47QIHXptPgtcHgm5texQcUdQggD0Ezqfa7ksOGPmte9v396aRy"

def check_account():
    """認証情報で接続できるアカウントを確認"""
    logger.info("=" * 60)
    logger.info("認証情報で接続できるアカウントを確認中...")
    logger.info("=" * 60)
    
    try:
        # Tweepyクライアントを作成
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
        # アカウント情報を取得
        logger.info("\nアカウント情報を取得中...")
        me = client.get_me(user_fields=['username', 'name', 'id'])
        
        if me and me.data:
            username = me.data.username
            name = me.data.name
            user_id = me.data.id
            
            logger.info("✓ 接続成功！")
            logger.info(f"  ユーザー名（ハンドル）: @{username}")
            logger.info(f"  表示名: {name}")
            logger.info(f"  ユーザーID: {user_id}")
            logger.info(f"  Twitter URL: https://twitter.com/{username}")
            logger.info(f"  X URL: https://x.com/{username}")
            
            logger.info("\n" + "=" * 60)
            logger.info("判断結果")
            logger.info("=" * 60)
            
            # アカウント名から判断
            username_lower = username.lower()
            if '365bot' in username_lower or '365' in username_lower:
                logger.info("✓ この認証情報は 365botGary アカウント用です")
                logger.info("\n設定方法:")
                logger.info("  同じアカウントで両方運用する場合:")
                logger.info("    - デフォルトのSecrets（TWITTER_API_KEY等）に設定")
                logger.info("  別アカウントで運用する場合:")
                logger.info("    - TWITTER_365BOT_API_KEY 等に設定")
                logger.info("    - pursahsgospel用の認証情報も別途取得が必要")
            elif 'pursahs' in username_lower or 'pursah' in username_lower:
                logger.info("✓ この認証情報は pursahsgospel アカウント用です")
                logger.info("\n設定方法:")
                logger.info("  同じアカウントで両方運用する場合:")
                logger.info("    - デフォルトのSecrets（TWITTER_API_KEY等）に設定")
                logger.info("  別アカウントで運用する場合:")
                logger.info("    - TWITTER_PURSAHS_API_KEY 等に設定")
                logger.info("    - 365botGary用の認証情報も別途取得が必要")
            else:
                logger.info(f"⚠️ アカウント名から判断できませんでした: @{username}")
                logger.info("\n設定方法:")
                logger.info("  この認証情報をデフォルトのSecretsに設定してください")
                logger.info("  同じアカウントで両方運用する場合は問題ありません")
                logger.info("  別アカウントで運用する場合は、それぞれの認証情報が必要です")
            
            return username
        else:
            logger.error("✗ アカウント情報の取得に失敗しました")
            return None
            
    except tweepy.Unauthorized:
        logger.error("✗ 認証エラー: API認証情報が無効です")
        return None
    except Exception as e:
        logger.error(f"✗ エラー: {e}")
        return None


if __name__ == "__main__":
    check_account()




