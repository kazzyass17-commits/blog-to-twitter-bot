"""
レート制限待機時間チェックモジュール
すべてのスクリプトで共通して使用する
"""
import json
import os
import time
import sys
from datetime import datetime, timedelta
import logging

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
            'reset_time': None,
            'reason': None,
            'error_time': None,
            'api_endpoint': None,
            'error_message': None
        },
        'pursahs': {
            'wait_until': None,
            'reset_time': None,
            'reason': None,
            'error_time': None,
            'api_endpoint': None,
            'error_message': None
        }
    }


def save_rate_limit_state(state):
    """待機時間の状態を保存する"""
    try:
        with open(RATE_LIMIT_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"状態ファイルの保存エラー: {e}")


def record_rate_limit_reason(account_key: str, account_name: str, api_endpoint: str, error_message: str, reset_time: datetime = None, wait_until: datetime = None, rate_limit_limit: int = None, rate_limit_remaining: int = None):
    """
    レート制限の原因を記録する
    
    Args:
        account_key: アカウントキー（'365bot' または 'pursahs'）
        account_name: アカウント名（表示用）
        api_endpoint: APIエンドポイント（例: 'POST /2/tweets'）
        error_message: エラーメッセージ
        reset_time: リセット時刻
        wait_until: 待機終了時刻
        rate_limit_limit: レート制限の上限（x-rate-limit-limit）
        rate_limit_remaining: 残りのリクエスト数（x-rate-limit-remaining）
    """
    state = load_rate_limit_state()
    now = datetime.now()
    
    used_count = None
    if rate_limit_limit is not None and rate_limit_remaining is not None:
        used_count = rate_limit_limit - rate_limit_remaining
    
    state[account_key] = {
        'wait_until': wait_until.isoformat() if wait_until else None,
        'reset_time': reset_time.isoformat() if reset_time else None,
        'reason': '429 Too Many Requests',
        'error_time': now.isoformat(),
        'api_endpoint': api_endpoint,
        'error_message': str(error_message)[:500],  # 長すぎる場合は切り詰め
        'rate_limit_limit': rate_limit_limit,
        'rate_limit_remaining': rate_limit_remaining,
        'used_count': used_count  # 15分間のウィンドウ内でカウントされているリクエスト数
    }
    
    save_rate_limit_state(state)
    logger.warning(f"{account_name}: レート制限の原因を記録しました。")
    logger.warning(f"  APIエンドポイント: {api_endpoint}")
    logger.warning(f"  エラー発生時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.warning(f"  エラーメッセージ: {str(error_message)[:200]}")
    if rate_limit_limit is not None and rate_limit_remaining is not None:
        logger.warning(f"  レート制限の状態:")
        logger.warning(f"    上限: {rate_limit_limit} リクエスト")
        logger.warning(f"    残り: {rate_limit_remaining} リクエスト")
        logger.warning(f"    使用済み: {used_count} リクエスト")
        logger.warning(f"    15分間のウィンドウ内で {used_count} リクエストがカウントされています")


def check_and_wait_for_account(account_key: str, account_name: str, skip_wait: bool = False):
    """
    アカウントの待機時間をチェックし、必要に応じて待機する
    
    Args:
        account_key: アカウントキー（'365bot' または 'pursahs'）
        account_name: アカウント名（表示用）
        skip_wait: Trueの場合、待機時間があっても待機せずにFalseを返す
    
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
            
            if skip_wait:
                logger.warning(f"{account_name} アカウント: レート制限待機中（待機時間をスキップします）")
                logger.warning(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.warning(f"  残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                return False
            
            print(f"\n{'='*60}")
            print(f"{account_name} アカウント: レート制限待機中")
            print(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
            print(f"{'='*60}")
            sys.stdout.flush()
            logger.info(f"\n{'='*60}")
            logger.info(f"{account_name} アカウント: レート制限待機中")
            logger.info(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
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
            # wait_untilが過ぎているが、reset_timeをチェックする必要がある
            reset_time_str = account_state.get('reset_time')
            if reset_time_str:
                reset_time = datetime.fromisoformat(reset_time_str)
                now = datetime.now()
                if reset_time > now:
                    # reset_timeがまだ来ていない場合は、reset_timeまで待機する必要がある
                    wait_seconds = (reset_time - now).total_seconds()
                    logger.warning(f"{account_name}: wait_untilは過ぎていますが、reset_timeがまだ来ていません。")
                    logger.warning(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.warning(f"  現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.warning(f"  残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                    logger.warning(f"  reset_timeまで待機する必要があります。")
                    
                    if skip_wait:
                        return False  # 待機中（投稿不可）
                    
                    # reset_time + 10秒まで待機
                    wait_until_reset = reset_time + timedelta(seconds=10)
                    if wait_until_reset > now:
                        wait_seconds = (wait_until_reset - now).total_seconds()
                        logger.info(f"{account_name}: reset_timeまで待機します。")
                        time.sleep(wait_seconds)
                        logger.info(f"{account_name}: reset_timeが過ぎました。")
            
            # 待機時間が過ぎている（reset_timeも過ぎている、またはreset_timeが設定されていない）
            logger.info(f"{account_name}: 以前の待機時間は既に過ぎています。クリアします。")
            state[account_key] = {
                'wait_until': None,
                'reset_time': None,
                'reason': None,
                'error_time': None,
                'api_endpoint': None,
                'error_message': None
            }
            save_rate_limit_state(state)
            return True  # 待機不要、投稿可能
    else:
        # 待機時間が設定されていない
        return True  # 待機不要、投稿可能

