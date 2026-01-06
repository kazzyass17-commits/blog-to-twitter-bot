"""
運用に不要なファイルをarchiveディレクトリに移動するスクリプト
"""
import os
import shutil
from pathlib import Path

# ベースディレクトリ
base_dir = Path(__file__).parent

# archiveディレクトリを作成
archive_dir = base_dir / "archive"
archive_scripts_dir = archive_dir / "scripts"
archive_docs_dir = archive_dir / "docs"

archive_scripts_dir.mkdir(parents=True, exist_ok=True)
archive_docs_dir.mkdir(parents=True, exist_ok=True)

# 運用に必要なファイル（移動しない）
essential_files = {
    "post_both_accounts.py",
    "schedule.py",
    "twitter_poster.py",
    "blog_fetcher.py",
    "database.py",
    "config.py",
    "rate_limit_checker.py",
    "requirements.txt",
    "env.example.txt",
    "init_posts.py",
    "organize_files.py",  # このスクリプト自体
    "README.md",  # READMEは残す
}

# 移動するファイルパターン
patterns_to_move = {
    "test_*.py": archive_scripts_dir,
    "check_*.py": archive_scripts_dir,
    "analyze_*.py": archive_scripts_dir,
    "compare_*.py": archive_scripts_dir,
    "debug_*.py": archive_scripts_dir,
    "verify_*.py": archive_scripts_dir,
    "diagnose_*.py": archive_scripts_dir,
}

# 特定のファイルを移動
specific_files_to_move = {
    "main_365bot.py": archive_scripts_dir,
    "main_pursahs.py": archive_scripts_dir,
    "main.py": archive_scripts_dir,
    "schedule_365bot.py": archive_scripts_dir,
    "schedule_pursahs.py": archive_scripts_dir,
    "post_single_page.py": archive_scripts_dir,
    "simple_post.py": archive_scripts_dir,
    "run_scheduled_test.py": archive_scripts_dir,
    "wait_15min.py": archive_scripts_dir,
    "fetch_actual_titles.py": archive_scripts_dir,
    "find_missing_goroku.py": archive_scripts_dir,
    "index_extractor.py": archive_scripts_dir,
    "save_html.py": archive_scripts_dir,
    "pdf_generator.py": archive_scripts_dir,
    "init_posts_from_index.py": archive_scripts_dir,
}

# MDファイル（README.md以外）を移動
md_files_to_move = []

# その他のファイル
other_files_to_move = {
    "*.html": archive_scripts_dir,
    "*.bat": archive_scripts_dir,
    "*.yml": archive_scripts_dir,
    "*.example": archive_scripts_dir,
}

def move_files():
    moved_count = 0
    
    # パターンマッチングで移動
    import glob
    for pattern, dest_dir in patterns_to_move.items():
        for file_path in glob.glob(str(base_dir / pattern)):
            file_name = os.path.basename(file_path)
            if file_name not in essential_files:
                try:
                    shutil.move(file_path, dest_dir / file_name)
                    print(f"移動: {file_name} -> {dest_dir.name}/")
                    moved_count += 1
                except Exception as e:
                    print(f"エラー（移動失敗）: {file_name} - {e}")
    
    # 特定のファイルを移動
    for file_name, dest_dir in specific_files_to_move.items():
        file_path = base_dir / file_name
        if file_path.exists() and file_name not in essential_files:
            try:
                shutil.move(str(file_path), dest_dir / file_name)
                print(f"移動: {file_name} -> {dest_dir.name}/")
                moved_count += 1
            except Exception as e:
                print(f"エラー（移動失敗）: {file_name} - {e}")
    
    # MDファイルを移動（README.md以外）
    for md_file in glob.glob(str(base_dir / "*.md")):
        file_name = os.path.basename(md_file)
        if file_name not in essential_files:
            try:
                shutil.move(md_file, archive_docs_dir / file_name)
                print(f"移動: {file_name} -> docs/")
                moved_count += 1
            except Exception as e:
                print(f"エラー（移動失敗）: {file_name} - {e}")
    
    # その他のファイル（.ps1, .html, .bat, .yml, .example）
    for pattern, dest_dir in other_files_to_move.items():
        for file_path in glob.glob(str(base_dir / pattern)):
            file_name = os.path.basename(file_path)
            if file_name not in essential_files:
                try:
                    shutil.move(file_path, dest_dir / file_name)
                    print(f"移動: {file_name} -> {dest_dir.name}/")
                    moved_count += 1
                except Exception as e:
                    print(f"エラー（移動失敗）: {file_name} - {e}")
    
    print(f"\n合計 {moved_count} ファイルを移動しました。")

if __name__ == "__main__":
    print("ファイル整理を開始します...")
    move_files()
    print("完了しました。")

