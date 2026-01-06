"""
既に発生した429エラーの情報を分析するスクリプト
rate_limit_state.jsonから情報を読み込んで分析
"""
import json
import os
from datetime import datetime

RATE_LIMIT_STATE_FILE = "rate_limit_state.json"


def analyze_rate_limit_state():
    """既に発生した429エラーの情報を分析"""
    if not os.path.exists(RATE_LIMIT_STATE_FILE):
        print(f"エラー: {RATE_LIMIT_STATE_FILE} が見つかりません")
        return
    
    with open(RATE_LIMIT_STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    print("=" * 60)
    print("既に発生した429エラーの情報を分析")
    print("=" * 60)
    
    for account_key, account_state in state.items():
        account_name = '365botGary' if account_key == '365bot' else 'pursahsgospel'
        print(f"\n[{account_name}]")
        print(f"  エラー発生時刻: {account_state.get('error_time', 'N/A')}")
        print(f"  APIエンドポイント: {account_state.get('api_endpoint', 'N/A')}")
        print(f"  リセット時刻: {account_state.get('reset_time', 'N/A')}")
        print(f"  待機終了時刻: {account_state.get('wait_until', 'N/A')}")
        
        rate_limit_limit = account_state.get('rate_limit_limit')
        rate_limit_remaining = account_state.get('rate_limit_remaining')
        used_count = account_state.get('used_count')
        
        if rate_limit_limit is not None and rate_limit_remaining is not None:
            print(f"\n  レート制限の状態:")
            print(f"    上限: {rate_limit_limit} リクエスト")
            print(f"    残り: {rate_limit_remaining} リクエスト")
            print(f"    使用済み: {used_count} リクエスト")
            print(f"    15分間のウィンドウ内で {used_count} リクエストがカウントされています")
        else:
            print(f"\n  警告: レート制限の詳細情報（x-rate-limit-limit, x-rate-limit-remaining）が記録されていません")
            print(f"  次回429エラーが発生した際に、詳細情報が記録されます")
        
        # エラー発生時刻と現在時刻の比較
        error_time_str = account_state.get('error_time')
        if error_time_str:
            try:
                error_time = datetime.fromisoformat(error_time_str)
                now = datetime.now()
                elapsed = (now - error_time).total_seconds()
                print(f"\n  エラー発生からの経過時間: {int(elapsed)} 秒（{int(elapsed // 60)} 分）")
                
                reset_time_str = account_state.get('reset_time')
                if reset_time_str:
                    reset_time = datetime.fromisoformat(reset_time_str)
                    if reset_time > now:
                        wait_seconds = (reset_time - now).total_seconds()
                        print(f"  リセットまで: {int(wait_seconds)} 秒（{int(wait_seconds // 60)} 分）")
                    else:
                        print(f"  リセット時刻は既に過ぎています")
            except Exception as e:
                print(f"  エラー: 時刻の解析に失敗しました: {e}")


if __name__ == "__main__":
    analyze_rate_limit_state()







