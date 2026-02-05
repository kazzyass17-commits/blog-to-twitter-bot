"""シンプルなスケジューラー起動スクリプト
各アカウント独立、毎日ランダムな時刻（0〜30分）に投稿
"""
import os
import sys
import time
import schedule
import logging
from datetime import datetime
import random
import subprocess

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler_simple.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 作業ディレクトリ設定
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PID_FILE = 'scheduler_simple.pid'

def check_existing_scheduler():
    """既存のスケジューラーが動作中かチェック"""
    if not os.path.exists(PID_FILE):
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            old_pid = int(f.read().strip())
        
        # psutilでプロセス確認
        import psutil
        if psutil.pid_exists(old_pid):
            proc = psutil.Process(old_pid)
            cmdline = ' '.join(proc.cmdline())
            if 'start_scheduler_simple' in cmdline or 'scheduler' in cmdline.lower():
                logger.error(f"既存のスケジューラーが動作中です (PID: {old_pid})")
                return True
        # プロセスが存在しない場合は古いPIDファイル
        logger.info(f"古いPIDファイルを検出 (PID: {old_pid} は存在しない)")
    except (ValueError, IOError, ImportError) as e:
        logger.warning(f"PIDファイルチェックエラー: {e}")
    except Exception as e:
        logger.warning(f"プロセス確認エラー: {e}")
    
    return False

# 複数起動チェック
if check_existing_scheduler():
    logger.error("終了します。既存のスケジューラーを停止してから再実行してください。")
    sys.exit(1)

# PIDファイル作成
with open(PID_FILE, 'w') as f:
    f.write(str(os.getpid()))
logger.info(f"スケジューラー起動 (PID: {os.getpid()})")


def run_post(account: str):
    """指定アカウントの投稿を実行"""
    logger.info(f"投稿実行開始: {account}")
    try:
        result = subprocess.run(
            [sys.executable, 'post_both_accounts.py', '--account', account],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        if result.returncode == 0:
            logger.info(f"投稿成功: {account}")
        else:
            logger.error(f"投稿失敗 ({account}): {result.stderr[:500]}")
    except Exception as e:
        logger.error(f"投稿エラー ({account}): {e}")


def run_post_and_reschedule(account: str, hour: int):
    """投稿実行後、翌日の時刻を再設定"""
    run_post(account)
    
    # 次回の時刻を再設定
    tag = f'{account}_{hour}'
    schedule.clear(tag)
    new_minute = random.randint(0, 30)
    schedule.every().day.at(f"{hour:02d}:{new_minute:02d}").do(
        run_post_and_reschedule, account=account, hour=hour
    ).tag(tag)
    logger.info(f"次回スケジュール再設定: {account} -> {hour:02d}:{new_minute:02d}")


# スケジュール設定（8時、12時、16時）
# 各アカウント独立、0〜30分のランダム
POST_HOURS = [8, 12, 16]
ACCOUNTS = ['pursahs', '365bot']

for account in ACCOUNTS:
    for hour in POST_HOURS:
        minute = random.randint(0, 30)
        tag = f'{account}_{hour}'
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
            run_post_and_reschedule, account=account, hour=hour
        ).tag(tag)
        logger.info(f"スケジュール登録: {account} -> {hour:02d}:{minute:02d}")

logger.info("スケジューラー開始。Ctrl+Cで終了。")
logger.info(f"登録ジョブ数: {len(schedule.get_jobs())}")

# メインループ
try:
    while True:
        schedule.run_pending()
        time.sleep(30)
except KeyboardInterrupt:
    logger.info("スケジューラー終了")
finally:
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
        logger.info("PIDファイル削除")
