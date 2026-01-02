# 365botGaryブログPDF生成ツール

365botGaryのブログ（http://notesofacim.blog.fc2.com/）の全投稿を1つのPDFにまとめるツールです。

## セットアップ

1. 依存パッケージをインストール:
```powershell
cd c:\Users\kazz17\.cursor\blog-to-pdf
python -m pip install -r requirements.txt
```

## 使用方法

```powershell
python generate_365bot_pdf.py
```

## 出力

- ファイル名: `神の使者365日の言葉.pdf`
- 場所: スクリプトと同じディレクトリ

## 機能

- 4つのインデックスページから全投稿のURLを抽出
- 各投稿のコンテンツを取得
- 1つのPDFにまとめる
- 日本語フォント対応（MS ゴシック、MS 明朝、メイリオ）

## 注意事項

- 全投稿を取得するため、実行に時間がかかります（365件 × 1秒 = 約6分以上）
- サーバーへの負荷を軽減するため、各リクエストの間に1秒の待機時間を設けています

