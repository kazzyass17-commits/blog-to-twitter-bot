# プロキシサーバーを使用してIPブロックを回避する方法

## 概要

GitHub ActionsのIPアドレスがブロックされている場合、プロキシサーバーを通すことで回避できる可能性があります。

## 実装方法

### 方法1: 環境変数でプロキシを設定

GitHub Actionsのワークフローでプロキシを設定します。

```yaml
- name: Test Twitter connection
  env:
    HTTP_PROXY: http://proxy.example.com:8080
    HTTPS_PROXY: http://proxy.example.com:8080
  run: |
    python test_twitter_connection.py --account both
```

### 方法2: requestsライブラリでプロキシを設定

`tweepy`は内部的に`requests`を使用しているため、環境変数でプロキシを設定できます。

### 方法3: カスタムHTTPアダプターを使用

より細かい制御が必要な場合、カスタムHTTPアダプターを作成します。

## 注意点とリスク

### ⚠️ 重要な注意事項

1. **X APIの利用規約に違反する可能性**
   - プロキシを使用してIPブロックを回避することは、利用規約に違反する可能性があります
   - 利用規約を確認してください

2. **セキュリティリスク**
   - プロキシサーバー経由で認証情報が流れる可能性
   - 信頼できるプロキシサーバーのみを使用してください

3. **コスト**
   - 有料プロキシサーバーを使用する場合、コストがかかります
   - 無料プロキシは信頼性が低い可能性があります

4. **パフォーマンス**
   - プロキシ経由でアクセスすると、レスポンスが遅くなる可能性があります

5. **レート制限**
   - プロキシサーバーのIPアドレスもレート制限の対象になります
   - 複数のユーザーが同じプロキシを使用している場合、制限に達しやすい

## 推奨される代替案

### 1. 時間を置いて再試行（推奨）

GitHub ActionsのIPアドレスは動的に変わります。しばらく待ってから再試行してください。

**メリット:**
- 追加の設定が不要
- コストがかからない
- 利用規約に違反しない

**デメリット:**
- 時間がかかる可能性がある

### 2. 別の時間帯に再試行

GitHub Actionsのワークフローを別の時間帯に実行してください。

### 3. X Developer Portalのサポートに問い合わせ

アプリの状態や403エラーの原因について問い合わせてください。

### 4. ローカル環境で実行（開発・テスト用）

開発やテストはローカル環境で実行し、本番環境のみGitHub Actionsを使用する。

## プロキシを使用する場合の実装例

### requestsライブラリでプロキシを設定

```python
import requests
import tweepy
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# プロキシ設定
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080',
}

# Tweepyクライアントを作成
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    wait_on_rate_limit=True
)

# プロキシを設定（tweepyの内部実装に依存）
# 注意: tweepyは直接プロキシ設定をサポートしていないため、
# 環境変数を使用する必要があります
```

### GitHub Secretsでプロキシ情報を管理

```yaml
env:
  HTTP_PROXY: ${{ secrets.HTTP_PROXY }}
  HTTPS_PROXY: ${{ secrets.HTTPS_PROXY }}
```

## 結論

### 推奨されるアプローチ

1. **まずは時間を置いて再試行**（最も安全で簡単）
2. **X Developer Portalのサポートに問い合わせ**
3. **それでも解決しない場合のみ、プロキシを検討**

### プロキシを使用する場合

- 利用規約を確認
- 信頼できるプロキシサーバーを使用
- セキュリティに注意
- コストを考慮

## 参考リンク

- X API利用規約: https://developer.twitter.com/en/developer-terms/agreement-and-policy
- GitHub Actions環境変数: https://docs.github.com/en/actions/learn-github-actions/variables




