@echo off
REM Twitter自動投稿バッチファイル
REM Windowsタスクスケジューラから実行するためのバッチファイル

cd /d C:\Users\kazz17\.cursor\blog-to-twitter-bot-temp

REM ログファイルに出力（追記モード）
python main.py >> log.txt 2>&1

REM エラーレベルを確認
if %ERRORLEVEL% NEQ 0 (
    echo エラーが発生しました。エラーレベル: %ERRORLEVEL% >> log.txt
    exit /b %ERRORLEVEL%
)

echo 実行完了: %DATE% %TIME% >> log.txt

