"""
直接APIを呼び出して403エラーの原因を調査
"""
import requests
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_api(credentials: dict, account_name: str):
    """直接APIを呼び出してテスト"""
    logger.info("=" * 60)
    logger.info(f"{account_name} アカウントの直接APIテスト")
    logger.info("=" * 60)
    
    # OAuth 1.0aでリクエストを送信
    from requests_oauthlib import OAuth1
    
    auth = OAuth1(
        credentials.get('api_key'),
        credentials.get('api_secret'),
        credentials.get('access_token'),
        credentials.get('access_token_secret')
    )
    
    # API v2のエンドポイントを直接呼び出し
    url = "https://api.x.com/2/users/me"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        logger.info(f"\nURL: {url}")
        logger.info("認証方法: OAuth 1.0a")
        
        response = requests.get(url, auth=auth, headers=headers, timeout=30)
        
        logger.info(f"ステータスコード: {response.status_code}")
        logger.info(f"レスポンスヘッダー: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✓ API接続成功！")
            logger.info(f"  レスポンス: {data}")
            return True
        else:
            logger.error(f"✗ API接続失敗: {response.status_code}")
            logger.error(f"  レスポンス本文（最初の500文字）: {response.text[:500]}")
            
            # レスポンスがHTMLの場合、セキュリティチェックの可能性
            if '<!DOCTYPE html>' in response.text or '<html' in response.text:
                logger.error("\n⚠️ HTMLレスポンスが返ってきました。")
                logger.error("  これは、セキュリティチェック（Cloudflareなど）に引っかかっている可能性があります。")
                logger.error("  考えられる原因:")
                logger.error("  1. GitHub ActionsのIPアドレスがブロックされている")
                logger.error("  2. レート制限に達している")
                logger.error("  3. アプリの状態に問題がある")
            
            return False
            
    except Exception as e:
        logger.error(f"✗ エラー: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"  トレースバック:\n{traceback.format_exc()}")
        return False


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='直接APIを呼び出してテスト')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both', 
                       help='テストするアカウント')
    
    args = parser.parse_args()
    
    success_count = 0
    
    if args.account in ['365bot', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_365bot()
        if test_direct_api(credentials, "365botGary"):
            success_count += 1
    
    if args.account in ['pursahs', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_pursahs()
        if test_direct_api(credentials, "pursahsgospel"):
            success_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"テスト完了: {success_count} 件成功")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()




