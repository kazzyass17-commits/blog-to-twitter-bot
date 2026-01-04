"""
投稿テストを自動実行するスクリプト
- 同じアカウントの次の文字数テスト: 900秒待機
- アカウント間（365botGary ↔ pursahsgospel）: 265秒待機
"""
import os
import time
import logging
import subprocess
import sys
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 900秒 = 15分（同じアカウントの次の文字数テストまで）
INTERVAL_SECONDS = 900

# 265秒 = アカウント間（365botGary ↔ pursahsgospel）の待機時間
ACCOUNT_INTERVAL_SECONDS = 265

STATE_FILE = "test_post_state.json"


def run_test():
    """テストスクリプトを実行"""
    logger.info("="*60)
    logger.info(f"テスト実行開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    try:
        # test_post_with_length_check.pyを実行
        result = subprocess.run(
            [sys.executable, "test_post_with_length_check.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 出力を表示
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            logger.info("テスト実行完了")
        else:
            logger.error(f"テスト実行エラー: 終了コード {result.returncode}")
            
    except Exception as e:
        logger.error(f"テスト実行エラー: {e}", exc_info=True)


def should_wait_for_account_switch():
    """アカウントが切り替わるかどうかを判定"""
    if not os.path.exists(STATE_FILE):
        return False
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        current_account_index = state.get('current_account_index', 0)
        current_length_index = state.get('current_length_index', 0)
        accounts = state.get('accounts', [])
        test_lengths = [50, 100, 150, 200, 230, 250, 270, 280]  # TEST_LENGTHSと同じ
        
        # 次の文字数インデックスが範囲外なら、アカウントが切り替わる
        return current_length_index >= len(test_lengths)
    except Exception as e:
        logger.warning(f"状態ファイルの読み込みエラー: {e}")
        return False


def main():
    """メイン関数 - アカウント間は265秒、同じアカウントは900秒待機"""
    logger.info("="*60)
    logger.info("投稿テストスケジューラーを開始")
    logger.info("="*60)
    logger.info(f"同じアカウントの次の文字数テスト: {INTERVAL_SECONDS} 秒（{INTERVAL_SECONDS // 60} 分）")
    logger.info(f"アカウント間（365botGary ↔ pursahsgospel）: {ACCOUNT_INTERVAL_SECONDS} 秒（{ACCOUNT_INTERVAL_SECONDS // 60} 分）")
    logger.info("停止するには Ctrl+C を押してください")
    logger.info("="*60)
    
    try:
        while True:
            # テストを実行
            run_test()
            
            # アカウントが切り替わるかどうかを判定
            account_switching = should_wait_for_account_switch()
            
            if account_switching:
                wait_seconds = ACCOUNT_INTERVAL_SECONDS
                logger.info(f"\nアカウントが切り替わります。{wait_seconds} 秒（{wait_seconds // 60} 分）待機します...")
            else:
                wait_seconds = INTERVAL_SECONDS
                logger.info(f"\n同じアカウントの次の文字数テストまで {wait_seconds} 秒（{wait_seconds // 60} 分）待機します...")
            
            logger.info(f"次回実行予定: {(datetime.now().timestamp() + wait_seconds):.0f} 秒後")
            
            time.sleep(wait_seconds)
            
    except KeyboardInterrupt:
        logger.info("\nスケジューラーを停止しました")
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)


if __name__ == "__main__":
    main()

