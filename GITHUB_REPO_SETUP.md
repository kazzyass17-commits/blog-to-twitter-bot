# GitHubリポジトリ作成時のConfiguration設定

GitHubで新しいリポジトリを作成する際の「Configuration」セクションの設定方法です。

## 推奨設定

### 1. Choose visibility（可視性の選択）

**設定: Private または Public**

- **Private**: あなただけがアクセス可能（推奨、機密情報を含むため）
- **Public**: 誰でもアクセス可能

このプロジェクトにはTwitter API認証情報を含むため、**Private**を推奨します。

### 2. Add README（READMEの追加）

**設定: Off（オフ）**

✅ **重要**: 既にプロジェクトに`README.md`が含まれているため、**Off（オフ）**にしてください。

もしOnにすると、既存のREADME.mdと競合する可能性があります。

### 3. Add .gitignore（.gitignoreの追加）

**設定: "No .gitignore"（追加しない）**

✅ **重要**: 既にプロジェクトに`.gitignore`が含まれているため、**"No .gitignore"**を選択してください。

もし他のテンプレートを選択すると、既存の`.gitignore`と競合する可能性があります。

### 4. Add license（ライセンスの追加）

**設定: "No license"（追加しない）**

オプションです。必要に応じてライセンスを追加できますが、通常は**"No license"**で問題ありません。

## まとめ

| 項目 | 推奨設定 | 理由 |
|------|---------|------|
| Choose visibility | **Private** | 機密情報（Twitter API認証情報）を含むため |
| Add README | **Off** | 既にREADME.mdが存在するため |
| Add .gitignore | **No .gitignore** | 既に.gitignoreが存在するため |
| Add license | **No license** | オプション（必要に応じて追加可能） |

## 次のステップ

Configurationを上記のように設定したら：

1. 「Create repository」ボタンをクリック
2. リポジトリが作成されたら、以下のコマンドを実行してプッシュ：

```powershell
cd c:\Users\kazz17\.cursor\blog-to-twitter-bot
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git push -u origin main
```

3. Settings → Secrets and variables → Actions でTwitter API認証情報を設定

詳細は `GITHUB_CONFIGURATION.md` を参照してください。

