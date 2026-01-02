"""
アプリの権限と状態を診断するスクリプト
"""
import os
import sys
from dotenv import load_dotenv
import tweepy
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def diagnose_account(account_name: str, credentials: dict):
    """アカウントの権限と状態を診断"""
    logger.info(f"\n{'='*60}")
    logger.info(f"{account_name} アカウントの診断")
    logger.info(f"{'='*60}\n")
    
    # 認証情報の確認
    api_key = credentials.get('api_key')
    api_secret = credentials.get('api_secret')
    access_token = credentials.get('access_token')
    access_token_secret = credentials.get('access_token_secret')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        logger.error("認証情報が不完全です")
        return False
    
    try:
        # OAuth 1.0a でクライアント作成
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # 1. アカウント情報の取得（読み取りテスト）
        logger.info("1. アカウント情報の取得（読み取りテスト）...")
        try:
            me = client.get_me(user_fields=['username', 'name', 'id'])
            if me and me.data:
                logger.info(f"   ✓ 成功: @{me.data.username} ({me.data.name})")
            else:
                logger.error("   ✗ 失敗: レスポンスが不正")
                return False
        except Exception as e:
            logger.error(f"   ✗ 失敗: {e}")
            return False
        
        # 2. ツイート投稿テスト（書き込みテスト）
        logger.info("\n2. ツイート投稿テスト（書き込みテスト）...")
        test_text = "テスト投稿 - これは自動投稿ボットのテストです。すぐに削除されます。"
        try:
            response = client.create_tweet(text=test_text)
            if response and response.data:
                tweet_id = response.data.get('id')
                logger.info(f"   ✓ 成功: ツイートID={tweet_id}")
                logger.info(f"   ツイート内容: {test_text}")
                logger.warning(f"   このツイートを削除してください: https://twitter.com/i/web/status/{tweet_id}")
                return True
            else:
                logger.error("   ✗ 失敗: レスポンスが不正")
                return False
        except tweepy.Forbidden as e:
            logger.error(f"   ✗ 403 Forbidden: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"   レスポンス本文: {e.response.text[:500]}")
            logger.error("\n   → 書き込み権限がありません。以下を確認してください:")
            logger.error("   1. X Developer Portalでアプリの権限が「Read and write」になっているか")
            logger.error("   2. 権限変更後にAccess Tokenを再生成したか")
            logger.error("   3. アプリの状態が「Pending approval」や「SUSPENDED」になっていないか")
            return False
        except tweepy.Unauthorized as e:
            logger.error(f"   ✗ 401 Unauthorized: {e}")
            logger.error("   → 認証情報が無効です。Access Tokenを再生成してください。")
            return False
        except Exception as e:
            logger.error(f"   ✗ エラー: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   レスポンス: {e.response}")
                if hasattr(e.response, 'text'):
                    logger.error(f"   レスポンス本文: {e.response.text[:500]}")
            return False
        
    except Exception as e:
        logger.error(f"クライアント作成エラー: {e}")
        return False


def main():
    """メイン関数"""
    from config import Config
    
    logger.info("="*60)
    logger.info("アプリの権限と状態を診断します")
    logger.info("="*60)
    
    results = []
    
    # 365botGary
    logger.info("\n[365botGary]")
    credentials_365bot = Config.get_twitter_credentials_365bot()
    result_365bot = diagnose_account("365botGary", credentials_365bot)
    results.append(("365botGary", result_365bot))
    
    # pursahsgospel
    logger.info("\n[pursahsgospel]")
    credentials_pursahs = Config.get_twitter_credentials_pursahs()
    result_pursahs = diagnose_account("pursahsgospel", credentials_pursahs)
    results.append(("pursahsgospel", result_pursahs))
    
    # 結果サマリー
    logger.info("\n" + "="*60)
    logger.info("診断結果サマリー")
    logger.info("="*60)
    for account_name, result in results:
        status = "✓ 成功" if result else "✗ 失敗"
        logger.info(f"{account_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    logger.info(f"\n成功: {success_count}/{len(results)} 件")


if __name__ == "__main__":
    main()

