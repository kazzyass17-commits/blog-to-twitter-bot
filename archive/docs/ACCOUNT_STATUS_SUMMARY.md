# アカウント別 投稿テスト結果まとめ

## 現在の状態（2026-01-03 18:35時点）

### 365botGary

**待機状態:**
- ⚠️ **待機中**（残り約47秒）
- 待機終了時刻: 2026-01-03 18:36:11
- リセット時刻: 2026-01-03 18:35:11

**接続テスト:**
- ✅ **接続成功**
  - ユーザー名: @365botGary
  - 表示名: 神の使者365日の言葉bot
  - ユーザーID: 2420551951
  - ツイート取得: 成功

**認証情報:**
- ✅ API Key: 設定済み
- ✅ API Secret: 設定済み
- ✅ Access Token: 設定済み（再生成済み）
- ✅ Access Token Secret: 設定済み（再生成済み）
- ✅ Bearer Token: 設定済み

**投稿テスト:**
- ❌ **投稿失敗**
  - エラー: 429 Too Many Requests（レート制限）
  - 原因: `test_post.py`を実行した際にレート制限が発生
  - 結果: 待機時間が設定された

**フォーマット設定:**
- ✅ **タイトルなしで本文のみ投稿**（修正済み）

**問題点:**
- レート制限が発生し、投稿に失敗
- 待機時間が設定されているため、現在は投稿不可

---

### pursahsgospel

**待機状態:**
- ⚠️ **待機中**（残り約46秒）
- 待機終了時刻: 2026-01-03 18:36:10
- リセット時刻: 2026-01-03 18:35:10

**接続テスト:**
- ✅ **接続成功**
  - ユーザー名: @pursahsgospel
  - 表示名: パーサーによる福音の言葉bot
  - ユーザーID: 2416625168
  - ツイート取得: 成功

**認証情報:**
- ✅ API Key: 設定済み
- ✅ API Secret: 設定済み
- ✅ Access Token: 設定済み（再生成済み）
- ✅ Access Token Secret: 設定済み（再生成済み）
- ✅ Bearer Token: 設定済み

**投稿テスト:**
- ❌ **投稿失敗または未実行**
  - `test_post_with_rate_limit_management.py`の実行がタイムアウト
  - レート制限が発生した可能性

**フォーマット設定:**
- ✅ **タイトル + 本文で投稿**（デフォルト設定）

**問題点:**
- 投稿テストの実行がタイムアウト
- 待機時間が設定されているため、現在は投稿不可

---

## 共通の問題点

### 1. レート制限（429 Too Many Requests）

**症状:**
- 両方のアカウントでレート制限が発生
- 待機時間が設定されている

**原因:**
- `test_post.py`を実行した際にレート制限が発生
- `test_post_with_rate_limit_management.py`でもレート制限が発生した可能性

**対処法:**
- 待機時間が終了するまで待つ
- 待機時間が終了したら、再度投稿テストを実行

### 2. プログラムの分離

**現状:**
- ✅ `main_365bot.py`: 365botGary専用（分離済み）
- ✅ `main_pursahs.py`: pursahsgospel専用（分離済み）
- ✅ `schedule_365bot.py`: 365botGary専用スケジューラー（分離済み）
- ✅ `schedule_pursahs.py`: pursahsgospel専用スケジューラー（分離済み）
- ✅ `test_post_with_rate_limit_management.py`: `--account`オプション追加（修正済み）

**問題:**
- `test_post.py`は`rate_limit_state.json`を更新しない
- そのため、`test_post.py`でレート制限が発生しても、状態が保存されない

---

## 次のステップ

### 1. 待機時間が終了したら

1. **待機時間の確認**
   ```powershell
   python check_rate_limit_state.py
   ```

2. **投稿テストの実行**
   ```powershell
   # 365botGaryのみ
   python test_post_with_rate_limit_management.py --account 365bot --yes
   
   # pursahsgospelのみ
   python test_post_with_rate_limit_management.py --account pursahs --yes
   ```

### 2. プログラムの確認

- ✅ 365botGary: タイトルなしで本文のみ投稿（修正済み）
- ✅ pursahsgospel: タイトル + 本文で投稿（デフォルト）
- ✅ レート制限管理: 実装済み
- ✅ アカウント分離: 完了

### 3. 推奨事項

1. **待機時間が終了するまで待つ**
   - 現在、両方のアカウントが待機中
   - 待機時間が終了したら、再度投稿テストを実行

2. **`test_post_with_rate_limit_management.py`を使用**
   - `test_post.py`は`rate_limit_state.json`を更新しない
   - `test_post_with_rate_limit_management.py`を使用することで、レート制限管理が機能する

3. **個別に実行**
   - `--account`オプションで個別に実行可能
   - 一方が待機中でも、もう一方は実行可能

---

## まとめ

| アカウント | 接続テスト | 認証情報 | 投稿テスト | 待機状態 | フォーマット |
|-----------|----------|---------|-----------|---------|------------|
| 365botGary | ✅ 成功 | ✅ 設定済み | ❌ 失敗（429） | ⚠️ 待機中 | ✅ タイトルなし |
| pursahsgospel | ✅ 成功 | ✅ 設定済み | ❌ 失敗/未実行 | ⚠️ 待機中 | ✅ タイトルあり |

**結論:**
- 両方のアカウントで接続テストは成功
- 認証情報は正しく設定されている
- 投稿テストでレート制限が発生し、現在は待機中
- 待機時間が終了したら、再度投稿テストを実行する必要がある










