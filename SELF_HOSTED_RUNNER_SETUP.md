# GitHub Actions セルフホストランナー設定ガイド

GitHub Actionsのセルフホストランナーを設定して、CloudflareのIPブロックを回避します。

## 前提条件

- Windows 10/11 がインストールされたPC
- GitHubリポジトリへの管理者権限
- PCが常時起動している（またはスケジュール実行時に起動している）

## セットアップ手順

### ステップ1: GitHubリポジトリでランナーを追加

1. GitHubリポジトリにアクセス
2. **Settings** → **Actions** → **Runners** を開く
3. **New self-hosted runner** ボタンをクリック
4. **Windows** を選択
5. 表示されるコマンドをコピー（例：`./config.cmd --url https://github.com/ユーザー名/リポジトリ名 --token XXXXXXXXXX`）

### ステップ2: PCでランナーをセットアップ

1. PowerShellを管理者として開く
2. プロジェクトディレクトリに移動：
   ```powershell
   cd C:\Users\kazz17\.cursor\blog-to-twitter-bot-temp
   ```

3. ランナーをダウンロード（GitHubから提供されるコマンドを実行）：
   ```powershell
   # 例（実際のコマンドはGitHubから取得）
   Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-win-x64-2.311.0.zip" -OutFile "actions-runner-win-x64-2.311.0.zip"
   ```

4. 解凍：
   ```powershell
   Expand-Archive -Path "actions-runner-win-x64-2.311.0.zip" -DestinationPath "runner"
   ```

5. ランナーを設定（GitHubから提供されるコマンドを実行）：
   ```powershell
   cd runner
   .\config.cmd --url https://github.com/ユーザー名/リポジトリ名 --token XXXXXXXXXX
   ```
   
   設定時に以下の質問に答えます：
   - **Enter the name of the runner**: `windows-runner`（任意の名前）
   - **Enter the name of the runner group**: `Default`（Enterキーでデフォルト）
   - **Enter any additional labels**: `self-hosted,Windows,X64`（Enterキーでデフォルト）
   - **Enter name of work folder**: `_work`（Enterキーでデフォルト）

6. ランナーをサービスとしてインストール（バックグラウンドで実行）：
   ```powershell
   .\run.cmd
   ```
   
   または、Windowsサービスとしてインストール（推奨）：
   ```powershell
   .\svc.cmd install
   .\svc.cmd start
   ```

### ステップ3: ワークフローファイルを更新

セルフホストランナーを使用するようにワークフローファイルを更新します。

#### `test_190_chars.yml` の更新

```yaml
name: Test Post 190 Characters

on:
  workflow_dispatch:  # 手動実行

jobs:
  test-190-chars:
    runs-on: self-hosted  # GitHub-hostedからself-hostedに変更
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    # 以下は同じ...
```

#### `scheduled_posts.yml` の更新

```yaml
name: Scheduled Blog Posts to Twitter

on:
  schedule:
    - cron: '0 */6 * * *'  # 6時間ごと

jobs:
  post-to-twitter:
    runs-on: self-hosted  # GitHub-hostedからself-hostedに変更
    
    # 以下は同じ...
```

### ステップ4: Python環境の確認

セルフホストランナーでPythonが正しく動作するか確認：

1. PowerShellで以下を実行：
   ```powershell
   python --version
   pip --version
   ```

2. 必要に応じてPythonをインストール：
   - [Python公式サイト](https://www.python.org/downloads/)からダウンロード
   - インストール時に「Add Python to PATH」にチェック

### ステップ5: テスト実行

1. GitHub Actionsのページで「Test Post 190 Characters」ワークフローを実行
2. セルフホストランナーで実行されることを確認
3. ログで403エラーが解消されているか確認

## トラブルシューティング

### ランナーが表示されない

- **Settings** → **Actions** → **Runners** でランナーが「Idle」状態になっているか確認
- ランナーのログを確認：
  ```powershell
  cd runner
  .\run.cmd
  ```

### ワークフローが実行されない

- ランナーが「Online」状態になっているか確認
- ランナーのラベルが正しく設定されているか確認
- ワークフローファイルの`runs-on: self-hosted`が正しいか確認

### Pythonが見つからない

- PythonがPATHに追加されているか確認
- ワークフローでPythonのパスを明示的に指定：
  ```yaml
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.11'
      python-version-file: '.python-version'  # オプション
  ```

## セキュリティに関する注意事項

- セルフホストランナーは、リポジトリのコードとシークレットにアクセスできます
- 信頼できる環境でのみ使用してください
- ランナーを実行するPCは、適切にセキュリティ対策を施してください

## ランナーの停止・削除

### ランナーを停止

```powershell
cd runner
.\svc.cmd stop
```

### ランナーを削除

1. GitHubリポジトリの **Settings** → **Actions** → **Runners** でランナーを削除
2. PC上でランナーディレクトリを削除：
   ```powershell
   cd runner
   .\config.cmd remove --token XXXXXXXXXX
   ```

## 参考リンク

- [GitHub Actions セルフホストランナーのドキュメント](https://docs.github.com/ja/actions/hosting-your-own-runners/about-self-hosted-runners)
- [セルフホストランナーの追加](https://docs.github.com/ja/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners)

