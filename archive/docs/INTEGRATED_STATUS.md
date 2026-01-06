# 統合されたチャット状況まとめ

## 以前のチャット「network disconnected error」の内容（HANDOVER.mdより）

### 作成されたスクリプト
- **`post_both_accounts.py`**: 両方のアカウントで投稿を実施するスクリプト
  - 365botGary用とpursahsgospel用のそれぞれのブログからランダムに1つずつ投稿を選ぶ
  - 各アカウントの待機時間をチェックしてから投稿
  - レート制限エラー（429）が発生した場合は原因を記録

### 重要な設定（以前のチャット）
- **365botGary**: タイトルなしで投稿（本文のみ）
- **pursahsgospel**: タイトルありで投稿
- 文字数制限: 最大280文字（URLは23文字としてカウント）

### レート制限管理（以前のチャット）
- `rate_limit_checker.py`で待機時間を管理
- `rate_limit_state.json`に待機状態を保存
- 429エラー発生時は原因を記録して次のアカウントに移る

## 現在のチャットの内容

### 主な問題と解決策

#### 1. 429エラー（レート制限）
- **状況**: 投稿時に429 Too Many Requestsエラーが発生
- **原因**: X APIの15分間のスライディングウィンドウでレート制限に達している
- **対策**: 
  - `reset_time`をX APIのヘッダーから取得して待機時間を管理（UTCタイムスタンプとして正しく解釈）
  - `check_and_wait_for_account`で状況確認（ただし、`create_tweet`を呼び出さないように修正済み）
  - `main.py`から`check_and_wait_for_account`の呼び出しを削除（過去の成功パターンに合わせる）

#### 2. 403エラー（IPブロック）
- **状況**: GitHub ActionsからX APIにアクセスすると403 Forbiddenエラーが発生
- **原因**: GitHub ActionsのIPアドレスがCloudflareによってブロックされている
- **対策**: 
  - ローカル実行（Windowsタスクスケジューラ + `schedule.py`）に移行
  - GitHub ActionsのIPブロック回避は現状維持

#### 3. 文字数制限
- **現在の設定**: 188文字（URL含む）
  - 365botGary: 165文字（タイトル含む）+ 改行1 + URL 23 = 189文字 → 188文字に調整
  - pursahsgospel: 164文字（タイトルなし）+ 改行2 + URL 23 = 189文字 → 188文字に調整
  - 「語録***」の後に改行を挿入（pursahsgospelのみ）

### 現在の実装状況

#### 主要ファイル
- **`main.py`**: メインの投稿スクリプト（`--account both`で両方のアカウントに対応）
  - `check_and_wait_for_account`の呼び出しを削除済み（過去の成功パターンに合わせる）
- **`post_both_accounts.py`**: 両アカウント投稿スクリプト（以前のチャットで作成）
  - `check_and_wait_for_account`を呼び出している（`skip_wait=False`）
- **`schedule.py`**: ローカルスケジューラー（1日3回：8時、14時、20時）
- **`twitter_poster.py`**: X APIへの投稿処理
- **`rate_limit_checker.py`**: レート制限の管理（`create_tweet`を呼び出さないように修正済み）

#### レート制限管理
- `rate_limit_state.json`: レート制限の状態を保存
- `reset_time`: X APIのヘッダーから取得したUTCタイムスタンプ
- `check_and_wait_for_account`: ローカルファイルのみを確認（API呼び出しなし）

#### ロックファイル機能
- `main.lock`: `main.py`の重複実行を防止
- `schedule.lock`: `schedule.py`の重複実行を防止
- `psutil`を使用してプロセス重複を検出

## 統合すべき内容

### 1. スクリプトの統合
- **`main.py`**: 現在使用中（`--account both`で両方のアカウントに対応）
- **`post_both_accounts.py`**: 以前のチャットで作成（専用スクリプト）
- **推奨**: `main.py`を使用（より柔軟で、`--account`オプションで個別実行も可能）

### 2. 待機時間チェックの違い
- **`post_both_accounts.py`**: `check_and_wait_for_account(account_key, twitter_handle, skip_wait=False)`を呼び出し
- **`main.py`**: `check_and_wait_for_account`の呼び出しを削除（過去の成功パターンに合わせる）
- **現在の方針**: `main.py`の方式（待機時間チェックなしで直接投稿）を使用

### 3. 文字数制限の変更
- **以前**: 最大280文字
- **現在**: 188文字（URL含む）
- **理由**: 403エラーを回避するため、より短い文字数に調整

### 4. タイトル設定の変更
- **以前**: 365botGaryはタイトルなし、pursahsgospelはタイトルあり
- **現在**: 365botGaryはタイトルあり、pursahsgospelはタイトルなし（「語録***」の後に改行）
- **理由**: 文字数制限と403エラー回避のため

## 次のステップ

1. **`main.py`を継続使用**（`--account both`で両方のアカウントに対応）
2. **`post_both_accounts.py`は参考として保持**（必要に応じて参照）
3. **現在の実装を維持**（待機時間チェックなしで直接投稿、188文字制限）

## 確認用コマンド

```powershell
# 待機時間の確認
python check_current_wait_time.py

# レート制限状態の確認
python check_rate_limit_reasons.py

# メインスクリプトの実行（両方のアカウント）
python main.py --account both

# メインスクリプトの実行（個別）
python main.py --account 365bot
python main.py --account pursahs
```




