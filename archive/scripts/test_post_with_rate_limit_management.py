"""
投稿テストスクリプト（レート制限管理付き）
レート制限が発生した場合、待機時間を管理し、自動的に再実行する
2つのアカウントの待機時間を個別に管理する
"""
import logging
import sys
import json
import os
import time
from datetime import datetime, timedelta
from database import PostDatabase
from twitter_poster import TwitterPoster
from blog_fetcher import BlogFetcher
from config import Config
import tweepy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 待機時間管理ファイル
RATE_LIMIT_STATE_FILE = "rate_limit_state.json"


def load_rate_limit_state():
    """待機時間の状態を読み込む"""
    if os.path.exists(RATE_LIMIT_STATE_FILE):
        try:
            with open(RATE_LIMIT_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"状態ファイルの読み込みエラー: {e}")
    return {
        '365bot': {
            'wait_until': None,
            'reset_time': None
        },
        'pursahs': {
            'wait_until': None,
            'reset_time': None
        }
    }


def save_rate_limit_state(state):
    """待機時間の状態を保存する"""
    try:
        with open(RATE_LIMIT_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"状態ファイルの保存エラー: {e}")


def check_and_wait_for_account(account_key: str, account_name: str):
    """
    アカウントの待機時間をチェックし、必要に応じて待機する
    
    Returns:
        True: 待機が完了した、または待機不要（投稿可能）
        False: 待機中（投稿不可）
    """
    state = load_rate_limit_state()
    account_state = state.get(account_key, {})
    
    wait_until_str = account_state.get('wait_until')
    if wait_until_str:
        wait_until = datetime.fromisoformat(wait_until_str)
        now = datetime.now()
        
        if wait_until > now:
            # まだ待機中
            wait_seconds = (wait_until - now).total_seconds()
            print(f"\n{'='*60}")
            print(f"{account_name} アカウント: レート制限待機中")
            print(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"次の実行予定時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
            print(f"{'='*60}")
            sys.stdout.flush()
            logger.info(f"\n{'='*60}")
            logger.info(f"{account_name} アカウント: レート制限待機中")
            logger.info(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"次の実行予定時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
            logger.info(f"{'='*60}")
            
            # 待機時間が長い場合（5分以上）は、定期的に残り時間を表示しながら待機
            if wait_seconds > 300:  # 5分以上
                logger.info("待機中にコードを修正できます。")
                logger.info("修正が完了したら、このスクリプトを再実行してください。")
                logger.info(f"待機時間が終わったら自動的に再実行されます。")
                logger.info(f"{'='*60}\n")
                
                # 待機中に修正を行えるように、待機時間を表示しながら待機
                last_logged = 0
                while wait_until > datetime.now():
                    remaining = (wait_until - datetime.now()).total_seconds()
                    if remaining > 0:
                        # 1分ごとに残り時間を表示
                        if int(remaining) != last_logged and (int(remaining) % 60 == 0 or remaining < 60):
                            logger.info(f"残り待機時間: {int(remaining)} 秒（{int(remaining // 60)} 分）")
                            logger.info(f"次の実行予定時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                            last_logged = int(remaining)
                        time.sleep(min(60, remaining))  # 最大60秒待機
                    else:
                        break
            else:
                # 短い待機時間の場合は、そのまま待機
                print(f"短い待機時間のため、自動的に待機します。")
                print(f"次の実行予定時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}\n")
                sys.stdout.flush()
                logger.info(f"短い待機時間のため、自動的に待機します。")
                logger.info(f"次の実行予定時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*60}\n")
                time.sleep(wait_seconds)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"待機時間が終了しました。{account_name} アカウントの投稿を再試行します。")
            logger.info(f"{'='*60}")
            # 待機時間をクリア（最新の状態を読み込んでからクリア）
            state = load_rate_limit_state()  # 最新の状態を読み込む
            reset_time_str = state.get(account_key, {}).get('reset_time')
            
            # リセット時刻を確認（Twitter API側で実際にリセットされるまで待機）
            if reset_time_str:
                reset_time = datetime.fromisoformat(reset_time_str)
                now = datetime.now()
                if reset_time > now:
                    # リセット時刻がまだ来ていない場合は、リセット時刻まで待機
                    wait_seconds = (reset_time - now).total_seconds()
                    logger.info(f"{account_name}: リセット時刻まで待機します。")
                    logger.info(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"  現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"  残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                    # 10秒の余裕を持たせる
                    wait_until_reset = reset_time + timedelta(seconds=10)
                    if wait_until_reset > now:
                        wait_seconds = (wait_until_reset - now).total_seconds()
                        time.sleep(wait_seconds)
                        logger.info(f"{account_name}: リセット時刻が過ぎました。投稿を再試行します。")
            
            # 待機時間をクリア
            state = load_rate_limit_state()  # 最新の状態を読み込む
            state[account_key] = {
                'wait_until': None,
                'reset_time': None
            }
            save_rate_limit_state(state)
            logger.info(f"{account_name}: 待機時間をクリアしました")
            return True  # 待機完了、投稿可能
        else:
            # 待機時間が過ぎている場合はクリア（最新の状態を読み込んでからクリア）
            logger.info(f"\n{'='*60}")
            logger.info(f"{account_name} アカウント: 待機時間が過ぎています。クリアします。")
            logger.info(f"{'='*60}")
            state = load_rate_limit_state()  # 最新の状態を読み込む
            state[account_key] = {
                'wait_until': None,
                'reset_time': None
            }
            save_rate_limit_state(state)
            logger.info(f"{account_name}: 待機時間をクリアしました（過ぎていた）")
            return True  # 待機不要、投稿可能
    
    # 待機時間がない場合
    return True  # 待機不要、投稿可能


def extract_rate_limit_reset_time(error: tweepy.TooManyRequests) -> Optional[datetime]:
    """レート制限エラーからリセット時刻を抽出する"""
    if hasattr(error, 'response') and error.response is not None:
        if hasattr(error.response, 'headers'):
            rate_limit_reset = error.response.headers.get('x-rate-limit-reset')
            if rate_limit_reset:
                reset_timestamp = int(rate_limit_reset)
                return datetime.fromtimestamp(reset_timestamp)
    return None


def test_post_with_rate_limit_handling(blog_url: str, twitter_handle: str, credentials: dict, account_key: str, account_name: str):
    """
    投稿テストを実行し、レート制限を処理する
    
    Returns:
        (success: bool, should_retry: bool, wait_until: Optional[datetime])
    """
    try:
        db = PostDatabase()
        
        # 未投稿の投稿を取得
        post_data = db.get_random_unposted_post(blog_url, twitter_handle)
        
        if not post_data:
            logger.warning(f"{account_name}: 未投稿の投稿がありません。")
            return False, False, None
        
        page_url = post_data.get('link', '')
        if not page_url:
            logger.warning(f"{account_name}: URLが取得できませんでした")
            return False, False, None
        
        logger.info(f"\n{account_name}: 選択された投稿: {post_data.get('title', '')}")
        logger.info(f"URL: {page_url}")
        
        # ページからコンテンツを取得
        logger.info("ページからコンテンツを取得中...")
        fetcher = BlogFetcher(page_url)
        page_content = fetcher.fetch_latest_post()
        
        if not page_content:
            logger.warning(f"ページコンテンツを取得できませんでした: {page_url}")
            page_content = {
                'title': post_data.get('title', ''),
                'content': '',
                'link': page_url,
                'published_date': '',
                'author': '',
            }
        
        logger.info(f"取得した投稿: {page_content.get('title', 'タイトルなし')}")
        
        # Twitterに投稿
        logger.info(f"[DEBUG] {account_name}: 投稿処理を開始します")
        logger.info(f"[DEBUG] {account_name}: TwitterPosterオブジェクトを作成します")
        poster = TwitterPoster(credentials)
        logger.info(f"[DEBUG] {account_name}: ツイートテキストをフォーマットします")
        tweet_text = poster.format_blog_post(
            title=page_content.get('title', ''),
            content=page_content.get('content', ''),
            link=page_content.get('link', page_url)
        )
        
        logger.info(f"投稿テキスト: {tweet_text}")
        logger.info(f"文字数: {len(tweet_text)} 文字（リンク含む: {len(tweet_text) + 24} 文字）")
        
        # 投稿前に待機時間を再確認（他のプロセスが設定した可能性があるため）
        logger.info(f"[DEBUG] {account_name}: 投稿前に待機時間を確認します")
        state_before_post = load_rate_limit_state()
        account_state_before = state_before_post.get(account_key, {})
        wait_until_before = account_state_before.get('wait_until')
        reset_time_before = account_state_before.get('reset_time')
        
        if wait_until_before:
            wait_until_dt = datetime.fromisoformat(wait_until_before)
            now = datetime.now()
            if wait_until_dt > now:
                wait_seconds = (wait_until_dt - now).total_seconds()
                logger.error(f"{account_name}: 投稿前に待機時間が設定されていました。")
                logger.error(f"  待機終了時刻: {wait_until_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.error(f"  現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.error(f"  残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                logger.error("待機時間が終了するまで待機します。")
                
                # 待機時間が終了するまで待機
                if wait_seconds > 0:
                    time.sleep(wait_seconds)
                    logger.info(f"{account_name}: 待機時間が終了しました。投稿を再試行します。")
                
                # 待機時間をクリア
                state_before_post[account_key] = {
                    'wait_until': None,
                    'reset_time': None
                }
                save_rate_limit_state(state_before_post)
            else:
                # 待機時間が過ぎている場合はクリア
                logger.info(f"{account_name}: 待機時間が過ぎています。クリアします。")
                state_before_post[account_key] = {
                    'wait_until': None,
                    'reset_time': None
                }
                save_rate_limit_state(state_before_post)
        
        # リセット時刻を確認（念のため）
        if reset_time_before:
            reset_time_dt = datetime.fromisoformat(reset_time_before)
            now = datetime.now()
            if reset_time_dt > now:
                remaining = (reset_time_dt - now).total_seconds()
                logger.warning(f"{account_name}: リセット時刻がまだ来ていません。")
                logger.warning(f"  リセット時刻: {reset_time_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.warning(f"  現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.warning(f"  残り時間: {int(remaining)} 秒（{int(remaining // 60)} 分）")
                logger.warning("リセット時刻まで待機します。")
                
                # リセット時刻まで待機（余裕を持たせる）
                wait_until_reset = reset_time_dt + timedelta(seconds=10)  # 10秒の余裕
                if wait_until_reset > now:
                    wait_seconds = (wait_until_reset - now).total_seconds()
                    time.sleep(wait_seconds)
                    logger.info(f"{account_name}: リセット時刻が過ぎました。投稿を再試行します。")
        
        logger.info(f"[DEBUG] {account_name}: post_tweet_with_linkを呼び出します（1回のみ）")
        
        # 文字数オーバー時のリトライ処理
        max_retries_for_length = 3  # 最大3回リトライ
        retry_count_for_length = 0
        current_tweet_text = tweet_text
        result = None  # 結果を初期化
        
        while retry_count_for_length < max_retries_for_length:
            try:
                result = poster.post_tweet_with_link(
                    text=current_tweet_text,
                    link=page_content.get('link', page_url)
                )
                logger.info(f"[DEBUG] {account_name}: post_tweet_with_linkの結果: {result is not None}")
                
                # 成功した場合はループを抜ける
                if result and result.get('success'):
                    break
                elif result is None:
                    # エラーが返されたが、レート制限エラーではない場合
                    # 文字数オーバーの可能性があるので、文字数を減らしてリトライ
                    logger.warning(f"{account_name}: 投稿が失敗しました。文字数を減らしてリトライします。")
                    retry_count_for_length += 1
                    if retry_count_for_length < max_retries_for_length:
                        # 文字数を10%減らす
                        reduction = int(len(current_tweet_text) * 0.1)
                        current_tweet_text = current_tweet_text[:len(current_tweet_text) - reduction]
                        logger.info(f"{account_name}: 文字数を {len(current_tweet_text)} 文字に減らしてリトライします（試行 {retry_count_for_length + 1}/{max_retries_for_length}）")
                        continue
                    else:
                        logger.error(f"{account_name}: 文字数を減らしても投稿に失敗しました。")
                        return False, False, None
                else:
                    # 予期しない結果
                    logger.error(f"{account_name}: 予期しない結果が返されました: {result}")
                    return False, False, None
                    
            except tweepy.TooManyRequests as e:
                # レート制限エラーが発生した場合は、すぐに報告して処理を中断（リトライしない）
                logger.error(f"\n{'='*60}")
                logger.error(f"✗ {account_name}: 投稿試行中にレート制限エラーが発生しました！")
                logger.error(f"{'='*60}")
                logger.error(f"エラー発生時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.error(f"詳細: {e}")
                
                reset_time = extract_rate_limit_reset_time(e)
                if reset_time:
                    wait_until = reset_time + timedelta(minutes=1)
                    wait_seconds = (wait_until - datetime.now()).total_seconds()
                    logger.error(f"レート制限のリセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.error(f"待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.error(f"待機時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                    
                    # 待機時間と原因を保存
                    from rate_limit_checker import record_rate_limit_reason
                    record_rate_limit_reason(
                        account_key=account_key,
                        account_name=account_name,
                        api_endpoint='POST /2/tweets (create_tweet)',
                        error_message=str(e),
                        reset_time=reset_time,
                        wait_until=wait_until
                    )
                    logger.error(f"{account_name}: 待機時間と原因を保存しました。")
                
                logger.error(f"\n{account_name}: レート制限エラーのため、処理を停止します。")
                logger.error(f"待機時間が終了するまで、このアカウントは再試行されません。")
                logger.error(f"{'='*60}\n")
                
                # エラーを再発生させて、呼び出し元で処理できるようにする
                raise
            except (tweepy.BadRequest, tweepy.HTTPException) as e:
                # 文字数オーバーなどの400/422エラーの可能性
                error_message = str(e).lower()
                if 'length' in error_message or 'too long' in error_message or 'exceed' in error_message:
                    # 文字数オーバーエラーの場合
                    logger.warning(f"{account_name}: 文字数オーバーエラーが発生しました。文字数を減らしてリトライします。")
                    logger.warning(f"  エラー詳細: {e}")
                    retry_count_for_length += 1
                    if retry_count_for_length < max_retries_for_length:
                        # 文字数を10%減らす
                        reduction = int(len(current_tweet_text) * 0.1)
                        current_tweet_text = current_tweet_text[:len(current_tweet_text) - reduction]
                        logger.info(f"{account_name}: 文字数を {len(current_tweet_text)} 文字に減らしてリトライします（試行 {retry_count_for_length + 1}/{max_retries_for_length}）")
                        continue
                    else:
                        logger.error(f"{account_name}: 文字数を減らしても投稿に失敗しました。")
                        return False, False, None
                else:
                    # その他の400/422エラー
                    logger.error(f"\n{'='*60}")
                    logger.error(f"✗ {account_name}: 投稿試行中にエラーが発生しました！")
                    logger.error(f"{'='*60}")
                    logger.error(f"エラー発生時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.error(f"エラータイプ: {type(e).__name__}")
                    logger.error(f"詳細: {e}")
                    import traceback
                    logger.error(f"トレースバック:\n{traceback.format_exc()}")
                    logger.error(f"{'='*60}\n")
                    return False, False, None
            except Exception as e:
                # その他のエラーもすぐに報告
                logger.error(f"\n{'='*60}")
                logger.error(f"✗ {account_name}: 投稿試行中にエラーが発生しました！")
                logger.error(f"{'='*60}")
                logger.error(f"エラー発生時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.error(f"エラータイプ: {type(e).__name__}")
                logger.error(f"詳細: {e}")
                import traceback
                logger.error(f"トレースバック:\n{traceback.format_exc()}")
                logger.error(f"{'='*60}\n")
                # 文字数オーバーエラーの可能性があるので、リトライを試みる
                retry_count_for_length += 1
                if retry_count_for_length < max_retries_for_length:
                    # 文字数を10%減らす
                    reduction = int(len(current_tweet_text) * 0.1)
                    current_tweet_text = current_tweet_text[:len(current_tweet_text) - reduction]
                    logger.info(f"{account_name}: 文字数を {len(current_tweet_text)} 文字に減らしてリトライします（試行 {retry_count_for_length + 1}/{max_retries_for_length}）")
                    continue
                else:
                    logger.error(f"{account_name}: 文字数を減らしても投稿に失敗しました。")
                    return False, False, None
        
        # ループを抜けた場合、resultが設定されているか確認
        if 'result' not in locals() or result is None or not result.get('success'):
            logger.error(f"{account_name}: 投稿に失敗しました。")
            return False, False, None
        
        if result and result.get('success'):
            # 投稿履歴を記録
            cycle_number = db.get_current_cycle_number(blog_url, twitter_handle)
            db.record_post(
                post_id=post_data['id'],
                blog_url=blog_url,
                twitter_handle=twitter_handle,
                cycle_number=cycle_number,
                tweet_id=str(result.get('id', ''))
            )
            
            logger.info(f"✓ {account_name}: 投稿成功!")
            logger.info(f"  ツイートID: {result.get('id')}")
            logger.info(f"  サイクル番号: {cycle_number}")
            logger.info(f"  URL: https://twitter.com/{twitter_handle}/status/{result.get('id')}")
            return True, False, None
        else:
            # エラーの種類を確認
            # twitter_poster.pyでエラーがログに記録されているので、ここでは簡潔に
            logger.error(f"✗ {account_name}: 投稿失敗")
            return False, False, None
            
    except tweepy.TooManyRequests as e:
        current_time = datetime.now()
        logger.error(f"\n✗ {account_name}: レート制限に達しました")
        logger.error(f"発生時刻: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        reset_time = extract_rate_limit_reset_time(e)
        if reset_time:
            # 少し余裕を持たせる（1分追加）
            wait_until = reset_time + timedelta(minutes=1)
            wait_seconds = (wait_until - current_time).total_seconds()
            
            logger.error(f"レート制限のリセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.error(f"待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.error(f"待機時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
            
            # 待機時間を保存
            state = load_rate_limit_state()
            state[account_key] = {
                'wait_until': wait_until.isoformat(),
                'reset_time': reset_time.isoformat()
            }
            save_rate_limit_state(state)
            
            return False, True, wait_until
        else:
            logger.error("リセット時刻の情報が取得できませんでした。")
            return False, False, None
            
    except Exception as e:
        logger.error(f"✗ {account_name}: エラー: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"トレースバック:\n{traceback.format_exc()}")
        return False, False, None


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='投稿テストスクリプト（レート制限管理付き）')
    parser.add_argument('--account', choices=['365bot', 'pursahs', 'both'], default='both', 
                       help='テストするアカウント')
    parser.add_argument('--yes', '-y', action='store_true', help='確認なしで自動的に続行')
    
    args = parser.parse_args()
    
    max_retries = 10  # 最大再試行回数
    retry_count = 0
    rate_limited_accounts = set()  # レート制限に達したアカウントを記録
    
    # テストするアカウントのリストを決定
    all_accounts = [('365bot', '365botGary'), ('pursahs', 'pursahsgospel')]
    if args.account == '365bot':
        accounts_to_check = [('365bot', '365botGary')]
    elif args.account == 'pursahs':
        accounts_to_check = [('pursahs', 'pursahsgospel')]
    else:
        accounts_to_check = all_accounts
    
    # 初回実行時に、以前の待機時間が残っているかチェック
    logger.info("=" * 60)
    logger.info("初回実行時の状態チェック")
    logger.info("=" * 60)
    state = load_rate_limit_state()
    now = datetime.now()
    
    accounts_ready = []  # 投稿可能なアカウント
    accounts_waiting = []  # 待機中のアカウント
    
    for account_key, account_name in accounts_to_check:
        account_state = state.get(account_key, {})
        wait_until_str = account_state.get('wait_until')
        reset_time_str = account_state.get('reset_time')
        
        if wait_until_str:
            wait_until = datetime.fromisoformat(wait_until_str)
            if wait_until > now:
                # まだ待機中
                wait_seconds = (wait_until - now).total_seconds()
                logger.warning(f"⚠ {account_name}: 以前の実行で設定された待機時間が残っています。")
                logger.warning(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.warning(f"  現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.warning(f"  残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                if reset_time_str:
                    reset_time = datetime.fromisoformat(reset_time_str)
                    logger.warning(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.warning(f"  → このアカウントは待機中です。投稿は試行されません。")
                accounts_waiting.append((account_key, account_name, wait_until))
            else:
                # 待機時間が過ぎている
                logger.info(f"✓ {account_name}: 以前の待機時間は既に過ぎています。クリアします。")
                state[account_key] = {
                    'wait_until': None,
                    'reset_time': None
                }
                save_rate_limit_state(state)
                logger.info(f"  → このアカウントは投稿可能です。")
                accounts_ready.append((account_key, account_name))
        else:
            # 待機時間が設定されていない
            logger.info(f"✓ {account_name}: 待機時間は設定されていません。")
            logger.info(f"  → このアカウントは投稿可能です。")
            accounts_ready.append((account_key, account_name))
    
    # 結果をまとめて報告
    logger.info("")
    logger.info("=" * 60)
    logger.info("初回実行時の状態チェック結果")
    logger.info("=" * 60)
    if accounts_ready:
        logger.info(f"✓ 投稿可能なアカウント: {len(accounts_ready)} 件")
        for account_key, account_name in accounts_ready:
            logger.info(f"  - {account_name}")
    else:
        logger.warning("⚠ 投稿可能なアカウントがありません。")
    
    if accounts_waiting:
        logger.warning(f"⚠ 待機中のアカウント: {len(accounts_waiting)} 件")
        for account_key, account_name, wait_until in accounts_waiting:
            wait_seconds = (wait_until - now).total_seconds()
            logger.warning(f"  - {account_name}: 待機終了時刻 {wait_until.strftime('%Y-%m-%d %H:%M:%S')} (残り {int(wait_seconds // 60)} 分)")
            # 待機中のアカウントをrate_limited_accountsに追加（ループ内で試行されないようにする）
            rate_limited_accounts.add(account_key)
        logger.warning("  → これらのアカウントは待機時間が終了するまで投稿は試行されません。")
    else:
        logger.info("✓ 待機中のアカウントはありません。")
    
    logger.info("=" * 60)
    logger.info("")
    
    while retry_count < max_retries:
        logger.info("=" * 60)
        logger.info(f"投稿テスト（レート制限管理付き） - 試行 {retry_count + 1}/{max_retries}")
        logger.info("=" * 60)
        
        # 待機時間をチェック
        state = load_rate_limit_state()
        
        accounts_to_test = []
        
        # アカウントのチェック（レート制限に達していない場合のみ）
        if args.account in ['365bot', 'both']:
            if '365bot' not in rate_limited_accounts:
                if check_and_wait_for_account('365bot', '365botGary'):
                    accounts_to_test.append(('365bot', '365botGary', Config.BLOG_365BOT_URL, Config.TWITTER_365BOT_HANDLE, Config.get_twitter_credentials_365bot()))
        
        if args.account in ['pursahs', 'both']:
            if 'pursahs' not in rate_limited_accounts:
                if check_and_wait_for_account('pursahs', 'pursahsgospel'):
                    accounts_to_test.append(('pursahs', 'pursahsgospel', Config.BLOG_PURSAHS_URL, Config.TWITTER_PURSAHS_HANDLE, Config.get_twitter_credentials_pursahs()))
        
        if not accounts_to_test:
            logger.warning(f"\n{'='*60}")
            logger.warning("すべてのアカウントが待機中です。")
            logger.warning(f"{'='*60}")
            
            # 原因を記録して表示
            state = load_rate_limit_state()
            for account_key, account_name in [('365bot', '365botGary'), ('pursahs', 'pursahsgospel')]:
                if args.account == 'both' or (args.account == '365bot' and account_key == '365bot') or (args.account == 'pursahs' and account_key == 'pursahs'):
                    account_state = state.get(account_key, {})
                    reason = account_state.get('reason', '待機時間中（原因不明）')
                    error_time_str = account_state.get('error_time')
                    wait_until_str = account_state.get('wait_until')
                    api_endpoint = account_state.get('api_endpoint', '不明')
                    logger.warning(f"{account_name}:")
                    logger.warning(f"  原因: {reason}")
                    logger.warning(f"  APIエンドポイント: {api_endpoint}")
                    if error_time_str:
                        error_time = datetime.fromisoformat(error_time_str)
                        logger.warning(f"  エラー発生時刻: {error_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    if wait_until_str:
                        wait_until = datetime.fromisoformat(wait_until_str)
                        now = datetime.now()
                        if wait_until > now:
                            wait_seconds = (wait_until - now).total_seconds()
                            logger.warning(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')} (残り {int(wait_seconds // 60)} 分)")
                        else:
                            logger.warning(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')} (既に終了)")
            
            logger.warning(f"{'='*60}")
            logger.warning("原因を確認するには: python check_rate_limit_reasons.py")
            logger.warning("処理を停止します。")
            break
        
        success_count = 0
        retry_needed = False
        
        for account_key, account_name, blog_url, twitter_handle, credentials in accounts_to_test:
            logger.info(f"\n{'='*60}")
            logger.info(f"{account_name} アカウントの投稿テスト")
            logger.info(f"{'='*60}")
            
            if not credentials.get('api_key') or not credentials.get('access_token'):
                logger.error(f"{account_name}: 認証情報が設定されていません")
                continue
            
            success, should_retry, wait_until = test_post_with_rate_limit_handling(
                blog_url, twitter_handle, credentials, account_key, account_name
            )
            
            if success:
                success_count += 1
                # 成功したアカウントはレート制限リストから削除
                if account_key in rate_limited_accounts:
                    rate_limited_accounts.remove(account_key)
                    logger.info(f"{account_name}: レート制限リストから削除しました")
            elif should_retry:
                retry_needed = True
                # レート制限に達したアカウントを記録（次のループでは試行しない）
                rate_limited_accounts.add(account_key)
                logger.info(f"\n{account_name}: レート制限のため待機が必要です。")
                logger.info(f"待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{account_name}: 次のループでは試行しません（待機時間が終了するまで）")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"テスト投稿完了: {success_count} 件成功")
        
        # すべて成功した場合は終了
        if success_count == len(accounts_to_test):
            logger.info("すべてのアカウントで投稿が成功しました！")
            break
        
        # 再試行が必要な場合
        if retry_needed:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"最大再試行回数（{max_retries}回）に達しました。")
                break
            
            logger.info(f"\nレート制限のため、再試行します（{retry_count}/{max_retries}）")
            # 待機時間をチェックして、最短の待機時間まで待機
            state = load_rate_limit_state()
            wait_times = []
            for account_key, account_state in state.items():
                wait_until_str = account_state.get('wait_until')
                if wait_until_str:
                    wait_until = datetime.fromisoformat(wait_until_str)
                    if wait_until > datetime.now():
                        wait_seconds = (wait_until - datetime.now()).total_seconds()
                        wait_times.append((wait_until, wait_seconds))
            
            if wait_times:
                # 最短の待機時間を取得
                wait_until, min_wait = min(wait_times, key=lambda x: x[1])
                logger.info(f"最短待機時間: {int(min_wait)} 秒（{int(min_wait // 60)} 分）")
                logger.info(f"待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"次の実行予定時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("待機中...")
                
                # 待機中に修正を行えるように、1分ごとに残り時間を表示
                last_logged = 0
                while datetime.now() < wait_until:
                    remaining = (wait_until - datetime.now()).total_seconds()
                    if remaining > 0:
                        # 1分ごとに残り時間を表示
                        if int(remaining) != last_logged and (int(remaining) % 60 == 0 or remaining < 60):
                            print(f"残り待機時間: {int(remaining)} 秒（{int(remaining // 60)} 分）")
                            print(f"次の実行予定時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                            sys.stdout.flush()
                            logger.info(f"残り待機時間: {int(remaining)} 秒（{int(remaining // 60)} 分）")
                            logger.info(f"次の実行予定時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                            last_logged = int(remaining)
                        time.sleep(min(60, remaining))  # 最大60秒待機
                    else:
                        break
                
                logger.info("待機時間が終了しました。再試行します。\n")
                # 待機時間が終了したので、レート制限リストをクリア（再試行可能にする）
                # ただし、check_and_wait_for_accountでリセット時刻まで待機するので、
                # ここでクリアしても問題ない
                rate_limited_accounts.clear()
                logger.info("レート制限リストをクリアしました。すべてのアカウントを再試行します。")
            else:
                logger.info("待機時間が終了しました。")
                # 待機時間が終了したので、レート制限リストをクリア
                rate_limited_accounts.clear()
        else:
            # レート制限以外のエラーの場合は終了
            logger.info("レート制限以外のエラーが発生しました。")
            break
    
    logger.info(f"\n{'='*60}")
    logger.info("投稿テスト終了")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()

