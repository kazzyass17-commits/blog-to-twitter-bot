"""
Twitter API v2の接続テスト（curlコマンド相当）
提供されたcurlコマンドをPythonで実行
"""
import requests
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .envファイルを読み込む
load_dotenv()

def test_api_v2_with_bearer_token():
    """Bearer Tokenを使用してAPI v2をテスト"""
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not bearer_token:
        logger.error("TWITTER_BEARER_TOKENが設定されていません")
        return False
    
    # 提供されたcurlコマンドをPythonで実行
    url = "https://api.x.com/2/tweets"
    params = {
        'ids': '1212092628029698048',
        'tweet.fields': 'attachments,author_id,context_annotations,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,text,withheld',
        'expansions': 'referenced_tweets.id'
    }
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    
    try:
        logger.info("Twitter API v2に接続中...")
        logger.info(f"URL: {url}")
        logger.info(f"Tweet ID: {params['ids']}")
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        logger.info(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✓ API接続成功！")
            
            if 'data' in data and len(data['data']) > 0:
                tweet = data['data'][0]
                logger.info(f"  ツイートID: {tweet.get('id')}")
                logger.info(f"  テキスト: {tweet.get('text', '')[:100]}...")
                logger.info(f"  作成日時: {tweet.get('created_at')}")
                if 'public_metrics' in tweet:
                    metrics = tweet['public_metrics']
                    logger.info(f"  いいね数: {metrics.get('like_count', 0)}")
                    logger.info(f"  リツイート数: {metrics.get('retweet_count', 0)}")
            else:
                logger.warning("  ツイートデータが見つかりませんでした")
            
            return True
        else:
            logger.error(f"✗ API接続失敗: {response.status_code}")
            logger.error(f"  レスポンス: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ リクエストエラー: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ 予期しないエラー: {e}")
        return False


def test_api_v2_with_oauth():
    """OAuth 1.0aを使用してAPI v2をテスト（投稿用）"""
    from config import Config
    
    credentials = Config.get_twitter_credentials_365bot()
    
    if not all([
        credentials.get('api_key'),
        credentials.get('api_secret'),
        credentials.get('access_token'),
        credentials.get('access_token_secret')
    ]):
        logger.error("認証情報が不足しています")
        return False
    
    # OAuth 1.0aでリクエストを送信
    import requests_oauthlib
    from requests_oauthlib import OAuth1
    
    auth = OAuth1(
        credentials.get('api_key'),
        credentials.get('api_secret'),
        credentials.get('access_token'),
        credentials.get('access_token_secret')
    )
    
    url = "https://api.x.com/2/tweets"
    params = {
        'ids': '1212092628029698048',
        'tweet.fields': 'created_at,text,public_metrics'
    }
    
    try:
        logger.info("OAuth 1.0aでTwitter API v2に接続中...")
        response = requests.get(url, params=params, auth=auth, timeout=30)
        
        logger.info(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✓ OAuth接続成功！")
            return True
        else:
            logger.error(f"✗ OAuth接続失敗: {response.status_code}")
            logger.error(f"  レスポンス: {response.text[:200]}")
            return False
            
    except Exception as e:
        logger.error(f"✗ エラー: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter API v2接続テスト')
    parser.add_argument('--method', choices=['bearer', 'oauth', 'both'], default='bearer',
                       help='テスト方法（bearer: Bearer Token, oauth: OAuth 1.0a）')
    
    args = parser.parse_args()
    
    success_count = 0
    
    if args.method in ['bearer', 'both']:
        logger.info("=" * 60)
        logger.info("Bearer Tokenでのテスト")
        logger.info("=" * 60)
        if test_api_v2_with_bearer_token():
            success_count += 1
    
    if args.method in ['oauth', 'both']:
        logger.info("\n" + "=" * 60)
        logger.info("OAuth 1.0aでのテスト")
        logger.info("=" * 60)
        if test_api_v2_with_oauth():
            success_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"テスト完了: {success_count} 件成功")
    logger.info("=" * 60)




