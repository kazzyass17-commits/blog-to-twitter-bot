# 実行中のプロセスとスケジュールの確認結果

## GitHub Actionsワークフロー

### 削除済み
- ✅ `scheduled_posts.yml` - 削除済み（コミット・プッシュ済み）

### 手動実行のみ（スケジュール実行なし）
- `test_190_chars.yml` - workflow_dispatchのみ
- `test_190_chars_main.yml` - workflow_dispatchのみ
- `test_connection.yml` - workflow_dispatchのみ
- `test_diagnose.yml` - workflow_dispatchのみ
- `test_post.yml` - workflow_dispatchのみ

**結論**: GitHub Actionsからの自動実行は停止済み

## ローカルのスケジュールスクリプト

### 存在するスクリプト
- `schedule.py` - 両アカウント用（手動実行が必要）
- `schedule_365bot.py` - 365botGary専用（手動実行が必要）
- `schedule_pursahs.py` - pursahsgospel専用（手動実行が必要）

**注意**: これらのスクリプトは手動で実行する必要があります。バックグラウンドで実行されている場合は、プロセスを確認してください。

## 確認すべき項目

1. **実行中のPythonプロセス**
   - `schedule.py`が実行中か
   - `main.py`が実行中か
   - `main_365bot.py`が実行中か
   - `main_pursahs.py`が実行中か

2. **Windowsタスクスケジューラ**
   - タスクが登録されているか
   - タスクが有効になっているか

3. **ロックファイル**
   - `schedule.lock`が存在するか（実行中の可能性）

