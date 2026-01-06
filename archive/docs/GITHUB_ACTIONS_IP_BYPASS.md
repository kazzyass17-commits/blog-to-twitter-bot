# GitHub ActionsからX APIへのアクセス回避策

## 問題の概要

GitHub ActionsからX APIにアクセスする際、Cloudflareのチャレンジページ（"Just a moment..."）が返され、403エラーが発生しています。これは、GitHub ActionsのIPアドレスがCloudflareによってブロックされているためです。

## 調査結果

### 1. GitHub ActionsのIPアドレス範囲

GitHub Actionsのホステッドランナーは動的なIPアドレスを使用しています。IPアドレス範囲は以下のAPIから取得できます：

```
GET https://api.github.com/meta
```

レスポンスには以下のIPアドレス範囲が含まれます：
- `actions` - GitHub ActionsのIPアドレス範囲
- `hooks` - GitHub WebhookのIPアドレス範囲

### 2. X API側でのIPホワイトリスト設定

**重要**: X（Twitter）APIの公式ドキュメントを確認したところ、**IPホワイトリスト機能は提供されていません**。

X APIは以下の認証方法のみをサポートしています：
- OAuth 1.0a
- OAuth 2.0
- Bearer Token

IPアドレスベースのアクセス制御は、X API側では設定できません。

### 3. Cloudflareチャレンジの回避方法

Cloudflareのチャレンジページが返される場合、以下の方法が考えられます：

#### 方法1: User-Agentヘッダーの設定（効果なし）

tweepyライブラリは内部的にrequestsライブラリを使用していますが、User-AgentをカスタマイズしてもCloudflareのチャレンジは回避できません。

#### 方法2: リクエスト間隔の調整（効果なし）

リクエスト間隔を調整しても、CloudflareのIPブロックは解除されません。

#### 方法3: セルフホストランナー（推奨）

セルフホストランナーを使用することで、固定IPアドレスから実行できます。これにより、Cloudflareのブロックを回避できる可能性があります。

**ただし、ユーザーはセルフホストランナーの設定を希望していません。**

## 結論

**X APIの公式マニュアルとGitHub Actionsのドキュメントを確認した結果、GitHub ActionsからX APIにアクセスする際のCloudflareブロックを回避する公式な方法は存在しません。**

### 利用可能な回避策

1. **セルフホストランナーを使用する**（設定が必要）
2. **別のCI/CDサービスを使用する**（GitLab CI、CircleCIなど）
3. **ローカルで実行する**（Windowsタスクスケジューラなど）
4. **プロキシサービスを使用する**（実装が複雑でコストがかかる可能性）

### 推奨事項

現時点では、以下のいずれかの方法を選択することをお勧めします：

1. **ローカル実行**: Windowsタスクスケジューラを使用してローカルで実行
2. **別のCI/CDサービス**: GitLab CIやCircleCIなど、IPがブロックされていないサービスを試す
3. **セルフホストランナー**: 将来的に設定を検討する

## 参考リンク

- [GitHub Actions IPアドレス範囲](https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/about-githubs-ip-addresses)
- [X API公式ドキュメント](https://developer.twitter.com/en/docs)
- [GitHub Actions セルフホストランナー](https://docs.github.com/ja/actions/hosting-your-own-runners/about-self-hosted-runners)




