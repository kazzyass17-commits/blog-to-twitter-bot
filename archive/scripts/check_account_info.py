"""
Twitterアカウント情報を確認するスクリプト
設定されている認証情報から実際のアカウント情報を取得
"""
import tweepy
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_account_info(credentials: dict, account_name: str):
    """
    Twitterアカウント情報を確認
    
    Args:
        credentials: Twitter API認証情報
        account_name: アカウント名（ログ用）
    """
    logger.info("=" * 60)
    logger.info(f"{account_name} アカウント情報の確認")
    logger.info("=" * 60)
    
    # 認証情報の確認
    has_api_key = bool(credentials.get('api_key'))
    has_api_secret = bool(credentials.get('api_secret'))
    has_access_token = bool(credentials.get('access_token'))
    has_access_token_secret = bool(credentials.get('access_token_secret'))
    
    if not (has_api_key and has_api_secret and has_access_token and has_access_token_secret):
        logger.error("✗ 認証情報が不足しています。")
        logger.error("  設定されている認証情報:")
        logger.error(f"    API Key: {'✓' if has_api_key else '✗'}")
        logger.error(f"    API Secret: {'✓' if has_api_secret else '✗'}")
        logger.error(f"    Access Token: {'✓' if has_access_token else '✗'}")
        logger.error(f"    Access Token Secret: {'✓' if has_access_token_secret else '✗'}")
        return None
    
    # Tweepyクライアントの作成
    try:
        client = tweepy.Client(
            bearer_token=credentials.get('bearer_token'),
            consumer_key=credentials.get('api_key'),
            consumer_secret=credentials.get('api_secret'),
            access_token=credentials.get('access_token'),
            access_token_secret=credentials.get('access_token_secret'),
            wait_on_rate_limit=True
        )
    except Exception as e:
        logger.error(f"✗ クライアント作成失敗: {e}")
        return None
    
    # アカウント情報を取得
    try:
        logger.info("\nアカウント情報を取得中...")
        me = client.get_me(user_fields=['username', 'name', 'id', 'description', 'profile_image_url', 'created_at'])
        
        if me and me.data:
            account_info = {
                'username': me.data.username,
                'name': me.data.name,
                'id': me.data.id,
                'description': getattr(me.data, 'description', ''),
                'profile_image_url': getattr(me.data, 'profile_image_url', ''),
                'created_at': getattr(me.data, 'created_at', ''),
            }
            
            logger.info("✓ アカウント情報取得成功！")
            logger.info(f"\nアカウント情報:")
            logger.info(f"  ユーザー名（ハンドル）: @{account_info['username']}")
            logger.info(f"  表示名: {account_info['name']}")
            logger.info(f"  ユーザーID: {account_info['id']}")
            if account_info['description']:
                logger.info(f"  プロフィール: {account_info['description'][:100]}")
            if account_info['created_at']:
                logger.info(f"  作成日時: {account_info['created_at']}")
            logger.info(f"\nTwitter URL: https://twitter.com/{account_info['username']}")
            logger.info(f"X URL: https://x.com/{account_info['username']}")
            
            return account_info
        else:
            logger.error("✗ アカウント情報の取得に失敗しました")
            return None
            
    except tweepy.Unauthorized:
        logger.error("✗ 認証エラー: API認証情報が無効です。")
        logger.error("  認証情報を確認してください。")
        return None
    except tweepy.Forbidden:
        logger.error("✗ アクセス拒否: この認証情報ではアカウント情報を取得できません。")
        return None
    except Exception as e:
        logger.error(f"✗ エラー: {e}")
        return None


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitterアカウント情報を確認')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both', 
                       help='確認するアカウント')
    
    args = parser.parse_args()
    
    results = {}
    
    if args.account in ['365bot', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_365bot()
        account_info = check_account_info(credentials, "365botGary")
        if account_info:
            results['365bot'] = account_info
            logger.info(f"\n設定されているハンドル: {Config.TWITTER_365BOT_HANDLE}")
            logger.info(f"実際のハンドル: @{account_info['username']}")
            if Config.TWITTER_365BOT_HANDLE.lower() != account_info['username'].lower():
                logger.warning("⚠️ 設定されているハンドルと実際のハンドルが異なります！")
                logger.warning(f"  設定: {Config.TWITTER_365BOT_HANDLE}")
                logger.warning(f"  実際: @{account_info['username']}")
    
    if args.account in ['pursahs', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_pursahs()
        account_info = check_account_info(credentials, "pursahsgospel")
        if account_info:
            results['pursahs'] = account_info
            logger.info(f"\n設定されているハンドル: {Config.TWITTER_PURSAHS_HANDLE}")
            logger.info(f"実際のハンドル: @{account_info['username']}")
            if Config.TWITTER_PURSAHS_HANDLE.lower() != account_info['username'].lower():
                logger.warning("⚠️ 設定されているハンドルと実際のハンドルが異なります！")
                logger.warning(f"  設定: {Config.TWITTER_PURSAHS_HANDLE}")
                logger.warning(f"  実際: @{account_info['username']}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"確認完了: {len(results)} 件成功")
    logger.info("=" * 60)
    
    # 結果をまとめて表示
    if results:
        logger.info("\n=== 確認結果のまとめ ===")
        for key, info in results.items():
            account_name = "365botGary" if key == '365bot' else "pursahsgospel"
            logger.info(f"\n{account_name}:")
            logger.info(f"  ハンドル: @{info['username']}")
            logger.info(f"  表示名: {info['name']}")
            logger.info(f"  URL: https://x.com/{info['username']}")


if __name__ == "__main__":
    main()




