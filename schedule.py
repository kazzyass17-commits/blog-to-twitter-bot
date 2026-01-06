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
from datetime import datetime, time as dt_time
from post_both_accounts import main

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ロックファイルのパス
LOCK_FILE = "schedule.lock"


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


def schedule_daily_posts():
    """1日3回（9時、12時、15時 JST）のランダム投稿をスケジュール"""
    # 各時間帯でランダムな分を生成（0-59分の間でランダム）
    times = [
        (9, random.randint(0, 59)),   # 9時00分～9時59分
        (12, random.randint(0, 59)),  # 12時00分～12時59分
        (15, random.randint(0, 59)),  # 15時00分～15時59分
    ]
    
    for hour, minute in times:
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(run_scheduled_task)
        logger.info(f"スケジュール登録: 毎日 {hour:02d}:{minute:02d}")
    
    logger.info(f"合計{len(times)}件のスケジュールを登録しました")


def start_scheduler():
    """スケジューラーを開始"""
    logger.info("=" * 60)
    logger.info("スケジューラーを開始します")
    logger.info("投稿時間: 9時、12時、15時（JST、各時間帯でランダムな分）")
    logger.info("=" * 60)
    
    # 初回実行（起動時）
    logger.info("初回実行を行います")
    run_scheduled_task()
    
    # 1日3回のスケジュールを登録
    schedule_daily_posts()
    
    logger.info("\nスケジューラーが実行中です。Ctrl+Cで停止できます。")
    logger.info("次の投稿スケジュール:")
    
    # 次の実行予定を表示
    jobs = schedule.jobs
    for job in jobs:
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
                    if any('schedule.py' in str(arg) for arg in cmdline):
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
                    if cmdline and any('schedule.py' in str(arg) for arg in cmdline):
                        if proc.info['pid'] != current_pid:
                            logger.warning(f"既存のschedule.pyプロセスが実行中です（PID: {proc.info['pid']}）")
                            logger.warning("重複実行を防ぐため、このプロセスを終了します。")
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        # psutilがインストールされていない場合はスキップ
        pass
    return False


if __name__ == "__main__":
    # 重複実行チェック
    logger.info("重複実行チェックを実行中...")
    
    # 1. ロックファイルをチェック
    if check_lock_file():
        logger.error("既存のschedule.pyプロセスが実行中です。重複実行を防ぐため終了します。")
        sys.exit(1)
    
    # 2. psutilを使って既存プロセスをチェック（利用可能な場合）
    if check_existing_process():
        logger.error("既存のschedule.pyプロセスが実行中です。重複実行を防ぐため終了します。")
        sys.exit(1)
    
    # 3. ロックファイルを作成
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
    
    logger.info("重複実行チェック完了。スケジューラーを開始します。")
    start_scheduler()
