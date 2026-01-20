"""テスト用スケジュール - 21:00に1回投稿"""
import sys
import os
import time
from datetime import datetime

# 文字コード設定
os.environ['PYTHONIOENCODING'] = 'utf-8'

# ログ設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_schedule.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from post_both_accounts import main as post_both

# テストスケジュール: 21:00
TEST_TIMES = ["21:00"]

def run_test_schedule():
    logger.info("=" * 60)
    logger.info("テストスケジュール開始")
    logger.info(f"投稿予定時刻: {', '.join(TEST_TIMES)}")
    logger.info("=" * 60)
    
    executed_times = set()
    
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # 全てのテスト時刻が実行済みなら終了
        if len(executed_times) >= len(TEST_TIMES):
            logger.info("全てのテスト投稿が完了しました")
            break
        
        # 予定時刻に達したら投稿
        if current_time in TEST_TIMES and current_time not in executed_times:
            logger.info(f"投稿開始: {current_time}")
            try:
                post_both()
                logger.info(f"投稿完了: {current_time}")
            except Exception as e:
                logger.error(f"投稿エラー: {e}")
            executed_times.add(current_time)
        
        # 1秒待機
        time.sleep(1)

if __name__ == "__main__":
    run_test_schedule()
