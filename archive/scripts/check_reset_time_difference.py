# -*- coding: utf-8 -*-
"""
エラー時刻とリセット時刻の差を確認するスクリプト
"""
import json
from datetime import datetime, timezone

def main():
    with open('rate_limit_state.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for account_key, account_name in [('365bot', '365botGary'), ('pursahs', 'pursahsgospel')]:
        if account_key not in data:
            continue
        
        account_data = data[account_key]
        reset_time_str = account_data.get('reset_time')
        error_time_str = account_data.get('error_time')
        
        if not reset_time_str or not error_time_str:
            print(f"{account_name}: データが不足しています")
            continue
        
        reset_time = datetime.fromisoformat(reset_time_str)
        error_time = datetime.fromisoformat(error_time_str)
        
        # error_timeがタイムゾーンなしの場合は、ローカルタイムゾーン（JST）として扱う
        # しかし、reset_timeはUTCなので、error_timeもUTCに変換する必要がある
        if error_time.tzinfo is None:
            # error_timeはローカルタイムゾーン（JST）で記録されている可能性が高い
            # JSTはUTC+9なので、9時間引いてUTCに変換
            from datetime import timedelta
            error_time_utc = error_time.replace(tzinfo=timezone.utc) - timedelta(hours=9)
        else:
            error_time_utc = error_time.astimezone(timezone.utc)
        
        # reset_timeがタイムゾーンなしの場合は、UTCとして扱う
        if reset_time.tzinfo is None:
            reset_time_utc = reset_time.replace(tzinfo=timezone.utc)
        else:
            reset_time_utc = reset_time.astimezone(timezone.utc)
        
        diff_seconds = (reset_time_utc - error_time_utc).total_seconds()
        diff_minutes = diff_seconds / 60
        
        print(f"\n{account_name}:")
        print(f"  エラー時刻 (JST): {error_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  エラー時刻 (UTC): {error_time_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  リセット時刻 (UTC): {reset_time_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  差: {diff_minutes:.1f}分 ({diff_seconds:.0f}秒)")
        
        if abs(diff_minutes - 15) < 0.5:
            print(f"  → ほぼ15分後です（XのAPIが15分間のスライディングウィンドウを返している）")
        elif diff_minutes < 15:
            print(f"  → {diff_minutes:.1f}分後（15分未満）")
        else:
            print(f"  → {diff_minutes:.1f}分後（15分を超えています）")

if __name__ == "__main__":
    main()

