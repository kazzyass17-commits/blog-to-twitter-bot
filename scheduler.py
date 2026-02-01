"""
スケジューラー
9時、12時、15時（JST）にランダムな時間でブログ→Twitter投稿を実行
"""
import schedule
import time
import random
import logging
import os
import sys
import atexit
from datetime import datetime, time as dt_time, timedelta
from post_both_accounts import main
from retry_failed_posts import main as retry_main

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)
logger = logging.getLogger(__name__)

# ロックファイルのパス
LOCK_FILE = "scheduler.lock"


def disable_auto_open_on_windows():
    """Windowsでの自動ファイルオープンを無効化（ログの自動オープン防止）"""
    if sys.platform != "win32":
        return
    # 明示的にONになっている場合のみ許可
    if os.environ.get("ALLOW_AUTO_OPEN_LOGS", "").strip().lower() in ("1", "true", "yes"):
        return
    if hasattr(os, "startfile"):
        try:
            os.startfile = lambda *args, **kwargs: None  # type: ignore[assignment]
        except Exception:
            pass


def run_scheduled_task():
    """スケジュールされたタスクを実行"""
    logger.info("=" * 60)
    logger.info("スケジュール実行を開始します")
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    try:
        main()
    except Exception as e:
        logger.error(f"スケジュール実行エラー: {e}", exc_info=True)


def run_retry_task():
    """失敗した投稿のリトライタスクを実行"""
    logger.info("=" * 60)
    logger.info("リトライ実行を開始します")
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    try:
        retry_main()
    except Exception as e:
        logger.error(f"リトライ実行エラー: {e}", exc_info=True)


def schedule_daily_posts():
    """1日3回（8時、12時、16時 JST）のランダム投稿をスケジュール"""
    # 各時間帯でランダムな分を生成（0-59分の間でランダム）
    post_times = [
        (8, random.randint(0, 59)),   # 8時00分～8時59分
        (12, random.randint(0, 59)),  # 12時00分～12時59分
        (16, random.randint(0, 59)),  # 16時00分～16時59分
    ]
    
    # リトライスケジュール（9時、13時、17時）
    retry_times = [
        (9, random.randint(0, 59)),   # 9時00分～9時59分
        (13, random.randint(0, 59)),  # 13時00分～13時59分
        (17, random.randint(0, 59)),  # 17時00分～17時59分
    ]

    created_jobs = []
    
    # 通常投稿スケジュール
    for hour, minute in post_times:
        job = schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(run_scheduled_task)
        created_jobs.append(job)
        logger.info(f"投稿スケジュール登録: 毎日 {hour:02d}:{minute:02d}")
    
    # リトライスケジュール
    for hour, minute in retry_times:
        job = schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(run_retry_task)
        created_jobs.append(job)
        logger.info(f"リトライスケジュール登録: 毎日 {hour:02d}:{minute:02d}")
    
    logger.info(f"合計{len(post_times) + len(retry_times)}件のスケジュールを登録しました（投稿: {len(post_times)}件、リトライ: {len(retry_times)}件）")
    return created_jobs


def shift_jobs_to_tomorrow(jobs):
    """渡されたジョブの初回実行を明日へずらす"""
    for job in jobs:
        job.next_run = job.next_run + timedelta(days=1)
    logger.info("スケジュールを明日開始にシフトしました")


def run_temp_hourly_posts(count=3, interval_hours=1):
    """臨時: interval_hours間隔でcount回投稿を順次実行"""
    logger.info(f"臨時スケジュール開始: {interval_hours}時間間隔で{count}回投稿します")
    start = datetime.now()
    for i in range(count):
        logger.info(f"臨時投稿 {i+1}/{count} を開始します")
        run_scheduled_task()
        if i < count - 1:
            target = start + timedelta(hours=interval_hours * (i + 1))
            sleep_sec = max(0, (target - datetime.now()).total_seconds())
            logger.info(f"次の臨時投稿まで {sleep_sec/60:.1f} 分待機 (目標時刻: {target})")
            time.sleep(sleep_sec)
    logger.info("臨時スケジュールを完了しました")


def start_scheduler(temp_hourly_count=0, shift_daily_to_tomorrow=False):
    """スケジューラーを開始"""
    logger.info("=" * 60)
    logger.info("スケジューラーを開始します")
    logger.info("投稿時間: 9時、12時、15時（JST、各時間帯でランダムな分）")
    logger.info("リトライ時間: 10時、13時、16時（JST、各時間帯でランダムな分）")
    logger.info("=" * 60)

    if temp_hourly_count > 0:
        logger.info(f"臨時投稿モード: 1時間おきに{temp_hourly_count}回実行します")
        run_temp_hourly_posts(count=temp_hourly_count, interval_hours=1)
        logger.info("臨時投稿モード完了")
        logger.info("通常スケジュールを明日から再開します" if shift_daily_to_tomorrow else "通常スケジュールを直ちに再開します")
    else:
        logger.info("初回実行をスキップしました。次のスケジュールから投稿を開始します。")

    # 1日3回のスケジュールを登録
    jobs = schedule_daily_posts()
    initial_shift_applied = False
    if shift_daily_to_tomorrow:
        shift_jobs_to_tomorrow(jobs)
        initial_shift_applied = True
    
    logger.info("\nスケジューラーが実行中です。Ctrl+Cで停止できます。")
    logger.info("次の投稿スケジュール:")
    
    # 次の実行予定を表示
    for job in schedule.jobs:
        logger.info(f"  - {job.next_run}")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック
            
            # 毎日0時に新しいランダム時間を再生成
            now = datetime.now()
            if now.hour == 0 and now.minute == 0:
                logger.info("新しい日のスケジュールを再生成します")
                schedule.clear()
                schedule_daily_posts()
                # 以降は通常サイクルに戻すため、初日のみシフト
    except KeyboardInterrupt:
        logger.info("\nスケジューラーを停止します")


def check_lock_file():
    """ロックファイルをチェックして、既存のプロセスが実行中か確認"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                lock_pid = int(f.read().strip())
            
            # ロックファイルのPIDが実際に実行中かチェック
            try:
                import psutil
                if psutil.pid_exists(lock_pid):
                    proc = psutil.Process(lock_pid)
                    cmdline = proc.cmdline()
                    if any('scheduler.py' in str(arg) for arg in cmdline):
                        logger.error(f"既存のschedule.pyプロセスが実行中です（PID: {lock_pid}）")
                        logger.error("重複実行を防ぐため、このプロセスを終了します。")
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, ImportError):
                # psutilが使えない、またはプロセスが存在しない場合はロックファイルを削除
                try:
                    os.remove(LOCK_FILE)
                    logger.warning(f"古いロックファイルを削除しました（PID: {lock_pid}）")
                except:
                    pass
        except (ValueError, IOError):
            # ロックファイルが破損している場合は削除
            try:
                os.remove(LOCK_FILE)
                logger.warning("破損したロックファイルを削除しました")
            except:
                pass
    return False


def create_lock_file():
    """ロックファイルを作成"""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"ロックファイルを作成しました（PID: {os.getpid()}）")
        return True
    except Exception as e:
        logger.error(f"ロックファイルの作成に失敗しました: {e}")
        return False


def remove_lock_file():
    """ロックファイルを削除"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            logger.info("ロックファイルを削除しました")
    except Exception as e:
        logger.warning(f"ロックファイルの削除に失敗しました: {e}")


def check_existing_process():
    """既存のschedule.pyプロセスが実行中かチェック（psutil使用）"""
    try:
        import psutil
        current_pid = os.getpid()
        current_script = os.path.abspath(__file__)
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('scheduler.py' in str(arg) for arg in cmdline):
                        if proc.info['pid'] != current_pid:
                            logger.warning(f"既存のscheduler.pyプロセスが実行中です（PID: {proc.info['pid']}）")
                            logger.warning("重複実行を防ぐため、このプロセスを終了します。")
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        # psutilがインストールされていない場合はスキップ
        pass
    return False


def terminate_existing_schedulers():
    """既存のスケジューラプロセスを終了させる"""
    terminated_count = 0
    try:
        import psutil
        current_pid = os.getpid()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('scheduler.py' in str(arg) for arg in cmdline):
                        if proc.info['pid'] != current_pid:
                            logger.info(f"既存のスケジューラプロセスを終了します（PID: {proc.info['pid']}）")
                            try:
                                proc.terminate()
                                proc.wait(timeout=5)  # 5秒待機
                                logger.info(f"  -> 正常に終了しました")
                                terminated_count += 1
                            except psutil.TimeoutExpired:
                                logger.warning(f"  -> 終了がタイムアウト、強制終了します")
                                proc.kill()
                                terminated_count += 1
                            except Exception as e:
                                logger.error(f"  -> 終了に失敗: {e}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if terminated_count > 0:
            logger.info(f"合計 {terminated_count} 個の既存スケジューラを終了しました")
            # ロックファイルも削除
            if os.path.exists(LOCK_FILE):
                try:
                    os.remove(LOCK_FILE)
                    logger.info("古いロックファイルを削除しました")
                except:
                    pass
            # プロセス終了が完了するのを待機
            logger.info("プロセス終了を待機中（3秒）...")
            time.sleep(3)
        else:
            logger.info("実行中の既存スケジューラはありませんでした")
            
    except ImportError:
        logger.warning("psutilがインストールされていないため、既存プロセスの終了はスキップします")
        logger.warning("pip install psutil でインストールしてください")
    
    return terminated_count


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='スケジューラを起動')
    parser.add_argument('--force', '-f', action='store_true', 
                        help='（互換性のため残存、現在は常に既存プロセスを終了）')
    parser.add_argument('--temp3', action='store_true',
                        help='臨時モード: 1時間おきに3回投稿してから通常スケジュール（明日開始）')
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("スケジューラ起動処理を開始します")
    logger.info("=" * 60)

    # ログの自動オープンを防止（Windows）
    disable_auto_open_on_windows()
    
    # 1. 起動時の競合防止（一時ロックファイル）
    STARTUP_LOCK = "scheduler_startup.lock"
    try:
        # 排他的にロックファイルを作成（O_CREAT | O_EXCL）
        fd = os.open(STARTUP_LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        logger.info("起動ロックを取得しました")
    except FileExistsError:
        # 既に別のプロセスが起動中
        logger.error("別のスケジューラが起動処理中です。数秒後に再試行してください。")
        sys.exit(1)
    
    try:
        # 2. 既存のスケジューラを検索・終了（重複防止）
        logger.info("既存のスケジューラを検索・終了中...")
        terminated = terminate_existing_schedulers()
        if terminated > 0:
            logger.info(f"{terminated}個の既存プロセスを終了しました")
            time.sleep(2)  # プロセス終了を待機
        
        # 3. 古いロックファイルを削除
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
                logger.info("古いロックファイルを削除しました")
            except:
                pass
    finally:
        # 起動ロックを解除
        try:
            os.remove(STARTUP_LOCK)
        except:
            pass
    
    # 4. ロックファイルを作成
    if not create_lock_file():
        logger.error("ロックファイルの作成に失敗しました。終了します。")
        sys.exit(1)
    
    # 終了時にロックファイルを削除
    atexit.register(remove_lock_file)
    
    # シグナルハンドラを設定（Ctrl+Cなど）
    import signal
    def signal_handler(sig, frame):
        logger.info("\nシグナルを受信しました。ロックファイルを削除して終了します。")
        remove_lock_file()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("スケジューラを起動します。")
    if args.temp3:
        start_scheduler(temp_hourly_count=3, shift_daily_to_tomorrow=True)
    else:
        start_scheduler()
