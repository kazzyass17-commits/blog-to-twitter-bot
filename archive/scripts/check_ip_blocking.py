"""
GitHub ActionsのIPアドレスがブロックされているか確認するスクリプト
"""
import requests
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ip_and_api_access():
    """IPアドレスとAPIアクセスを確認"""
    logger.info("=" * 60)
    logger.info("IPアドレスとAPIアクセスの確認")
    logger.info("=" * 60)
    
    # 1. 現在のIPアドレスを確認
    try:
        logger.info("\n1. 現在のIPアドレスを確認中...")
        ip_response = requests.get("https://api.ipify.org?format=json", timeout=10)
        if ip_response.status_code == 200:
            ip_data = ip_response.json()
            current_ip = ip_data.get('ip', 'Unknown')
            logger.info(f"   現在のIPアドレス: {current_ip}")
        else:
            logger.warning("   IPアドレスの取得に失敗しました")
            current_ip = "Unknown"
    except Exception as e:
        logger.warning(f"   IPアドレスの取得エラー: {e}")
        current_ip = "Unknown"
    
    # 2. X APIへのアクセステスト（Bearer Tokenのみ）
    logger.info("\n2. X APIへのアクセステスト（Bearer Tokenのみ）...")
    logger.info("   エンドポイント: GET https://api.x.com/2/tweets/search/recent")
    
    # Bearer Tokenは環境変数から取得（テスト用の簡単なエンドポイント）
    import os
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("TWITTER_365BOT_BEARER_TOKEN")
    
    if not bearer_token:
        logger.warning("   Bearer Tokenが設定されていません。スキップします。")
        return
    
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 簡単なエンドポイントでテスト（認証が必要だが、IPブロックを確認できる）
    test_url = "https://api.x.com/2/tweets/search/recent?query=test&max_results=10"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=30)
        
        logger.info(f"   ステータスコード: {response.status_code}")
        logger.info(f"   レスポンスヘッダー: {dict(response.headers)}")
        
        if response.status_code == 200:
            logger.info("   ✓ APIアクセス成功（IPブロックされていません）")
            return True
        elif response.status_code == 403:
            logger.error("   ✗ 403 Forbidden: IPブロックまたは認証エラーの可能性")
            
            # レスポンス本文を確認
            response_text = response.text[:500]
            logger.info(f"   レスポンス本文（最初の500文字）: {response_text}")
            
            if '<!DOCTYPE html>' in response_text or '<html' in response_text:
                logger.error("   ⚠️ HTMLレスポンスが返ってきました。")
                logger.error("     これは、セキュリティチェック（Cloudflareなど）に引っかかっている可能性があります。")
                logger.error("     GitHub ActionsのIPアドレスがブロックされている可能性が高いです。")
            else:
                logger.error("   JSONレスポンスが返ってきています。")
                logger.error("     認証エラーまたはアプリの権限の問題の可能性があります。")
            
            return False
        elif response.status_code == 401:
            logger.error("   ✗ 401 Unauthorized: 認証エラー")
            logger.error("     Bearer Tokenが無効または期限切れの可能性があります。")
            return False
        else:
            logger.error(f"   ✗ 予期しないステータスコード: {response.status_code}")
            logger.error(f"   レスポンス本文: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"   ✗ リクエストエラー: {e}")
        return False
    except Exception as e:
        logger.error(f"   ✗ 予期しないエラー: {e}")
        import traceback
        logger.error(f"   トレースバック:\n{traceback.format_exc()}")
        return False


def check_github_actions_environment():
    """GitHub Actions環境かどうかを確認"""
    logger.info("\n3. 実行環境の確認...")
    
    github_actions = os.getenv("GITHUB_ACTIONS")
    github_runner_os = os.getenv("RUNNER_OS")
    github_workflow = os.getenv("GITHUB_WORKFLOW")
    
    if github_actions == "true":
        logger.info("   ✓ GitHub Actions環境で実行されています")
        logger.info(f"   OS: {github_runner_os}")
        logger.info(f"   Workflow: {github_workflow}")
        logger.info("   ⚠️ GitHub ActionsのIPアドレスは動的に変わる可能性があります")
        logger.info("   ⚠️ X側でGitHub ActionsのIPアドレスがブロックされている可能性があります")
        return True
    else:
        logger.info("   ✓ ローカル環境で実行されています")
        return False


if __name__ == "__main__":
    import os
    
    check_github_actions_environment()
    check_ip_and_api_access()
    
    logger.info("\n" + "=" * 60)
    logger.info("確認完了")
    logger.info("=" * 60)
    logger.info("\n推奨される対処法:")
    logger.info("1. しばらく待ってから再試行（1時間〜数時間）")
    logger.info("2. 別の時間帯に再試行")
    logger.info("3. ローカル環境でテストして、IPブロックかどうか確認")
    logger.info("4. X Developer Portalでアプリの状態を確認")




