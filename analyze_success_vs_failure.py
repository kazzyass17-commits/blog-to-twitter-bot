"""
過去の成功時と現在の失敗時の違いを分析
"""
import json
from datetime import datetime
import sys
import io

# Windowsでの文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_difference():
    """過去の成功時と現在の失敗時の違いを分析"""
    print("=" * 60)
    print("過去の成功時と現在の失敗時の違いを分析")
    print("=" * 60)
    print()
    
    # 過去の成功例
    print("【過去の成功例】")
    print("- ツイートID: 2007267037748568194 (365botGary)")
    print("- ツイートID: 2006912844516978928 (pursahsgospel)")
    print("- 成功した理由: レート制限に達していなかった")
    print()
    
    # 現在の状況
    print("【現在の状況】")
    try:
        with open('rate_limit_state.json', 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        now = datetime.now()
        
        for account_key, account_name in [('365bot', '365botGary'), ('pursahs', 'pursahsgospel')]:
            account_state = state.get(account_key, {})
            wait_until_str = account_state.get('wait_until')
            reset_time_str = account_state.get('reset_time')
            
            print(f"{account_name}:")
            if wait_until_str:
                wait_until = datetime.fromisoformat(wait_until_str)
                if wait_until > now:
                    wait_seconds = (wait_until - now).total_seconds()
                    print(f"  ⚠ 待機中（残り {int(wait_seconds // 60)} 分）")
                    print(f"  待機終了時刻: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"  ✓ 待機時間は過ぎています")
            else:
                print(f"  ✓ 待機時間なし")
            
            if reset_time_str:
                reset_time = datetime.fromisoformat(reset_time_str)
                print(f"  リセット時刻: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    except FileNotFoundError:
        print("rate_limit_state.json が見つかりません。")
    except Exception as e:
        print(f"エラー: {e}")
    
    # 違いの分析
    print("=" * 60)
    print("違いの分析")
    print("=" * 60)
    print()
    print("【過去の成功時】")
    print("1. レート制限に達していなかった")
    print("2. 待機時間が設定されていなかった")
    print("3. 投稿APIを呼び出した際に429エラーが発生しなかった")
    print()
    print("【現在の失敗時】")
    print("1. レート制限に達している（429エラー）")
    print("2. 待機時間が設定されている")
    print("3. 投稿APIを呼び出した際に429エラーが発生している")
    print()
    print("【考えられる原因】")
    print("1. 過去の成功後、レート制限に達するまでに複数回投稿を試みた")
    print("2. 接続テストやその他のAPI呼び出しでレート制限に達した")
    print("3. 待機時間を守らずに複数回投稿を試みた")
    print("4. レート制限のリセット時刻が過ぎていない")
    print()
    print("【解決策】")
    print("1. 待機時間が終了するまで待つ")
    print("2. 待機時間が終了したら、再度投稿を試みる")
    print("3. レート制限を守る（1時間あたり300ツイート）")
    print("4. 接続テストなどの不要なAPI呼び出しを減らす")
    print()
    print("=" * 60)

if __name__ == "__main__":
    analyze_difference()







