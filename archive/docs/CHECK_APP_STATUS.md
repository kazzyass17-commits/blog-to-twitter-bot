# アプリの状態とX側の承認を確認する方法

## 403エラーが続く場合の確認事項

Bearer Tokenが設定済みでも403エラーが発生する場合、X側の承認やアプリの状態に問題がある可能性があります。

## 確認手順

### ステップ1: アプリの状態を確認

#### 365botGaryアカウント用

1. Twitter Developer Portalにアクセス
2. 「2006671045663797250365botGary」アプリを開く
3. 「Overview」タブを確認
4. 以下を確認：
   - アプリの状態が「Active」になっているか
   - 「Pending approval」「Under review」などの表示がないか
   - エラーメッセージや警告が表示されていないか

#### pursahsgospelアカウント用

1. Twitter Developer Portalにアクセス
2. pursahsgospel用のアプリを開く
3. 「Overview」タブを確認
4. 同様の確認を行う

### ステップ2: アプリの一覧で状態を確認

1. Twitter Developer Portalの「Projects & Apps」を開く
2. アプリの一覧を確認
3. アプリの状態を確認：
   - 「Active」（アクティブ）: 正常
   - 「SUSPENDED」（停止）: 問題あり
   - 「Pending approval」（承認待ち）: 承認が必要

### ステップ3: 権限設定を再確認

1. アプリの「Settings」タブを開く
2. 「App permissions」セクションを確認
3. 「Read and write」が選択されているか確認
4. 選択されていない場合は選択して「Save」

### ステップ4: Access Tokenを再生成

権限を変更した場合、必ずAccess Tokenを再生成してください。

1. 「Keys and tokens」タブを開く
2. 「Access Token and Secret」セクションを探す
3. 「Regenerate」ボタンをクリック
4. 新しいAccess TokenとAccess Token Secretをコピー
5. GitHub Secretsを更新

## X側の承認が必要な場合

### 承認が必要なケース

- 新しく作成したアプリ
- 権限を変更したアプリ
- 使用目的が不明確なアプリ

### 承認を待つ

- 通常、数時間〜数日かかります
- 承認が完了すると、アプリの状態が「Active」になります

### 承認を早める方法

1. アプリの説明をより詳細に記述
2. 使用目的を明確に記述
3. プライバシーポリシーや利用規約のURLを設定

## トラブルシューティング

### アプリが「SUSPENDED」になっている場合

1. アプリの状態を確認
2. 停止理由を確認（Developer Portalに表示される場合があります）
3. 必要に応じて新しいアプリを作成

### 「Pending approval」状態の場合

1. 承認を待つ
2. または、アプリの説明を更新して再申請

### それでも解決しない場合

1. GitHub Actionsのログで詳細なエラーメッセージを確認
2. `test_detailed_error.py` を実行して詳細なエラー情報を取得
3. Twitter Developer Portalのサポートに問い合わせ




