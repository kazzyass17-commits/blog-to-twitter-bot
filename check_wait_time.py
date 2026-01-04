"""
待機時間の残り時間を確認するスクリプト
X側のレート制限が原因なので、待機時間をクリアせず、残り時間のみ確認します
"""
import json
import os
from datetime import datetime

RATE_LIMIT_STATE_FILE = "rate_limit_state.json"

def check_wait_time():
    """待機時間の残り時間を確認"""
    if not os.path.exists(RATE_LIMIT_STATE_FILE):
        print("待機時間の状態ファイルが見つかりません。")
        return
    
    with open(RATE_LIMIT_STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    now = datetime.now()
    account_names = {
        '365bot': '365botGary',
        'pursahs': 'pursahsgospel'
    }
    
    print("=" * 60)
    print("待機時間の確認")
    print("=" * 60)
    print(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    for key, account_name in account_names.items():
        account_state = state.get(key, {})
        wait_until_str = account_state.get('wait_until')
        reset_time_str = account_state.get('reset_time')
        
        print(f"{account_name}:")
        if wait_until_str:
            wait_until = datetime.fromisoformat(wait_until_str)
            remaining = (wait_until - now).total_seconds()
            
            if remaining > 0:
                print(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  残り時間: {int(remaining)} 秒（{int(remaining // 60)} 分）")
                if reset_time_str:
                    reset_time = datetime.fromisoformat(reset_time_str)
                    print(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  → このアカウントは待機中です。投稿テストは実行できません。")
            else:
                print(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  → 待機時間は過ぎています。投稿テストを実行できます。")
        else:
            print(f"  → 待機時間は設定されていません。投稿テストを実行できます。")
        print("")
    
    print("=" * 60)
    print("注意: X側のレート制限が原因なので、待機時間をクリアすることはできません。")
    print("      待機時間が終了するまで待つ必要があります。")
    print("=" * 60)

if __name__ == "__main__":
    check_wait_time()








