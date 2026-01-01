# アプリの権限設定を見つける方法

## 手順（詳細版）

### ステップ1: Twitter Developer Portalにアクセス

1. https://developer.twitter.com/ にアクセス
2. Xアカウントでログイン

### ステップ2: アプリを開く

#### 365botGaryアカウント用

1. 左サイドバーの「**Projects & Apps**」をクリック
2. 「**Free**」セクションを探す
3. 「**Default project-2006671045663797250**」をクリック（またはプロジェクト名をクリック）
4. 「**2006671045663797250365botGary**」アプリをクリック

#### pursahsgospelアカウント用

1. 左サイドバーの「**Projects & Apps**」をクリック
2. pursahsgospel用のプロジェクトまたはアプリを探す
3. アプリをクリック

### ステップ3: Settingsタブを開く

アプリを開いたら、上部にタブが表示されます：

- **Overview**（概要）
- **Keys and tokens**（認証情報）
- **Settings**（設定）← これをクリック

### ステップ4: App permissionsを探す

「Settings」タブを開くと、以下のようなセクションが表示されます：

#### 見つけ方1: 左サイドバーから

Settingsタブ内の左サイドバーに以下が表示される場合があります：
- **App info**（アプリ情報）
- **App permissions**（アプリ権限）← これをクリック

#### 見つけ方2: メインコンテンツエリアから

Settingsタブのメインコンテンツエリアに以下が表示される場合があります：

1. **App info** セクション
   - App name（アプリ名）
   - App description（アプリの説明）
   - など

2. **App permissions** セクション ← これを探す
   - 「**App permissions**」という見出し
   - ラジオボタンまたはドロップダウンメニューで権限を選択
   - 選択肢：
     - **Read**（読み取り専用）
     - **Read and Write**（読み取りと書き込み）← これを選択
     - **Read and write and Direct message**（読み取り、書き込み、DM）

#### 見つけ方3: 別の場所にある場合

もし「App permissions」が見つからない場合：

1. **User authentication settings** セクションを探す
2. **OAuth 1.0a** セクションを探す
3. **Permissions** という項目を探す

### ステップ5: 権限を変更

1. 「**Read and Write**」または「**Read and write and Direct message**」を選択
2. 「**Save**」または「**Update**」ボタンをクリック
3. 確認ダイアログが表示されたら「**Yes**」または「**Confirm**」をクリック

### ステップ6: Access Tokenを再生成

**重要**: 権限を変更した後、必ずAccess Tokenを再生成してください。

1. 「**Keys and tokens**」タブをクリック
2. 「**Access Token and Secret**」セクションを探す
3. 「**Regenerate**」ボタンをクリック
4. 新しいAccess TokenとAccess Token Secretをコピー
5. GitHub Secretsを更新

## 画面が見つからない場合

### 代替方法1: 検索機能を使用

1. Twitter Developer Portalの上部に検索ボックスがある場合、そこに「permissions」と入力
2. 関連する設定を探す

### 代替方法2: ヘルプを確認

1. Twitter Developer Portalの右上に「Help」または「？」アイコンがある場合、それをクリック
2. 「App permissions」で検索

### 代替方法3: 直接URLにアクセス

アプリのIDがわかっている場合、直接URLにアクセスできる場合があります：
- `https://developer.twitter.com/en/portal/projects/[PROJECT_ID]/apps/[APP_ID]/settings`

## よくある質問

### Q: Settingsタブが見つからない
A: アプリを開いた状態で、上部のタブを確認してください。「Settings」は「Keys and tokens」の隣にあります。

### Q: App permissionsセクションが見つからない
A: Settingsタブ内をスクロールして探してください。または、左サイドバーに「App permissions」がある場合があります。

### Q: 権限を変更できない
A: アプリの状態を確認してください。停止（SUSPENDED）されている場合は、アプリを有効化する必要があります。

## スクリーンショットの参考

もし可能であれば、現在の画面のスクリーンショットを共有していただければ、より具体的な案内ができます。

