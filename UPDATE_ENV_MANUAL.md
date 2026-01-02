# .envファイルを手動で更新する方法

## pursahsgospel用の認証情報を更新

`.env`ファイルをメモ帳などで開いて、以下の認証情報を更新してください：

### 更新する認証情報

```env
TWITTER_PURSAHS_API_KEY=PCotoQSfRLlBPoWgcBA7455y1
TWITTER_PURSAHS_API_SECRET=5H4mO4WXSAyadI7yQqlXrOR9DgCm1UOEpZqfPGWlzZTEgCG6Iv
TWITTER_PURSAHS_ACCESS_TOKEN=2416625168-HjSU1zutJdPiIkViltErroLVz81VusJBnGlP9BX
TWITTER_PURSAHS_ACCESS_TOKEN_SECRET=DyVPAj1Lj7Ebvi6kR2y1xqi1ES49B3XdzuOxLfDkNil7M
TWITTER_PURSAHS_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAP6u6gEAAAAANFP7mlTxPI1BeRpCpaJDtja2HB0%3DV443mkbthkCI5NC5ubm0l0AZYHL0YAIC9hJBDC5qoT9Q1pHHYL
```

## 手順

1. **.envファイルを開く**
   ```powershell
   notepad .env
   ```
   または、エクスプローラーで`.env`ファイルを右クリックして「プログラムから開く」→「メモ帳」

2. **認証情報を更新**
   - 上記の認証情報をコピー&ペースト
   - 既存の値と置き換える

3. **保存**
   - `Ctrl+S`で保存
   - メモ帳を閉じる

4. **接続テストを実行**
   ```powershell
   python test_twitter_connection.py --account pursahs
   ```

## 注意事項

- 前後の空白がないか確認
- 値が正しくコピーされているか確認
- 既存の他の認証情報（365botGary用など）は変更しない

## 401エラーが続く場合

1. **認証情報が正しくコピーされているか確認**
2. **Access Tokenを再生成**（権限変更後は必須）
3. **アプリの権限が「Read and write」に設定されているか確認**

