"""待機状態を確認するスクリプト"""
import json
from datetime import datetime
import os
import sys
import io

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RATE_LIMIT_STATE_FILE = "rate_limit_state.json"

def check_state():
    """待機状態を確認"""
    if not os.path.exists(RATE_LIMIT_STATE_FILE):
        print("rate_limit_state.json が存在しません。")
        return
    
    with open(RATE_LIMIT_STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    now = datetime.now()
    print("=" * 60)
    print("待機状態の確認")
    print("=" * 60)
    print(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for account_key, account_name in [('365bot', '365botGary'), ('pursahs', 'pursahsgospel')]:
        account_state = state.get(account_key, {})
        wait_until_str = account_state.get('wait_until')
        reset_time_str = account_state.get('reset_time')
        
        print(f"{account_name}:")
        if wait_until_str:
            wait_until = datetime.fromisoformat(wait_until_str)
            if wait_until > now:
                wait_seconds = (wait_until - now).total_seconds()
                print(f"  [WARNING] 待機中")
                print(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  残り時間: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                if reset_time_str:
                    reset_time = datetime.fromisoformat(reset_time_str)
                    print(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"  [OK] 待機時間は既に過ぎています（クリア可能）")
                print(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  [OK] 待機時間は設定されていません（投稿可能）")
        print()
    
    print("=" * 60)

if __name__ == "__main__":
    check_state()

