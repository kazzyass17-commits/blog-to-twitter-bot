"""残りの不要ファイルを移動"""
import shutil
import os
from pathlib import Path

base_dir = Path(__file__).parent
archive_scripts_dir = base_dir / "archive" / "scripts"

# このファイル自体も移動
files_to_move = ["organize_files.py", "update_env.ps1", "update_pursahs_env.ps1", "move_remaining.py"]

for file_name in files_to_move:
    file_path = base_dir / file_name
    if file_path.exists():
        try:
            shutil.move(str(file_path), archive_scripts_dir / file_name)
            print(f"移動: {file_name}")
        except Exception as e:
            print(f"エラー: {file_name} - {e}")

print("完了")

