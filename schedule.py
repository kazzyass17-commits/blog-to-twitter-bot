"""
スケジューラー
8時、14時、20時にランダムな時間でブログ→Twitter投稿を実行
"""
import schedule
import time
import random
import logging
from datetime import datetime, time as dt_time
from main import main

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    """1日3回（8時、14時、20時）のランダム投稿をスケジュール"""
    # 各時間帯でランダムな分を生成（0-59分の間でランダム）
    times = [
        (8, random.randint(0, 59)),   # 8時00分～8時59分
        (14, random.randint(0, 59)),  # 14時00分～14時59分
        (20, random.randint(0, 59)),  # 20時00分～20時59分
    ]
    
    for hour, minute in times:
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(run_scheduled_task)
        logger.info(f"スケジュール登録: 毎日 {hour:02d}:{minute:02d}")
    
    logger.info(f"合計{len(times)}件のスケジュールを登録しました")


def start_scheduler():
    """スケジューラーを開始"""
    logger.info("=" * 60)
    logger.info("スケジューラーを開始します")
    logger.info("投稿時間: 8時、14時、20時（各時間帯でランダムな分）")
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


if __name__ == "__main__":
    start_scheduler()
