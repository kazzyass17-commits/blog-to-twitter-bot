"""スケジューラーが実際に実行中か確認"""
import os
import sys

lock_file = "scheduler.lock"

print("="*60)
print("スケジューラーの実行状況確認")
print("="*60)

# ロックファイルの確認
if os.path.exists(lock_file):
    print(f"\nロックファイル存在: {lock_file}")
    try:
        with open(lock_file, 'r') as f:
            lock_pid = int(f.read().strip())
        print(f"ロックファイルのPID: {lock_pid}")
        
        # プロセスが実行中か確認
        try:
            import psutil
            if psutil.pid_exists(lock_pid):
                proc = psutil.Process(lock_pid)
                cmdline = proc.cmdline()
                if any('scheduler.py' in str(arg) for arg in cmdline):
                    print(f"[OK] スケジューラーは実行中です（PID: {lock_pid}）")
                    print(f"  コマンドライン: {' '.join(cmdline)}")
                else:
                    print(f"[NG] PID {lock_pid} は存在しますが、scheduler.pyではありません")
                    print(f"  コマンドライン: {' '.join(cmdline)}")
            else:
                print(f"[NG] PID {lock_pid} のプロセスは存在しません（古いロックファイル）")
        except ImportError:
            print("[WARN] psutilがインストールされていません。プロセスの確認ができません。")
        except Exception as e:
            print(f"[NG] プロセス確認エラー: {e}")
    except Exception as e:
        print(f"[NG] ロックファイルの読み込みエラー: {e}")
else:
    print(f"\nロックファイルなし: {lock_file}")
    print("[NG] スケジューラーは実行中ではありません")

# 全Pythonプロセスからscheduler.pyを検索
try:
    import psutil
    print(f"\n全Pythonプロセスからscheduler.pyを検索:")
    found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('scheduler.py' in str(arg) for arg in cmdline):
                    print(f"  [OK] 実行中: PID={proc.info['pid']}, コマンドライン={' '.join(cmdline)}")
                    found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not found:
        print("  [NG] scheduler.pyを実行しているプロセスは見つかりませんでした")
except ImportError:
    print("\n[WARN] psutilがインストールされていません。プロセスの検索ができません。")
except Exception as e:
    print(f"\n[NG] プロセス検索エラー: {e}")
