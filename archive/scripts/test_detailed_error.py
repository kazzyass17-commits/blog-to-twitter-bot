"""
403エラーの詳細な原因を調査するスクリプト
"""
import tweepy
import logging
from config import Config

logging.basicConfig(level=logging.DEBUG)  # DEBUGレベルで詳細なログを取得
logger = logging.getLogger(__name__)

def test_with_detailed_error(credentials: dict, account_name: str):
    """詳細なエラー情報を取得"""
    logger.info("=" * 60)
    logger.info(f"{account_name} アカウントの詳細エラー調査")
    logger.info("=" * 60)
    
    # 認証情報の確認
    logger.info("\n認証情報の確認:")
    logger.info(f"  API Key: {credentials.get('api_key', '')[:10]}... (長さ: {len(credentials.get('api_key', ''))})")
    logger.info(f"  API Secret: {'設定済み' if credentials.get('api_secret') else '未設定'} (長さ: {len(credentials.get('api_secret', ''))})")
    logger.info(f"  Access Token: {credentials.get('access_token', '')[:20]}... (長さ: {len(credentials.get('access_token', ''))})")
    logger.info(f"  Access Token Secret: {'設定済み' if credentials.get('access_token_secret') else '未設定'} (長さ: {len(credentials.get('access_token_secret', ''))})")
    logger.info(f"  Bearer Token: {'設定済み' if credentials.get('bearer_token') else '未設定'} (長さ: {len(credentials.get('bearer_token', ''))})")
    
    try:
        # Tweepyクライアントの作成
        logger.info("\nTweepyクライアントを作成中...")
        client = tweepy.Client(
            bearer_token=credentials.get('bearer_token') or None,
            consumer_key=credentials.get('api_key'),
            consumer_secret=credentials.get('api_secret'),
            access_token=credentials.get('access_token'),
            access_token_secret=credentials.get('access_token_secret'),
            wait_on_rate_limit=True
        )
        logger.info("✓ クライアント作成成功")
        
        # API接続テスト
        logger.info("\nAPI接続テスト中...")
        logger.info("使用するエンドポイント: GET /2/users/me")
        
        me = client.get_me()
        
        if me and me.data:
            logger.info(f"✓ 接続成功！")
            logger.info(f"  ユーザー名: @{me.data.username}")
            logger.info(f"  表示名: {me.data.name}")
            logger.info(f"  ユーザーID: {me.data.id}")
            return True
        else:
            logger.error("✗ API接続失敗: レスポンスが不正")
            return False
            
    except tweepy.Unauthorized as e:
        logger.error(f"✗ 認証エラー (401 Unauthorized): {e}")
        logger.error(f"  詳細: {str(e)}")
        if hasattr(e, 'response'):
            logger.error(f"  レスポンス: {e.response}")
        return False
        
    except tweepy.Forbidden as e:
        logger.error(f"✗ アクセス拒否 (403 Forbidden): {e}")
        logger.error(f"  詳細: {str(e)}")
        if hasattr(e, 'response'):
            logger.error(f"  レスポンス: {e.response}")
            if hasattr(e.response, 'text'):
                logger.error(f"  レスポンス本文: {e.response.text}")
        logger.error("\n403エラーの一般的な原因:")
        logger.error("  1. アプリの権限が「Read and write」に設定されていない")
        logger.error("  2. 権限変更後にAccess Tokenを再生成していない")
        logger.error("  3. アプリがX側の承認待ち（Pending approval）")
        logger.error("  4. アプリが停止（SUSPENDED）されている")
        logger.error("  5. API v2へのアクセス権限がない")
        return False
        
    except tweepy.TooManyRequests as e:
        logger.error(f"✗ レート制限 (429 Too Many Requests): {e}")
        logger.error("  しばらく待ってから再試行してください")
        return False
        
    except Exception as e:
        logger.error(f"✗ 予期しないエラー: {type(e).__name__}: {e}")
        logger.error(f"  詳細: {str(e)}")
        import traceback
        logger.error(f"  トレースバック:\n{traceback.format_exc()}")
        return False


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='403エラーの詳細な原因を調査')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both', 
                       help='調査するアカウント')
    
    args = parser.parse_args()
    
    success_count = 0
    
    if args.account in ['365bot', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_365bot()
        if test_with_detailed_error(credentials, "365botGary"):
            success_count += 1
    
    if args.account in ['pursahs', 'both']:
        logger.info("\n" + "=" * 60)
        credentials = Config.get_twitter_credentials_pursahs()
        if test_with_detailed_error(credentials, "pursahsgospel"):
            success_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"調査完了: {success_count} 件成功")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()




