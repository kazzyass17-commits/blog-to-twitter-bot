"""
レート制限の原因を確認するスクリプト
"""
import json
from datetime import datetime
import os
import sys
import io

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RATE_LIMIT_STATE_FILE = "rate_limit_state.json"

def check_reasons():
    """レート制限の原因を確認"""
    if not os.path.exists(RATE_LIMIT_STATE_FILE):
        print("rate_limit_state.json が存在しません。")
        return
    
    with open(RATE_LIMIT_STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    print("=" * 60)
    print("レート制限の原因確認")
    print("=" * 60)
    print(f"確認時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for account_key, account_name in [('365bot', '365botGary'), ('pursahs', 'pursahsgospel')]:
        account_state = state.get(account_key, {})
        reason = account_state.get('reason')
        error_time_str = account_state.get('error_time')
        api_endpoint = account_state.get('api_endpoint')
        error_message = account_state.get('error_message')
        wait_until_str = account_state.get('wait_until')
        reset_time_str = account_state.get('reset_time')
        
        print(f"{account_name}:")
        if reason:
            print(f"  [原因] {reason}")
            if error_time_str:
                error_time = datetime.fromisoformat(error_time_str)
                print(f"  [エラー発生時刻] {error_time.strftime('%Y-%m-%d %H:%M:%S')}")
            if api_endpoint:
                print(f"  [APIエンドポイント] {api_endpoint}")
            if error_message:
                print(f"  [エラーメッセージ] {error_message[:200]}")
            if wait_until_str:
                wait_until = datetime.fromisoformat(wait_until_str)
                now = datetime.now()
                if wait_until > now:
                    wait_seconds = (wait_until - now).total_seconds()
                    print(f"  [待機終了時刻] {wait_until.strftime('%Y-%m-%d %H:%M:%S')} (残り {int(wait_seconds // 60)} 分)")
                else:
                    print(f"  [待機終了時刻] {wait_until.strftime('%Y-%m-%d %H:%M:%S')} (既に終了)")
            if reset_time_str:
                reset_time = datetime.fromisoformat(reset_time_str)
                print(f"  [リセット時刻] {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  [原因] 記録されていません")
        print()
    
    print("=" * 60)

if __name__ == "__main__":
    check_reasons()










