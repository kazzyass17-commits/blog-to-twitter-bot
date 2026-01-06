# -*- coding: utf-8 -*-
"""
現在の待ち時間を確認するスクリプト
"""
import json
from datetime import datetime, timezone

def main():
    with open('rate_limit_state.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    now_utc = datetime.now(timezone.utc)
    now_jst = datetime.now()
    
    print("=" * 60)
    print("現在の待ち時間確認")
    print("=" * 60)
    print(f"現在時刻 (JST): {now_jst.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"現在時刻 (UTC): {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    for account_key, account_name in [('365bot', '365botGary'), ('pursahs', 'pursahsgospel')]:
        if account_key not in data:
            continue
        
        account_data = data[account_key]
        reset_time_str = account_data.get('reset_time')
        
        print(f"{account_name}:")
        
        if not reset_time_str:
            print("  リセット時刻: 不明（reset_timeが取得できませんでした）")
            print("  待ち時間: 不明")
        else:
            reset_time = datetime.fromisoformat(reset_time_str)
            
            # reset_timeがタイムゾーンなしの場合は、UTCとして扱う
            if reset_time.tzinfo is None:
                reset_time = reset_time.replace(tzinfo=timezone.utc)
            else:
                reset_time = reset_time.astimezone(timezone.utc)
            
            diff_seconds = (reset_time - now_utc).total_seconds()
            diff_minutes = int(diff_seconds // 60)
            diff_seconds_remainder = int(diff_seconds % 60)
            
            from datetime import timedelta
            reset_time_jst = reset_time + timedelta(hours=9)  # UTC+9 = JST
            print(f"  リセット時刻 (UTC): {reset_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"  リセット時刻 (JST): {reset_time_jst.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if diff_seconds > 0:
                print(f"  残り時間: {diff_minutes}分 {diff_seconds_remainder}秒")
                print(f"  残り時間 (合計): {int(diff_seconds)}秒")
            else:
                print(f"  待ち時間: 終了済み（投稿可能）")
        
        print()

if __name__ == "__main__":
    main()

