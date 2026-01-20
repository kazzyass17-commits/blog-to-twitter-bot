$ErrorActionPreference = "SilentlyContinue"

$workdir = "C:\Users\kazz17\.cursor\blog-to-twitter-bot-temp"
$pyw = "C:\Users\kazz17\AppData\Local\Python\bin\pythonw.exe"
if (!(Test-Path $pyw)) {
    $pyw = "C:\Users\kazz17\AppData\Local\Python\bin\python.exe"
}

# 既存スケジューラ停止（ロックが残っていても無視）
$lockPid = Get-Content "$workdir\scheduler.lock" -ErrorAction SilentlyContinue
if ($lockPid) { Stop-Process -Id $lockPid -Force -ErrorAction SilentlyContinue }
Remove-Item "$workdir\scheduler.lock","$workdir\scheduler_startup.lock" -Force -ErrorAction SilentlyContinue

$env:PYTHONIOENCODING = "utf-8"
Start-Process -FilePath $pyw -ArgumentList "scheduler.py" -WorkingDirectory $workdir -WindowStyle Hidden | Out-Null
