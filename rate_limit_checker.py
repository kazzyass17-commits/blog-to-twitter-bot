"""
レート制限待機時間チェックモジュール
すべてのスクリプトで共通して使用する
"""
import json
import os
import time
import sys
from datetime import datetime, timedelta, timezone
import logging

# Windowsでの文字化け対策（環境変数を設定）
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

logger = logging.getLogger(__name__)

# 待機時間管理ファイル
RATE_LIMIT_STATE_FILE = "rate_limit_state.json"


def load_rate_limit_state():
    """待機時間の状態を読み込む"""
    if os.path.exists(RATE_LIMIT_STATE_FILE):
        try:
            # WindowsのOut-File等でUTF-8 BOM付きになることがあるため utf-8-sig を使用
            with open(RATE_LIMIT_STATE_FILE, 'r', encoding='utf-8-sig') as f:
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


def clear_rate_limit_state(account_key: str):
    """
    レート制限状態をクリアする（投稿成功時など）
    
    Args:
        account_key: アカウントキー（'365bot' または 'pursahs'）
    """
    state = load_rate_limit_state()
    if account_key in state:
        state[account_key] = {
            'wait_until': None,
            'reset_time': None,
            'reason': None,
            'error_time': None,
            'api_endpoint': None,
            'error_message': None,
            'rate_limit_limit': None,
            'rate_limit_remaining': None,
            'used_count': None
        }
        save_rate_limit_state(state)
        logger.info(f"{account_key} アカウント: レート制限状態をクリアしました（投稿成功のため）")


def record_rate_limit_reason(
    account_key: str,
    account_name: str,
    api_endpoint: str,
    error_message: str,
    reason: str = '429 Too Many Requests',
    reset_time: datetime = None,
    wait_until: datetime = None,
    rate_limit_limit: int = None,
    rate_limit_remaining: int = None
):
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
        'reason': reason,
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


def check_and_wait_for_account(account_key: str, account_name: str, skip_wait: bool = False, credentials: dict = None):
    """
    アカウントの待機時間をチェックし、必要に応じて待機する
    
    注意: create_tweetでレート制限を確認すると実際に投稿されてしまうため、
    保存された状態（rate_limit_state.json）のみを確認する。
    実際のレート制限は、投稿時に429エラーが発生した際に記録される。
    
    Args:
        account_key: アカウントキー（'365bot' または 'pursahs'）
        account_name: アカウント名（表示用）
        skip_wait: Trueの場合、待機時間があっても待機せずにFalseを返す
        credentials: Twitter API認証情報（現在は使用しない。将来の拡張用）
    
    Returns:
        True: 待機が完了した、または待機不要（投稿可能）
        False: 待機中（投稿不可）
    """
    # 保存された状態を確認（create_tweetで確認すると投稿されてしまうため、保存された状態のみ確認）
    state = load_rate_limit_state()
    account_state = state.get(account_key, {})
    reason = account_state.get('reason')
    if reason == 'length_error':
        # 文字数由来なら待っても改善しない（ユーザー要望）
        logger.warning(f"{account_name} アカウント: 文字数由来のエラー（length_error）として記録されています。待機せず続行します。")
        return True
    
    # reset_timeを優先的に確認（XのAPIから取得した実際のリセット時刻）
    reset_time_str = account_state.get('reset_time')
    
    # reset_timeがNoneの場合、wait_untilを確認（過去の時刻なら問題なし）
    if not reset_time_str:
        # wait_untilを確認（過去の時刻なら問題なし）
        wait_until_str = account_state.get('wait_until')
        if wait_until_str and wait_until_str != 'None':
            wait_until = datetime.fromisoformat(wait_until_str)
            if wait_until.tzinfo is not None:
                now = datetime.now(timezone.utc)
            else:
                now = datetime.now()
            
            if wait_until <= now:
                # wait_untilが過去の時刻なら、問題なし（投稿可能）
                logger.info(f"{account_name} アカウント: 待機時刻を過ぎています。投稿可能です。")
                return True
            # wait_until が未来なら、その時刻まで待機 or スキップ
            wait_seconds = (wait_until - now).total_seconds()
            if skip_wait:
                logger.warning(f"{account_name} アカウント: 待機中のためスキップします（残り {int(wait_seconds)} 秒）")
                return False
            logger.info(f"{account_name} アカウント: 待機中（{int(wait_seconds)} 秒）...")
            time.sleep(max(0, int(wait_seconds)))
            return True
        
        # 429（レート制限）の場合のみ、reset_time不明時の保守的待機/スキップを行う
        if reason == '429 Too Many Requests':
            logger.warning(f"{account_name} アカウント: レート制限が発生しましたが、リセット時刻が不明です。")
            logger.warning(f"  15分待っても、実際のリセット時刻が15分後ではない可能性があります。")
            logger.warning(f"  安全のため、投稿をスキップします。")
            if skip_wait:
                return False  # 不明のため、投稿不可
            else:
                # 不明の場合は、実際のAPIを呼び出してreset_timeを取得する必要がある
                # しかし、APIを呼び出すとレート制限を消費する可能性があるため、
                # 安全のため、15分待機してから再試行（ただし、正確ではない可能性がある）
                logger.warning(f"  注意: 15分待機しますが、実際のリセット時刻が15分後ではない可能性があります。")
                logger.warning(f"  再試行時に429エラーが発生した場合は、その時点でreset_timeを取得します。")
                time.sleep(900)  # 15分 = 900秒
                return True
        
        # 429以外（例: 403など）はレート制限ではないので、ここではブロックしない
        return True
    
    if reset_time_str:
        reset_time = datetime.fromisoformat(reset_time_str)
        # reset_timeがUTCタイムゾーン付きの場合は、UTCで比較
        # そうでない場合は、ローカルタイムゾーンで比較
        if reset_time.tzinfo is not None:
            now = datetime.now(timezone.utc)
        else:
            now = datetime.now()
        
        if reset_time > now:
            # reset_timeがまだ来ていない場合は、reset_timeまで待機
            wait_seconds = (reset_time - now).total_seconds()
            
            if skip_wait:
                logger.warning(f"{account_name} アカウント: レート制限待機中（待機時間をスキップします）")
                logger.warning(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.warning(f"  残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                return False
            
            print(f"\n{'='*60}")
            print(f"{account_name} アカウント: レート制限待機中（XのAPIリセット時刻まで）")
            print(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
            print(f"{'='*60}")
            sys.stdout.flush()
            logger.info(f"\n{'='*60}")
            logger.info(f"{account_name} アカウント: レート制限待機中（XのAPIリセット時刻まで）")
            logger.info(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
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
                while wait_seconds > 0:
                    time.sleep(60)  # 1分ごとにチェック
                    if reset_time.tzinfo is not None:
                        wait_seconds = (reset_time - datetime.now(timezone.utc)).total_seconds()
                    else:
                        wait_seconds = (reset_time - datetime.now()).total_seconds()
                    
                    # 5分ごとにログを出力
                    if int(wait_seconds) % 300 < 60 and int(wait_seconds) != last_logged:
                        logger.info(f"待機中... 残り {int(wait_seconds // 60)} 分")
                        last_logged = int(wait_seconds)
                
                logger.info(f"待機時間が終了しました。続行します。")
                return True
            else:
                # 5分未満の場合は、そのまま待機
                logger.info(f"待機中... 残り {int(wait_seconds // 60)} 分")
                time.sleep(int(wait_seconds))
                logger.info(f"待機時間が終了しました。続行します。")
                return True
        else:
            # reset_timeが過ぎている場合は、待機不要
            logger.info(f"{account_name} アカウント: リセット時刻を過ぎています。投稿可能です。")
            return True
    
    # reset_timeがない場合は、wait_untilを確認（後方互換性のため）
    # ただし、wait_untilがNoneの場合は不明として扱う
    wait_until_str = account_state.get('wait_until')
    if wait_until_str and wait_until_str != 'None':
        wait_until = datetime.fromisoformat(wait_until_str)
        # wait_untilがUTCタイムゾーン付きの場合は、UTCで比較
        # そうでない場合は、ローカルタイムゾーンで比較
        if wait_until.tzinfo is not None:
            now = datetime.now(timezone.utc)
        else:
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
                while wait_until > (datetime.now(timezone.utc) if wait_until.tzinfo is not None else datetime.now()):
                    if wait_until.tzinfo is not None:
                        remaining = (wait_until - datetime.now(timezone.utc)).total_seconds()
                    else:
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
                if reset_time.tzinfo is not None:
                    now = datetime.now(timezone.utc)
                else:
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
        # reset_timeもwait_untilも設定されていない場合
        # reset_timeが取得できなかった場合は不明として扱う
        if account_state.get('reason') == '429 Too Many Requests':
            # 429エラーが発生したが、reset_timeが取得できなかった場合は不明
            logger.warning(f"{account_name} アカウント: レート制限が発生しましたが、リセット時刻が不明です。")
            logger.warning(f"  15分待っても、実際のリセット時刻が15分後ではない可能性があります。")
            logger.warning(f"  安全のため、投稿をスキップします。")
            if skip_wait:
                return False  # 不明のため、投稿不可
            else:
                # 不明の場合は、実際のAPIを呼び出してreset_timeを取得する必要がある
                # しかし、APIを呼び出すとレート制限を消費する可能性があるため、
                # 安全のため、15分待機してから再試行（ただし、正確ではない可能性がある）
                logger.warning(f"  注意: 15分待機しますが、実際のリセット時刻が15分後ではない可能性があります。")
                logger.warning(f"  再試行時に429エラーが発生した場合は、その時点でreset_timeを取得します。")
                time.sleep(900)  # 15分 = 900秒
                return True
        else:
            # レート制限が発生していない場合は、投稿可能
            return True  # 待機不要、投稿可能

