"""45分おきに3回投稿し、その後スケジューラーを起動"""
import subprocess
import time
import os
import sys
from datetime import datetime

# ログ出力用
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    with open("post_3times_45min.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

# 作業ディレクトリを設定
os.chdir(os.path.dirname(os.path.abspath(__file__)))

log("="*60)
log("45分おきに3回投稿スクリプト開始")
log("="*60)

# 1回目は既に投稿済みなので、残り2回
remaining_posts = 2
wait_minutes = 45

for i in range(remaining_posts):
    post_num = i + 2  # 2回目、3回目
    
    log(f"次の投稿まで{wait_minutes}分待機中...")
    time.sleep(wait_minutes * 60)
    
    log(f"{post_num}回目の投稿を実行中...")
    try:
        result = subprocess.run(
            [sys.executable, "post_both_accounts.py"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300
        )
        if result.returncode == 0:
            log(f"{post_num}回目の投稿成功")
        else:
            log(f"{post_num}回目の投稿失敗: {result.stderr}")
    except Exception as e:
        log(f"{post_num}回目の投稿エラー: {e}")

log("="*60)
log("3回の投稿完了。スケジューラーを起動します...")
log("="*60)

# 古いロックファイルを削除
lock_file = "scheduler.lock"
if os.path.exists(lock_file):
    try:
        os.remove(lock_file)
        log(f"古いロックファイルを削除: {lock_file}")
    except Exception as e:
        log(f"ロックファイル削除エラー: {e}")

# スケジューラーを起動（pythonwで非表示で起動）
try:
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    subprocess.Popen(
        [pythonw, "scheduler.py"],
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
    )
    log("スケジューラーを起動しました")
except Exception as e:
    log(f"スケジューラー起動エラー: {e}")

log("スクリプト終了")
