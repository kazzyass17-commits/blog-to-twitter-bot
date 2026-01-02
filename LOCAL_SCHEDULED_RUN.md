# ローカルPCでのスケジュール実行方法

## 概要

GitHub ActionsのIPブロック問題を回避するため、しばらくはローカルPCでスケジュール実行する方法です。

## 方法1: Pythonのscheduleライブラリを使用（推奨）

### セットアップ

1. **依存パッケージのインストール**
   ```powershell
   cd c:\Users\kazz17\.cursor\blog-to-twitter-bot-temp
   python -m pip install -r requirements.txt
   ```

2. **.envファイルの作成**
   - `LOCAL_TEST_GUIDE.md`を参照して`.env`ファイルを作成

3. **スケジュール実行スクリプトの実行**
   ```powershell
   python schedule.py
   ```

### スケジュール設定

`schedule.py`で以下の時間に実行されます：
- 8:00 JST（午前8時）
- 14:00 JST（午後2時）
- 20:00 JST（午後8時）

### 実行方法

```powershell
# バックグラウンドで実行（推奨）
Start-Process python -ArgumentList "schedule.py" -WindowStyle Hidden

# または、通常のウィンドウで実行
python schedule.py
```

### 停止方法

- `Ctrl+C`で停止
- タスクマネージャーでPythonプロセスを終了

## 方法2: Windowsタスクスケジューラを使用

### セットアップ手順

1. **バッチファイルを作成**

   `run_bot.bat`を作成：
   ```batch
   @echo off
   cd /d C:\Users\kazz17\.cursor\blog-to-twitter-bot-temp
   python main.py
   ```

2. **タスクスケジューラでタスクを作成**

   - 「タスクスケジューラ」を開く
   - 「基本タスクの作成」をクリック
   - 名前: 「Blog to Twitter Bot」
   - トリガー: 「毎日」
   - 時刻: 8:00、14:00、20:00（3つのタスクを作成）
   - 操作: 「プログラムの開始」
   - プログラム: `C:\Users\kazz17\.cursor\blog-to-twitter-bot-temp\run_bot.bat`

3. **タスクの設定**

   - 「最上位の特権で実行する」にチェック
   - 「ユーザーがログオンしているかどうかにかかわらず実行する」を選択

## 方法3: 手動実行

毎回手動で実行する場合：

```powershell
cd c:\Users\kazz17\.cursor\blog-to-twitter-bot-temp
python main.py
```

## PCを常時起動しておく必要がある

### 注意事項

- **PCが起動している必要があります**
- PCをスリープやシャットダウンすると実行されません
- ノートPCの場合は、電源に接続しておくことを推奨

### 推奨設定

1. **電源設定の変更**
   - スリープを無効化
   - ディスプレイの電源を切るだけにする

2. **自動ログインの設定**（オプション）
   - Windowsの自動ログインを有効化
   - タスクスケジューラで実行する場合に便利

## ログの確認

### ログファイルの場所

- `init_posts.log`: データベース初期化のログ
- コンソール出力: 実行時のログ

### ログの確認方法

```powershell
# ログファイルを確認
Get-Content init_posts.log -Tail 50
```

## トラブルシューティング

### PCが起動していない場合

- タスクスケジューラのタスクは実行されません
- PCを常時起動しておく必要があります

### Pythonが見つからない場合

- Pythonのパスを絶対パスで指定：
  ```batch
   C:\Users\kazz17\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py
   ```

### 認証エラーが発生する場合

- `.env`ファイルの認証情報を確認
- Twitter Developer Portalで認証情報を再生成

## GitHub Actionsへの移行

将来的にGitHub Actionsに移行する場合：

1. IPブロック問題が解決されるのを待つ
2. X Developer Portalのサポートに問い合わせ
3. プロキシサーバーを使用（利用規約を確認）

## まとめ

### 推奨される方法

1. **短期間**: Pythonのscheduleライブラリを使用
2. **長期間**: Windowsタスクスケジューラを使用

### メリット

- ✅ IPブロックの問題を回避
- ✅ ローカル環境で動作確認済み
- ✅ 追加の設定が不要

### デメリット

- ❌ PCを常時起動しておく必要がある
- ❌ PCが故障すると実行されない
- ❌ 手動での管理が必要

