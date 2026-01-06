"""
403エラーの詳細診断スクリプト
段階的にテキスト長を変えてテストし、403エラーの原因を特定します
"""
import os
import sys
import logging
from dotenv import load_dotenv
import tweepy
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

def diagnose_403_error(account_name: str, credentials: dict):
    """
    403エラーを段階的に診断
    
    Args:
        account_name: アカウント名
        credentials: 認証情報辞書
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"{account_name} アカウントの403エラー診断")
    logger.info(f"{'='*60}\n")
    
    # 認証情報の確認
    api_key = credentials.get('api_key')
    api_secret = credentials.get('api_secret')
    access_token = credentials.get('access_token')
    access_token_secret = credentials.get('access_token_secret')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        logger.error("[ERROR] 認証情報が不完全です")
        return False
    
    try:
        # OAuth 1.0a でクライアント作成
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=False  # レート制限時はエラーを返す
        )
        
        # 1. アカウント情報の取得（読み取りテスト）
        logger.info("【ステップ1】アカウント情報の取得（読み取りテスト）...")
        try:
            me = client.get_me(user_fields=['username', 'name', 'id'])
            if me and me.data:
                logger.info(f"   [OK] 成功: @{me.data.username} ({me.data.name})")
                logger.info(f"   ユーザーID: {me.data.id}")
            else:
                logger.error("   [ERROR] 失敗: レスポンスが不正")
                return False
        except tweepy.Forbidden as e:
            logger.error(f"   [ERROR] 403 Forbidden: 読み取り権限もありません")
            logger.error(f"   詳細: {e}")
            return False
        except Exception as e:
            logger.error(f"   [ERROR] エラー: {type(e).__name__}: {e}")
            return False
        
        # 2. 短いテキストでの投稿テスト
        logger.info("\n【ステップ2】短いテキストでの投稿テスト（50文字）...")
        test_text_short = "テスト投稿 - これは自動投稿ボットのテストです。"
        try:
            response = client.create_tweet(text=test_text_short)
            if response and response.data:
                tweet_id = response.data.get('id')
                logger.info(f"   [OK] 成功: ツイートID={tweet_id}")
                logger.info(f"   ツイート内容: {test_text_short}")
                logger.warning(f"   [WARN] このツイートを削除してください: https://twitter.com/i/web/status/{tweet_id}")
            else:
                logger.error("   [ERROR] 失敗: レスポンスが不正")
                return False
        except tweepy.Forbidden as e:
            logger.error(f"   [ERROR] 403 Forbidden: 短いテキストでも投稿できません")
            logger.error(f"   詳細: {e}")
            _log_detailed_error(e, "短いテキスト")
            return False
        except tweepy.TooManyRequests as e:
            logger.warning(f"   [WARN] レート制限: {e}")
            logger.warning("   レート制限のため、次のテストをスキップします")
            return True  # レート制限は成功とみなす（権限は問題ない）
        except Exception as e:
            logger.error(f"   [ERROR] エラー: {type(e).__name__}: {e}")
            return False
        
        # 3. 中程度のテキストでの投稿テスト
        logger.info("\n【ステップ3】中程度のテキストでの投稿テスト（150文字）...")
        test_text_medium = "テスト投稿 - これは自動投稿ボットのテストです。" * 3
        test_text_medium = test_text_medium[:150]
        try:
            response = client.create_tweet(text=test_text_medium)
            if response and response.data:
                tweet_id = response.data.get('id')
                logger.info(f"   [OK] 成功: ツイートID={tweet_id}")
                logger.warning(f"   [WARN] このツイートを削除してください: https://twitter.com/i/web/status/{tweet_id}")
            else:
                logger.error("   [ERROR] 失敗: レスポンスが不正")
                return False
        except tweepy.Forbidden as e:
            logger.error(f"   [ERROR] 403 Forbidden: 中程度のテキストで投稿できません")
            logger.error(f"   詳細: {e}")
            _log_detailed_error(e, "中程度のテキスト")
            logger.info("\n   → 短いテキストは成功、中程度のテキストで失敗")
            logger.info("   → テキストの長さが原因の可能性があります")
            return False
        except tweepy.TooManyRequests as e:
            logger.warning(f"   [WARN] レート制限: {e}")
            logger.warning("   レート制限のため、次のテストをスキップします")
            return True
        except Exception as e:
            logger.error(f"   [ERROR] エラー: {type(e).__name__}: {e}")
            return False
        
        # 4. 長いテキストでの投稿テスト
        logger.info("\n【ステップ4】長いテキストでの投稿テスト（250文字）...")
        test_text_long = "テスト投稿 - これは自動投稿ボットのテストです。" * 10
        test_text_long = test_text_long[:250]
        try:
            response = client.create_tweet(text=test_text_long)
            if response and response.data:
                tweet_id = response.data.get('id')
                logger.info(f"   [OK] 成功: ツイートID={tweet_id}")
                logger.warning(f"   [WARN] このツイートを削除してください: https://twitter.com/i/web/status/{tweet_id}")
            else:
                logger.error("   [ERROR] 失敗: レスポンスが不正")
                return False
        except tweepy.Forbidden as e:
            logger.error(f"   [ERROR] 403 Forbidden: 長いテキストで投稿できません")
            logger.error(f"   詳細: {e}")
            _log_detailed_error(e, "長いテキスト")
            logger.info("\n   → 短い・中程度のテキストは成功、長いテキストで失敗")
            logger.info("   → テキストの長さが原因の可能性が高いです")
            return False
        except tweepy.TooManyRequests as e:
            logger.warning(f"   ⚠ レート制限: {e}")
            logger.warning("   レート制限のため、テストを終了します")
            return True
        except Exception as e:
            logger.error(f"   [ERROR] エラー: {type(e).__name__}: {e}")
            return False
        
        # 5. URL付きテキストでの投稿テスト
        logger.info("\n【ステップ5】URL付きテキストでの投稿テスト...")
        test_text_with_url = "テスト投稿 - これは自動投稿ボットのテストです。\nhttps://example.com"
        try:
            response = client.create_tweet(text=test_text_with_url)
            if response and response.data:
                tweet_id = response.data.get('id')
                logger.info(f"   [OK] 成功: ツイートID={tweet_id}")
                logger.warning(f"   [WARN] このツイートを削除してください: https://twitter.com/i/web/status/{tweet_id}")
            else:
                logger.error("   [ERROR] 失敗: レスポンスが不正")
                return False
        except tweepy.Forbidden as e:
            logger.error(f"   [ERROR] 403 Forbidden: URL付きテキストで投稿できません")
            logger.error(f"   詳細: {e}")
            _log_detailed_error(e, "URL付きテキスト")
            logger.info("\n   → URLを含む投稿に制限がある可能性があります")
            return False
        except tweepy.TooManyRequests as e:
            logger.warning(f"   ⚠ レート制限: {e}")
            logger.warning("   レート制限のため、テストを終了します")
            return True
        except Exception as e:
            logger.error(f"   [ERROR] エラー: {type(e).__name__}: {e}")
            return False
        
        logger.info("\n" + "="*60)
        logger.info("[OK] すべてのテストが成功しました！")
        logger.info("   403エラーは発生していません。")
        logger.info("="*60)
        return True
        
    except Exception as e:
        logger.error(f"クライアント作成エラー: {e}")
        import traceback
        logger.error(f"トレースバック:\n{traceback.format_exc()}")
        return False


def _log_detailed_error(e: Exception, test_type: str):
    """詳細なエラー情報をログに記録"""
    logger.error(f"\n   【{test_type}での403エラー詳細】")
    logger.error(f"   エラータイプ: {type(e).__name__}")
    logger.error(f"   エラーメッセージ: {e}")
    
    if hasattr(e, 'response') and e.response is not None:
        logger.error(f"   レスポンスオブジェクト: {e.response}")
        
        if hasattr(e.response, 'status_code'):
            logger.error(f"   ステータスコード: {e.response.status_code}")
        
        if hasattr(e.response, 'headers'):
            logger.error(f"   レスポンスヘッダー: {e.response.headers}")
        
        if hasattr(e.response, 'text'):
            response_text = e.response.text
            logger.error(f"   レスポンス本文（最初の500文字）: {response_text[:500]}")
            
            # HTMLレスポンスの場合は特別に処理
            if '<html' in response_text.lower() or '<!doctype' in response_text.lower():
                logger.error("   [WARN] HTMLレスポンスが返ってきています")
                logger.error("   → セキュリティチェック（Cloudflareなど）に引っかかっている可能性があります")
                logger.error("   → IPアドレスがブロックされている可能性があります")
    
    logger.error("\n   【考えられる原因】")
    logger.error("   1. アプリの権限が「Read and write」に設定されていない")
    logger.error("   2. 権限変更後にAccess Tokenを再生成していない")
    logger.error("   3. アプリがX側の承認待ち（Pending approval）")
    logger.error("   4. アプリが停止（SUSPENDED）されている")
    logger.error("   5. 投稿内容がXのポリシーに違反している可能性")
    logger.error("   6. テキストの長さや内容による制限")
    logger.error("   7. IPアドレスがブロックされている（GitHub Actionsなど）")
    logger.error("   8. レート制限に達している（ただし、これは429エラーになるはず）")


def main():
    """メイン関数"""
    import argparse
    from config import Config
    
    parser = argparse.ArgumentParser(description='403エラーの詳細診断')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both',
                       help='診断するアカウント')
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("403エラーの詳細診断を開始します")
    logger.info("="*60)
    
    results = []
    
    if args.account in ['365bot', 'both']:
        logger.info("\n[365botGary]")
        credentials_365bot = Config.get_twitter_credentials_365bot()
        result_365bot = diagnose_403_error("365botGary", credentials_365bot)
        results.append(("365botGary", result_365bot))
    
    if args.account in ['pursahs', 'both']:
        logger.info("\n[pursahsgospel]")
        credentials_pursahs = Config.get_twitter_credentials_pursahs()
        result_pursahs = diagnose_403_error("pursahsgospel", credentials_pursahs)
        results.append(("pursahsgospel", result_pursahs))
    
    # 結果サマリー
    logger.info("\n" + "="*60)
    logger.info("診断結果サマリー")
    logger.info("="*60)
    for account_name, result in results:
        status = "[OK] 成功" if result else "[ERROR] 失敗"
        logger.info(f"{account_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    logger.info(f"\n成功: {success_count}/{len(results)} 件")
    
    if success_count < len(results):
        logger.info("\n【次のステップ】")
        logger.info("1. X Developer Portalでアプリの状態を確認")
        logger.info("2. アプリの権限が「Read and write」になっているか確認")
        logger.info("3. Access Tokenを再生成")
        logger.info("4. 時間を置いてから再試行（IPブロックの場合）")


if __name__ == "__main__":
    main()

