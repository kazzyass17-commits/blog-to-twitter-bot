"""
900秒ごとに投稿テストを実行し、文字数の上限を確認
本番で使うものと同じ形式で投稿（文字数以外）
"""
import os
import sys
from dotenv import load_dotenv
import logging
import time
import json
from datetime import datetime
from config import Config
from database import PostDatabase
from blog_fetcher import BlogFetcher
from twitter_poster import TwitterPoster
import tweepy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# tweepyのレート制限警告を適切に処理
# wait_on_rate_limit=Trueを設定している場合、警告メッセージは正常な動作です
# レート制限に達すると、自動的に待機して再試行します
tweepy_logger = logging.getLogger('tweepy.client')
# レート制限の警告はINFOレベルで表示（正常な動作なので）
tweepy_logger.setLevel(logging.INFO)

load_dotenv()

# テスト状態を保存するファイル
STATE_FILE = "test_post_state.json"

# テストする文字数のリスト（段階的に長くする）
TEST_LENGTHS = [50, 100, 150, 200, 230, 250, 270, 280]

# 900秒 = 15分（同じアカウントの次の文字数テストまで）
INTERVAL_SECONDS = 900

# 265秒 = アカウント間（365botGary ↔ pursahsgospel）の待機時間
ACCOUNT_INTERVAL_SECONDS = 265


def load_test_state():
    """テスト状態を読み込む"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"状態ファイルの読み込みエラー: {e}")
    return {
        'current_account_index': 0,
        'current_length_index': 0,
        'accounts': ['365botGary', 'pursahsgospel'],
        'results': []
    }


def save_test_state(state):
    """テスト状態を保存"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"状態ファイルの保存エラー: {e}")


def get_test_post_data(blog_url: str, twitter_handle: str):
    """テスト用の投稿データを取得（本番と同じ形式）"""
    try:
        # データベースからランダムに投稿を取得
        db = PostDatabase()
        post_data = db.get_random_unposted_post(blog_url, twitter_handle)
        
        if not post_data:
            logger.warning("未投稿の投稿がありません。")
            return None
        
        page_url = post_data.get('link', '')
        if not page_url:
            logger.warning("URLが取得できませんでした")
            return None
        
        # ページからコンテンツを取得
        logger.info("ページからコンテンツを取得中...")
        fetcher = BlogFetcher(page_url)
        page_content = fetcher.fetch_latest_post()
        
        if not page_content:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url}")
            return None
        
        return {
            'title': page_content.get('title', ''),
            'content': page_content.get('content', ''),
            'link': page_content.get('link', page_url),
            'url': page_url
        }
    except Exception as e:
        logger.error(f"投稿データ取得エラー: {e}", exc_info=True)
        return None


def format_text_for_length(base_text: str, target_length: int, url: str):
    """指定された長さになるようにテキストをフォーマット（本番と同じ形式を保つ）"""
    # URLは23文字 + 改行1文字 = 24文字（Twitter APIが自動的に短縮）
    available_text_length = target_length - 24
    
    if available_text_length < 0:
        return None
    
    # テキストを切り詰める（本番と同じロジックを使用）
    if len(base_text) > available_text_length:
        # 本番と同じ方法で切り詰める（TwitterPoster.format_blog_postと同じロジック）
        content_preview = base_text[:available_text_length]
        # 最後の文字が途中で切れないように調整（単語境界で切る）
        if available_text_length > 0:
            last_part = content_preview[-50:] if len(content_preview) > 50 else content_preview
            for punct in ['。', '.', '、', ',', '！', '!', '？', '?', '\n']:
                if punct in last_part:
                    content_preview = content_preview[:content_preview.rfind(punct) + 1]
                    break
        test_text = content_preview
    else:
        test_text = base_text
    
    return test_text


def test_post_with_length(account_name: str, credentials: dict, post_data: dict, target_length: int):
    """指定された文字数で投稿テストを実行"""
    logger.info(f"\n{'='*60}")
    logger.info(f"{account_name} - 文字数 {target_length} のテスト投稿")
    logger.info(f"{'='*60}\n")
    
    try:
        # Twitter投稿テキストをフォーマット（本番と同じ形式）
        poster = TwitterPoster(credentials)
        base_tweet_text = poster.format_blog_post(
            title=post_data.get('title', ''),
            content=post_data.get('content', ''),
            link=post_data.get('link', post_data.get('url', ''))
        )
        
        # 指定された長さになるように調整
        tweet_text = format_text_for_length(base_tweet_text, target_length, post_data.get('url', ''))
        
        if not tweet_text:
            logger.warning(f"  長さ {target_length}: スキップ（URL分を引くと負の値）")
            return {
                'length': target_length,
                'success': False,
                'error': '長さが負の値'
            }
        
        # 実際の投稿形式（テキスト + 改行 + URL）
        actual_tweet_text = f"{tweet_text}\n{post_data.get('url', '')}"
        
        # Twitter APIがカウントする文字数（URLは23文字）
        twitter_counted_length = len(tweet_text) + 1 + 23
        actual_length = len(actual_tweet_text)
        
        logger.info(f"  テキスト長: {len(tweet_text)} 文字")
        logger.info(f"  Twitterカウント: {twitter_counted_length} 文字")
        logger.info(f"  実際の長さ: {actual_length} 文字")
        logger.info(f"  投稿内容（最初の100文字）: {tweet_text[:100]}...")
        
        # クライアントを作成
        # wait_on_rate_limit=False: レート制限時はエラーを返す（手動で処理）
        # これにより、投稿失敗とレート制限を明確に区別できる
        client = tweepy.Client(
            consumer_key=credentials.get('api_key'),
            consumer_secret=credentials.get('api_secret'),
            access_token=credentials.get('access_token'),
            access_token_secret=credentials.get('access_token_secret'),
            wait_on_rate_limit=False  # レート制限時はエラーを返す（手動で処理）
        )
        
        # 投稿実行
        logger.info("  投稿中...")
        response = client.create_tweet(text=actual_tweet_text)
        
        if response and response.data:
            tweet_id = response.data.get('id')
            logger.info(f"  ✓ 投稿成功!")
            logger.info(f"  ツイートID: {tweet_id}")
            logger.info(f"  ツイートURL: https://twitter.com/i/web/status/{tweet_id}")
            logger.warning(f"  ⚠ このツイートはテスト投稿です。確認後、削除してください。")
            
            return {
                'length': target_length,
                'text_length': len(tweet_text),
                'twitter_counted_length': twitter_counted_length,
                'actual_length': actual_length,
                'success': True,
                'tweet_id': tweet_id,
                'tweet_url': f"https://twitter.com/i/web/status/{tweet_id}",
                'timestamp': datetime.now().isoformat()
            }
        else:
            logger.error("  ✗ 投稿失敗: レスポンスが不正")
            logger.error(f"  レスポンス: {response}")
            return {
                'length': target_length,
                'text_length': len(tweet_text),
                'twitter_counted_length': twitter_counted_length,
                'actual_length': actual_length,
                'success': False,
                'error': 'レスポンスが不正',
                'response': str(response) if response else 'None'
            }
            
    except tweepy.Forbidden as e:
        logger.error(f"  ✗ 403 Forbidden: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"  レスポンス: {e.response}")
            if hasattr(e.response, 'text'):
                logger.error(f"  レスポンス本文: {e.response.text[:500]}")
        return {
            'length': target_length,
            'text_length': len(tweet_text) if 'tweet_text' in locals() else 0,
            'success': False,
            'error': '403 Forbidden',
            'error_detail': str(e),
            'response_text': e.response.text[:500] if hasattr(e, 'response') and hasattr(e.response, 'text') else None
        }
    except tweepy.TooManyRequests as e:
        # レート制限エラー
        logger.error(f"  ✗ レート制限: {e}")
        if hasattr(e, 'response') and e.response is not None:
            # レート制限の詳細情報を取得
            if hasattr(e.response, 'headers'):
                rate_limit_reset = e.response.headers.get('x-rate-limit-reset')
                if rate_limit_reset:
                    import time
                    wait_seconds = int(rate_limit_reset) - int(time.time())
                    logger.warning(f"  レート制限のリセットまで: {wait_seconds} 秒（{wait_seconds // 60} 分）")
                    logger.warning(f"  次回の実行（900秒後）まで待機してください")
        return {
            'length': target_length,
            'text_length': len(tweet_text) if 'tweet_text' in locals() else 0,
            'success': False,
            'error': 'レート制限',
            'error_detail': str(e),
            'rate_limit_reset': e.response.headers.get('x-rate-limit-reset') if hasattr(e, 'response') and hasattr(e.response, 'headers') else None
        }
    except Exception as e:
        logger.error(f"  ✗ エラー: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"  トレースバック:\n{traceback.format_exc()}")
        return {
            'length': target_length,
            'text_length': len(tweet_text) if 'tweet_text' in locals() else 0,
            'success': False,
            'error': type(e).__name__,
            'error_detail': str(e)
        }


def main():
    """メイン関数 - 900秒ごとに投稿テストを実行（1回で1アカウントのみ）"""
    logger.info("="*60)
    logger.info("900秒ごとの投稿テスト（文字数上限確認）")
    logger.info("="*60)
    logger.info("注意: 1回の実行で1つのアカウントのみをテストします")
    logger.info("      アカウント間のレート制限を避けるため、900秒待機します")
    logger.info("="*60)
    
    # テスト状態を読み込む
    state = load_test_state()
    
    account_name = state['accounts'][state['current_account_index']]
    length_index = state['current_length_index']
    
    if length_index >= len(TEST_LENGTHS):
        # すべての文字数をテスト済み
        logger.info(f"\n{account_name} のすべての文字数テストが完了しました。")
        logger.info("結果サマリー:")
        for result in state['results']:
            if result.get('account') == account_name:
                status = "✓" if result.get('success') else "✗"
                logger.info(f"  {status} 文字数 {result.get('length')}: {result.get('error', '成功')}")
        
        # 次のアカウントに進む
        state['current_account_index'] = (state['current_account_index'] + 1) % len(state['accounts'])
        state['current_length_index'] = 0
        
        if state['current_account_index'] == 0:
            # すべてのアカウントのテストが完了
            logger.info("\nすべてのアカウントのテストが完了しました。最初から再開します。")
        
        save_test_state(state)
        return
    
    target_length = TEST_LENGTHS[length_index]
    
    # 認証情報を取得
    if account_name == "365botGary":
        credentials = Config.get_twitter_credentials_365bot()
        blog_url = Config.BLOG_365BOT_URL
        twitter_handle = Config.TWITTER_365BOT_HANDLE
    else:
        credentials = Config.get_twitter_credentials_pursahs()
        blog_url = Config.BLOG_PURSAHS_URL
        twitter_handle = Config.TWITTER_PURSAHS_HANDLE
    
    if not credentials.get('api_key') or not credentials.get('access_token'):
        logger.error(f"{account_name} の認証情報が設定されていません")
        return
    
    # テスト用の投稿データを取得（本番と同じ形式）
    logger.info(f"\n{account_name} のテスト投稿データを取得中...")
    post_data = get_test_post_data(blog_url, twitter_handle)
    
    if not post_data:
        logger.error(f"{account_name} の投稿データを取得できませんでした")
        return
    
    logger.info(f"選択された投稿: {post_data.get('title', '')}")
    logger.info(f"URL: {post_data.get('url', '')}")
    
    # 投稿テストを実行
    result = test_post_with_length(account_name, credentials, post_data, target_length)
    
    # 結果を保存
    result['account'] = account_name
    state['results'].append(result)
    
    # 次のテストに進む
    state['current_length_index'] += 1
    
    save_test_state(state)
    
    # 結果サマリー
    logger.info(f"\n{'='*60}")
    logger.info("テスト結果")
    logger.info(f"{'='*60}")
    status = "✓ 成功" if result.get('success') else f"✗ 失敗 ({result.get('error', '不明')})"
    logger.info(f"{account_name} - 文字数 {target_length}: {status}")
    if result.get('tweet_id'):
        logger.warning(f"  削除してください: {result.get('tweet_url')}")
    
    # 次のアカウントに進むか、同じアカウントの次の文字数に進むか
    next_account_index = state['current_account_index']
    next_length_index = state['current_length_index']
    
    # アカウントが切り替わるかどうかを判定
    account_switching = next_length_index >= len(TEST_LENGTHS)
    
    if account_switching:
        # このアカウントのすべての文字数をテスト済み → 次のアカウントに進む
        next_account_index = (state['current_account_index'] + 1) % len(state['accounts'])
        next_length_index = 0
        next_account_name = state['accounts'][next_account_index]
        wait_seconds = ACCOUNT_INTERVAL_SECONDS  # アカウント間は265秒
        logger.info(f"\n{account_name} のすべての文字数テストが完了しました。")
        logger.info(f"次回は {next_account_name} のテストを開始します。")
        logger.info(f"（アカウント間のレート制限を避けるため、{wait_seconds}秒待機します）")
    else:
        next_account_name = account_name
        wait_seconds = INTERVAL_SECONDS  # 同じアカウントの次の文字数は900秒
        logger.info(f"\n次回は同じアカウント（{account_name}）の次の文字数をテストします。")
        logger.info(f"（同じアカウントの次の文字数テストまで、{wait_seconds}秒待機します）")
    
    # 次の実行までの待機時間を表示
    logger.info(f"\n次のテストまで {wait_seconds} 秒（{wait_seconds // 60} 分）待機します...")
    logger.info(f"次回テスト: {next_account_name} - 文字数 {TEST_LENGTHS[next_length_index] if next_length_index < len(TEST_LENGTHS) else '完了'}")


if __name__ == "__main__":
    main()

