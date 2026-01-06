# 現在のチャット状況まとめ

## プロジェクト概要
X（Twitter）への自動投稿ボット - ブログ記事をXに自動投稿するシステム

## 現在の主な問題

### 1. 429エラー（レート制限）
- **状況**: 投稿時に429 Too Many Requestsエラーが発生
- **原因**: X APIの15分間のスライディングウィンドウでレート制限に達している
- **対策**: 
  - `reset_time`をX APIのヘッダーから取得して待機時間を管理
  - `check_and_wait_for_account`で状況確認（ただし、`create_tweet`を呼び出さないように修正済み）
  - `main.py`から`check_and_wait_for_account`の呼び出しを削除（過去の成功パターンに合わせる）

### 2. 403エラー（IPブロック）
- **状況**: GitHub ActionsからX APIにアクセスすると403 Forbiddenエラーが発生
- **原因**: GitHub ActionsのIPアドレスがCloudflareによってブロックされている
- **対策**: 
  - ローカル実行（Windowsタスクスケジューラ + `schedule.py`）に移行
  - GitHub ActionsのIPブロック回避は現状維持（プロキシ、VPS、セルフホストランナーなどの選択肢あり）

### 3. 文字数制限
- **状況**: 188文字（URL含む）で投稿
- **設定**:
  - 365botGary: 165文字（タイトル含む）+ 改行1 + URL 23 = 189文字 → 188文字に調整
  - pursahsgospel: 164文字（タイトルなし）+ 改行2 + URL 23 = 189文字 → 188文字に調整
  - 「語録***」の後に改行を挿入（pursahsgospelのみ）

## 現在の実装状況

### 主要ファイル
- `main.py`: メインの投稿スクリプト（`check_and_wait_for_account`の呼び出しを削除済み）
- `schedule.py`: ローカルスケジューラー（1日3回：8時、14時、20時）
- `twitter_poster.py`: X APIへの投稿処理
- `rate_limit_checker.py`: レート制限の管理（`create_tweet`を呼び出さないように修正済み）

### レート制限管理
- `rate_limit_state.json`: レート制限の状態を保存
- `reset_time`: X APIのヘッダーから取得したUTCタイムスタンプ
- `check_and_wait_for_account`: ローカルファイルのみを確認（API呼び出しなし）

### ロックファイル機能
- `main.lock`: `main.py`の重複実行を防止
- `schedule.lock`: `schedule.py`の重複実行を防止
- `psutil`を使用してプロセス重複を検出

## 以前のチャットとの統合が必要な情報

### 「network disconnected error」チャット
- **タイトル**: "network disconnected error"
- **内容**: 不明（ユーザーが詳細を知らない）
- **統合が必要**: 以前のチャットで解決した問題や実装内容を確認する必要がある

## 次のステップ

1. 以前のチャット「network disconnected error」の内容を確認
2. 現在の実装と以前のチャットの解決内容を統合
3. ネットワーク切断エラーへの対処が現在の実装に含まれているか確認




